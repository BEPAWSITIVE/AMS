import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:apk_sideload/install_apk.dart';

Future<void> downloadAndInstallDirectly(BuildContext context, String downloadUrl) async {
  bool mounted = true;
  StateSetter? dialogSetState;
  double progress = 0.0;
  int received = 0;
  int total = 0;

  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (ctx) {
      return StatefulBuilder(
        builder: (context, setState) {
          dialogSetState = setState;
          final pct = total > 0 ? ((progress) * 100).toStringAsFixed(1) : "0.0";
          final receivedMb = (received / 1024 / 1024).toStringAsFixed(2);
          final totalMb = (total / 1024 / 1024).toStringAsFixed(2);

          return AlertDialog(
            backgroundColor: const Color(0xFFFFFFFF),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            title: const Row(
              children: [
                Icon(Icons.downloading, color: Colors.blueAccent),
                SizedBox(width: 10),
                Text("Downloading Update...", style: TextStyle(color: Colors.black87, fontSize: 17, fontWeight: FontWeight.bold)),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Fetching the latest APK directly from GitHub. Android will prompt you to install automatically.",
                  style: TextStyle(color: Colors.black54, fontSize: 13),
                ),
                const SizedBox(height: 18),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: total > 0 ? progress : null,
                    minHeight: 10,
                    backgroundColor: const Color(0xFFF8FAFC),
                    valueColor: const AlwaysStoppedAnimation<Color>(Colors.blueAccent),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text("$pct% complete", style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                    Text("$receivedMb MB / $totalMb MB", style: const TextStyle(color: Colors.black54, fontSize: 12)),
                  ],
                ),
              ],
            ),
          );
        },
      );
    },
  ).then((_) => mounted = false);

  try {
    final client = http.Client();
    final request = http.Request('GET', Uri.parse(downloadUrl));
    final response = await client.send(request);

    total = response.contentLength ?? 0;
    final tempDir = await getTemporaryDirectory();
    final apkFile = File('${tempDir.path}/attendance_update.apk');
    if (await apkFile.exists()) {
      await apkFile.delete();
    }

    final sink = apkFile.openWrite();

    await response.stream.listen((chunk) {
      sink.add(chunk);
      received += chunk.length;
      if (total > 0 && dialogSetState != null) {
        dialogSetState!(() {
          progress = received / total;
        });
      }
    }).asFuture();

    await sink.close();

    // Close progress dialog
    if (mounted) Navigator.pop(context);

    // Trigger native Android package installer
    await InstallApk().installApk(apkFile.path);

  } catch (e) {
    if (mounted) {
      Navigator.pop(context); // Close dialog if open
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Download error: $e"),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
