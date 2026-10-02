import 'package:flutter/material.dart';
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
  int _pendingCount = 0;

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
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("Settings & Sync", style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            color: const Color(0xFF1E293B),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("Google Sheet Webhook", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                  const SizedBox(height: 6),
                  const Text(
                    "Paste the Google Apps Script Web App URL to push attendance records automatically.",
                    style: TextStyle(color: Colors.white60, fontSize: 13),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _urlCtrl,
                    style: const TextStyle(color: Colors.white, fontSize: 13),
                    decoration: InputDecoration(
                      hintText: "https://script.google.com/macros/s/.../exec",
                      hintStyle: const TextStyle(color: Colors.white30),
                      filled: true,
                      fillColor: const Color(0xFF0F172A),
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
          Card(
            color: const Color(0xFF1E293B),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("Offline Sync Queue", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                  const SizedBox(height: 6),
                  Text(
                    "Unsynced records pending upload: $_pendingCount",
                    style: TextStyle(color: _pendingCount > 0 ? Colors.amberAccent : Colors.greenAccent, fontWeight: FontWeight.w600),
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
          Card(
            color: const Color(0xFF1E293B),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: ListTile(
              leading: const Icon(Icons.people_outline, color: Colors.blueAccent),
              title: const Text("Load Sample Employees", style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
              subtitle: const Text("Pre-load sample staff for immediate testing", style: TextStyle(color: Colors.white60, fontSize: 12)),
              onTap: _loadSampleStaff,
            ),
          ),
        ],
      ),
    );
  }
}
