import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:apk_sideload/install_apk.dart';
import 'package:intl/intl.dart';
import '../services/sync_service.dart';
import '../database/db_helper.dart';
import '../models/employee.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _urlCtrl = TextEditingController();
  bool _isSyncing = false;
  bool _isCheckingUpdate = false;
  int _pendingCount = 0;

  static const String CURRENT_APP_VERSION = "v1.0.3";
  static const String GITHUB_REPO = "BEPAWSITIVE/AMS";
  static const String DIRECT_APK_DOWNLOAD_URL = "https://github.com/BEPAWSITIVE/AMS/releases/download/latest/app-release.apk";

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final url = await SyncService.instance.getGoogleSheetUrl();
    if (url != null) _urlCtrl.text = url;
    _refreshPendingCount();
  }

  Future<void> _refreshPendingCount() async {
    final unsynced = await DBHelper.instance.getUnsyncedAttendance();
    setState(() => _pendingCount = unsynced.length);
  }

  Future<void> _triggerSync() async {
    setState(() => _isSyncing = true);
    final result = await SyncService.instance.syncPendingAttendance();
    setState(() => _isSyncing = false);
    _refreshPendingCount();

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message'] ?? 'Sync finished'),
          backgroundColor: result['success'] == true ? Colors.green : Colors.red,
        ),
      );
    }
  }

  Future<void> _downloadAndInstallDirectly(String downloadUrl) async {
    // Show download progress dialog
    double progress = 0.0;
    int received = 0;
    int total = 0;
    StateSetter? dialogSetState;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) {
          dialogSetState = setModalState;
          final pct = (progress * 100).toInt();
          final receivedMb = (received / (1024 * 1024)).toStringAsFixed(1);
          final totalMb = total > 0 ? (total / (1024 * 1024)).toStringAsFixed(1) : "30";

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
      ),
    );

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

  Future<void> _checkForAppUpdates() async {
    setState(() => _isCheckingUpdate = true);

    try {
      final isConnected = await SyncService.instance.isConnected();
      if (!isConnected) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text("You are currently offline. Connect to Wi-Fi or Mobile Data to check for updates."),
              backgroundColor: Colors.amber,
            ),
          );
        }
        return;
      }

      // Check GitHub Releases API for the latest published release
      final apiUrl = Uri.parse("https://api.github.com/repos/$GITHUB_REPO/releases/tags/latest");
      final response = await http.get(apiUrl, headers: {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Attendance-Manager-App'
      }).timeout(const Duration(seconds: 10));

      String downloadUrl = DIRECT_APK_DOWNLOAD_URL;
      String releaseDateStr = "Latest Release";

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        final assets = data['assets'] as List<dynamic>?;
        if (assets != null && assets.isNotEmpty) {
          final apkAsset = assets.firstWhere(
            (a) => a['name'].toString().endsWith('.apk'),
            orElse: () => null,
          );
          if (apkAsset != null) {
            if (apkAsset['browser_download_url'] != null) {
              downloadUrl = apkAsset['browser_download_url'];
            }
            if (apkAsset['updated_at'] != null) {
              final dt = DateTime.parse(apkAsset['updated_at']).toLocal();
              releaseDateStr = DateFormat('dd MMM yyyy, hh:mm a').format(dt);
            } else if (data['published_at'] != null) {
              final dt = DateTime.parse(data['published_at']).toLocal();
              releaseDateStr = DateFormat('dd MMM yyyy, hh:mm a').format(dt);
            }
          }
        }
      }

      if (!mounted) return;

      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: const Color(0xFFFFFFFF),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Row(
            children: [
              Icon(Icons.system_update, color: Colors.blueAccent),
              SizedBox(width: 10),
              Text("App Update Ready", style: TextStyle(color: Colors.black87, fontSize: 18, fontWeight: FontWeight.bold)),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "A new version of Attendance Manager is ready on GitHub.",
                style: TextStyle(color: Colors.black54, fontSize: 13),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text("Current Version:", style: TextStyle(color: Colors.black54, fontSize: 12)),
                        Text(CURRENT_APP_VERSION, style: const TextStyle(color: Colors.orange.shade800, fontWeight: FontWeight.bold, fontSize: 12)),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text("Updated on GitHub:", style: TextStyle(color: Colors.black54, fontSize: 12)),
                        Text(releaseDateStr, style: const TextStyle(color: Colors.green.shade700, fontWeight: FontWeight.bold, fontSize: 12)),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              const Text(
                "Tap below to download directly and trigger the Android update dialog.",
                style: TextStyle(color: Colors.black54, fontSize: 12),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text("Later", style: TextStyle(color: Colors.black54)),
            ),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              ),
              icon: const Icon(Icons.download, size: 18),
              label: const Text("Update Directly Now", style: TextStyle(fontWeight: FontWeight.bold)),
              onPressed: () {
                Navigator.pop(ctx);
                _downloadAndInstallDirectly(downloadUrl);
              },
            ),
          ],
        ),
      );

    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Could not connect to update server: $e"),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isCheckingUpdate = false);
    }
  }

  Future<void> _loadSampleStaff() async {
    final samples = [
      Employee(empId: "EMP101", name: "Rahul Sharma", department: "Operations", phone: "+91 98765 43210", createdAt: DateTime.now().toIso8601String()),
      Employee(empId: "EMP102", name: "Priya Patel", department: "HR & Admin", phone: "+91 98765 43211", createdAt: DateTime.now().toIso8601String()),
      Employee(empId: "EMP103", name: "Amit Verma", department: "Security", phone: "+91 98765 43212", createdAt: DateTime.now().toIso8601String()),
      Employee(empId: "EMP104", name: "Sneha Reddy", department: "IT Support", phone: "+91 98765 43213", createdAt: DateTime.now().toIso8601String()),
    ];

    for (var emp in samples) {
      await DBHelper.instance.insertEmployee(emp);
    }

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Sample employees added! View them in Employees tab."), backgroundColor: Colors.blue),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFFFFFF),
        title: const Text("Settings & Sync", style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // IN-APP AUTO-UPDATE CARD
          Card(
            color: const Color(0xFFFFFFFF),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.system_update_alt, color: Colors.blueAccent),
                          SizedBox(width: 8),
                          Text("App Version & Updates", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.black87)),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: Colors.blue.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: const Text(
                          CURRENT_APP_VERSION,
                          style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    "Connected to GitHub repo (BEPAWSITIVE/AMS). Tap below to check, download, and install the latest APK directly without opening a browser.",
                    style: TextStyle(color: Colors.black54, fontSize: 13),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 13),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: _isCheckingUpdate ? null : _checkForAppUpdates,
                      icon: _isCheckingUpdate
                          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.refresh, size: 20),
                      label: Text(
                        _isCheckingUpdate ? "Checking GitHub for updates..." : "Check & Install Latest Update",
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 14),

          // GOOGLE SHEET WEBHOOK
          Card(
            color: const Color(0xFFFFFFFF),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("Google Sheet Webhook", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.black87)),
                  const SizedBox(height: 6),
                  const Text(
                    "Paste the Google Apps Script Web App URL to push attendance records automatically.",
                    style: TextStyle(color: Colors.black54, fontSize: 13),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _urlCtrl,
                    style: const TextStyle(color: Colors.black87, fontSize: 13),
                    decoration: InputDecoration(
                      hintText: "https://script.google.com/macros/s/.../exec",
                      hintStyle: const TextStyle(color: Colors.black38),
                      filled: true,
                      fillColor: const Color(0xFFF8FAFC),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
                    onPressed: () async {
                      await SyncService.instance.saveGoogleSheetUrl(_urlCtrl.text);
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text("URL saved!"), backgroundColor: Colors.green),
                        );
                      }
                    },
                    icon: const Icon(Icons.save, color: Colors.white),
                    label: const Text("Save URL", style: TextStyle(color: Colors.white)),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 14),

          // OFFLINE SYNC QUEUE
          Card(
            color: const Color(0xFFFFFFFF),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("Offline Sync Queue", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.black87)),
                  const SizedBox(height: 6),
                  Text(
                    "Unsynced records pending upload: $_pendingCount",
                    style: TextStyle(color: _pendingCount > 0 ? Colors.orange.shade800 : Colors.green.shade700, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green.shade700,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      onPressed: _isSyncing ? null : _triggerSync,
                      icon: _isSyncing
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.cloud_upload, color: Colors.white),
                      label: Text(
                        _isSyncing ? "Syncing to Google Sheets..." : "Sync Pending Records Now",
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 14),

          // DEMO DATA
          Card(
            color: const Color(0xFFFFFFFF),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: ListTile(
              leading: const Icon(Icons.people_outline, color: Colors.blueAccent),
              title: const Text("Load Sample Employees", style: TextStyle(color: Colors.black87, fontWeight: FontWeight.w600)),
              subtitle: const Text("Pre-load sample staff for immediate testing", style: TextStyle(color: Colors.black54, fontSize: 12)),
              onTap: _loadSampleStaff,
            ),
          ),
        ],
      ),
    );
  }
}
