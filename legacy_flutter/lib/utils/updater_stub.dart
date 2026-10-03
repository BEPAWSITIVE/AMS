import 'package:flutter/material.dart';

Future<void> downloadAndInstallDirectly(BuildContext context, String downloadUrl) async {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text("App updates are not supported on the Web platform."),
      backgroundColor: Colors.amber,
    ),
  );
}
