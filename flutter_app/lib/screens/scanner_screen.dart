import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:permission_handler/permission_handler.dart';
import '../models/employee.dart';
import '../models/attendance_record.dart';
import '../database/db_helper.dart';
import '../services/sync_service.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> with WidgetsBindingObserver {
  late final MobileScannerController _cameraController = MobileScannerController(
    detectionSpeed: DetectionSpeed.normal,
    facing: CameraFacing.back,
    torchEnabled: false,
    autoStart: false,
  );

  bool _isProcessing = false;
  bool _hasCameraPermission = false;
  bool _isCheckingPermission = true;
  String _lastScanned = "";
  DateTime _lastScanTime = DateTime.now().subtract(const Duration(seconds: 10));

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _checkAndRequestCameraPermission();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _cameraController.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (!_hasCameraPermission) return;
    if (state == AppLifecycleState.inactive || state == AppLifecycleState.paused) {
      _cameraController.stop();
    } else if (state == AppLifecycleState.resumed) {
      _cameraController.start();
    }
  }

  Future<void> _checkAndRequestCameraPermission() async {
    setState(() => _isCheckingPermission = true);
    var status = await Permission.camera.status;

    if (!status.isGranted) {
      status = await Permission.camera.request();
    }

    if (mounted) {
      setState(() {
        _hasCameraPermission = status.isGranted;
        _isCheckingPermission = false;
      });
    }

    if (status.isGranted) {
      // Delay slightly so the Android SurfaceView is fully rendered and attached
      await Future.delayed(const Duration(milliseconds: 250));
      if (!mounted) return;
      try {
        await _cameraController.start();
      } catch (e) {
        debugPrint("Camera start error: $e");
      }
    }
  }

  Future<void> _retryCamera() async {
    try {
      await _cameraController.stop();
    } catch (_) {}
    await Future.delayed(const Duration(milliseconds: 300));
    if (!mounted) return;
    try {
      await _cameraController.start();
      setState(() {});
    } catch (e) {
      debugPrint("Camera retry error: $e");
    }
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

  void _promptManualTestScan() async {
    final employees = await DBHelper.instance.getAllEmployees();
    if (!mounted) return;

    if (employees.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("No employees found. Go to 'Settings' and tap 'Load Sample Employees' first.")),
      );
      return;
    }

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("Test Scan Employee", style: TextStyle(color: Colors.white)),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: employees.length,
            itemBuilder: (c, i) {
              final emp = employees[i];
              return ListTile(
                title: Text(emp.name, style: const TextStyle(color: Colors.white)),
                subtitle: Text("${emp.empId} • ${emp.department}", style: const TextStyle(color: Colors.white60)),
                trailing: const Icon(Icons.touch_app, color: Colors.blueAccent),
                onTap: () {
                  Navigator.pop(ctx);
                  _processBarcode(emp.empId);
                },
              );
            },
          ),
        ),
      ),
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
          if (_hasCameraPermission) ...[
            IconButton(
              icon: const Icon(Icons.flash_on),
              onPressed: () => _cameraController.toggleTorch(),
            ),
            IconButton(
              icon: const Icon(Icons.flip_camera_android),
              onPressed: () => _cameraController.switchCamera(),
            ),
          ],
          IconButton(
            icon: const Icon(Icons.dialpad, color: Colors.blueAccent),
            tooltip: "Test Scan without camera",
            onPressed: _promptManualTestScan,
          ),
        ],
      ),
      body: _isCheckingPermission
          ? const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(color: Colors.blueAccent),
                  SizedBox(height: 16),
                  Text("Checking permissions...", style: TextStyle(color: Colors.white70)),
                ],
              ),
            )
          : !_hasCameraPermission
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 28),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            color: Colors.amber.withOpacity(0.15),
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.amber, width: 2),
                          ),
                          child: const Icon(Icons.camera_alt, color: Colors.amber, size: 40),
                        ),
                        const SizedBox(height: 20),
                        const Text(
                          "Camera Permission Required",
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          "Attendance Manager needs camera permission to scan employee QR passes at office gates.",
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.white60, fontSize: 13, height: 1.4),
                        ),
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.blueAccent,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                            icon: const Icon(Icons.lock_open),
                            label: const Text("Grant Camera Permission", style: TextStyle(fontWeight: FontWeight.bold)),
                            onPressed: _checkAndRequestCameraPermission,
                          ),
                        ),
                        const SizedBox(height: 10),
                        TextButton(
                          onPressed: () => openAppSettings(),
                          child: const Text("Open Phone App Settings", style: TextStyle(color: Colors.white54)),
                        ),
                      ],
                    ),
                  ),
                )
              : Stack(
                  children: [
                    MobileScanner(
                      controller: _cameraController,
                      onDetect: _onDetect,
                      errorBuilder: (context, error, child) {
                        return Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.videocam_off, color: Colors.redAccent, size: 52),
                                const SizedBox(height: 14),
                                Text(
                                  "Camera Error: ${error.errorCode.name}",
                                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  error.errorDetails?.message ?? "Could not connect to camera hardware. Tap to restart:",
                                  textAlign: TextAlign.center,
                                  style: const TextStyle(color: Colors.white60, fontSize: 12),
                                ),
                                const SizedBox(height: 16),
                                ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
                                  icon: const Icon(Icons.refresh, color: Colors.white),
                                  label: const Text("Restart Camera", style: TextStyle(color: Colors.white)),
                                  onPressed: _retryCamera,
                                ),
                                const SizedBox(height: 8),
                                TextButton(
                                  onPressed: () => openAppSettings(),
                                  child: const Text("Open Phone App Settings", style: TextStyle(color: Colors.white54, fontSize: 12)),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
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
