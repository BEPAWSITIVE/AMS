import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../models/employee.dart';
import '../models/attendance_record.dart';
import '../database/db_helper.dart';
import '../services/sync_service.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final MobileScannerController _cameraController = MobileScannerController(
    detectionSpeed: DetectionSpeed.normal,
    facing: CameraFacing.back,
    torchEnabled: false,
  );

  bool _isProcessing = false;
  String _lastScanned = "";
  DateTime _lastScanTime = DateTime.now().subtract(const Duration(seconds: 10));

  @override
  void dispose() {
    _cameraController.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_isProcessing) return;

    final List<Barcode> barcodes = capture.barcodes;
    if (barcodes.isEmpty) return;

    final String? code = barcodes.first.rawValue;
    if (code == null || code.trim().isEmpty) return;

    final now = DateTime.now();
    if (code == _lastScanned && now.difference(_lastScanTime).inSeconds < 3) {
      return; // prevent rapid repeat triggers
    }

    _lastScanned = code;
    _lastScanTime = now;
    _processBarcode(code);
  }

  Future<void> _processBarcode(String rawCode) async {
    setState(() => _isProcessing = true);
    HapticFeedback.mediumImpact();

    try {
      String empId = rawCode.trim();
      String empName = "";
      String empDept = "";

      // Try decoding JSON payload
      if (rawCode.startsWith('{') && rawCode.endsWith('}')) {
        try {
          final data = jsonDecode(rawCode);
          empId = data['empId'] ?? data['id'] ?? empId;
          empName = data['name'] ?? '';
          empDept = data['department'] ?? '';
        } catch (_) {}
      } else if (rawCode.startsWith('EMP:')) {
        empId = rawCode.replaceFirst('EMP:', '').trim();
      }

      // 1. Fetch or create employee
      Employee? emp = await DBHelper.instance.getEmployee(empId);
      if (emp == null) {
        emp = Employee(
          empId: empId,
          name: empName.isNotEmpty ? empName : "Employee $empId",
          department: empDept.isNotEmpty ? empDept : "General",
          phone: "",
          createdAt: DateTime.now().toIso8601String(),
        );
        await DBHelper.instance.insertEmployee(emp);
      }

      final now = DateTime.now();
      final String todayStr = DateFormat('yyyy-MM-dd').format(now);
      final String timeStr = DateFormat('hh:mm:ss a').format(now);
      final String recordId = "${todayStr}_$empId";

      AttendanceRecord? record = await DBHelper.instance.getAttendanceRecord(recordId);

      if (record == null) {
        // CHECK-IN
        record = AttendanceRecord(
          recordId: recordId,
          empId: emp.empId,
          empName: emp.name,
          department: emp.department,
          date: todayStr,
          inTime: timeStr,
          inTimestamp: now.millisecondsSinceEpoch,
          status: "Checked In",
          isSynced: 0,
          updatedAt: now.toIso8601String(),
        );
        await DBHelper.instance.saveAttendance(record);
        HapticFeedback.heavyImpact();
        if (mounted) {
          _showFeedbackModal(
            title: "CHECK-IN RECORDED",
            subtitle: "Arrival Time: $timeStr",
            color: Colors.green,
            icon: Icons.login,
            employee: emp,
          );
        }
      } else if (record.outTime == null || record.outTime!.isEmpty) {
        // CHECK-OUT
        final inTimeDt = DateTime.fromMillisecondsSinceEpoch(record.inTimestamp);
        final diff = now.difference(inTimeDt);
        final hours = diff.inHours;
        final mins = diff.inMinutes.remainder(60);
        final totalHoursStr = "${hours}h ${mins}m";

        record.outTime = timeStr;
        record.outTimestamp = now.millisecondsSinceEpoch;
        record.totalHours = totalHoursStr;
        record.status = "Completed";
        record.isSynced = 0;
        record.updatedAt = now.toIso8601String();

        await DBHelper.instance.saveAttendance(record);
        HapticFeedback.heavyImpact();
        if (mounted) {
          _showFeedbackModal(
            title: "CHECK-OUT RECORDED",
            subtitle: "Leaving Time: $timeStr • Total: $totalHoursStr",
            color: Colors.blue,
            icon: Icons.logout,
            employee: emp,
          );
        }
      } else {
        // ALREADY COMPLETED TODAY
        if (mounted) {
          _showFeedbackModal(
            title: "ALREADY LOGGED TODAY",
            subtitle: "In: ${record.inTime} | Out: ${record.outTime} (${record.totalHours})",
            color: Colors.amber.shade800,
            icon: Icons.check_circle_outline,
            employee: emp,
          );
        }
      }

      // Auto background sync if internet is connected
      SyncService.instance.syncPendingAttendance();

    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error: $e"), backgroundColor: Colors.red),
        );
      }
    } finally {
      Future.delayed(const Duration(milliseconds: 1500), () {
        if (mounted) setState(() => _isProcessing = false);
      });
    }
  }

  void _showFeedbackModal({
    required String title,
    required String subtitle,
    required Color color,
    required IconData icon,
    required Employee employee,
  }) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  shape: BoxShape.circle,
                  border: Border.all(color: color, width: 2),
                ),
                child: Icon(icon, color: color, size: 36),
              ),
              const SizedBox(height: 14),
              Text(
                title,
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color),
              ),
              const SizedBox(height: 6),
              Text(
                employee.name,
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: Colors.white),
              ),
              Text(
                "${employee.empId} • ${employee.department}",
                style: const TextStyle(fontSize: 14, color: Colors.white70),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.black26,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  subtitle,
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white),
                ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF334155),
                    foregroundColor: Colors.white,
                  ),
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text("Done"),
                ),
              )
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("Guard QR Scanner", style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.flash_on),
            onPressed: () => _cameraController.toggleTorch(),
          ),
          IconButton(
            icon: const Icon(Icons.flip_camera_android),
            onPressed: () => _cameraController.switchCamera(),
          ),
        ],
      ),
      body: Stack(
        children: [
          MobileScanner(
            controller: _cameraController,
            onDetect: _onDetect,
          ),
          // Viewfinder box overlay
          Center(
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.blueAccent, width: 2.5),
                borderRadius: BorderRadius.circular(16),
              ),
            ),
          ),
          Positioned(
            bottom: 30,
            left: 20,
            right: 20,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.75),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.qr_code_scanner, color: Colors.blueAccent),
                  SizedBox(width: 10),
                  Text(
                    "Point camera at employee QR badge",
                    style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
