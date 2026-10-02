import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../models/employee.dart';
import '../database/db_helper.dart';

class EmployeeScreen extends StatefulWidget {
  const EmployeeScreen({super.key});

  @override
  State<EmployeeScreen> createState() => _EmployeeScreenState();
}

class _EmployeeScreenState extends State<EmployeeScreen> {
  List<Employee> _employees = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadEmployees();
  }

  Future<void> _loadEmployees() async {
    final list = await DBHelper.instance.getAllEmployees();
    setState(() {
      _employees = list;
      _isLoading = false;
    });
  }

  void _showAddEmployeeDialog() {
    final nameCtrl = TextEditingController();
    final idCtrl = TextEditingController(text: "EMP${100 + _employees.length + 1}");
    final deptCtrl = TextEditingController();
    final phoneCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("Register Employee", style: TextStyle(color: Colors.white)),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameCtrl,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(labelText: "Full Name *", labelStyle: TextStyle(color: Colors.white70)),
              ),
              TextField(
                controller: idCtrl,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(labelText: "Employee ID *", labelStyle: TextStyle(color: Colors.white70)),
              ),
              TextField(
                controller: deptCtrl,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(labelText: "Department / Role", labelStyle: TextStyle(color: Colors.white70)),
              ),
              TextField(
                controller: phoneCtrl,
                keyboardType: TextInputType.phone,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(labelText: "Phone Number", labelStyle: TextStyle(color: Colors.white70)),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("Cancel", style: TextStyle(color: Colors.white60)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
            onPressed: () async {
              if (nameCtrl.text.trim().isEmpty || idCtrl.text.trim().isEmpty) return;

              final emp = Employee(
                empId: idCtrl.text.trim().toUpperCase(),
                name: nameCtrl.text.trim(),
                department: deptCtrl.text.trim().isNotEmpty ? deptCtrl.text.trim() : "General",
                phone: phoneCtrl.text.trim(),
                createdAt: DateTime.now().toIso8601String(),
              );

              await DBHelper.instance.insertEmployee(emp);
              Navigator.pop(ctx);
              _loadEmployees();
              _showQrDialog(emp);
            },
            child: const Text("Save & Generate QR", style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _showQrDialog(Employee emp) {
    final qrPayload = jsonEncode({
      'type': 'ATTENDANCE_EMP',
      'empId': emp.empId,
      'name': emp.name,
      'department': emp.department,
    });

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.white,
        contentPadding: const EdgeInsets.all(20),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              "ATTENDANCE PASS",
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.blueAccent, letterSpacing: 1.2),
            ),
            const SizedBox(height: 6),
            Text(
              emp.name,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black87),
            ),
            Text(
              "${emp.empId} • ${emp.department}",
              style: const TextStyle(fontSize: 13, color: Colors.black54),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade300),
                borderRadius: BorderRadius.circular(12),
              ),
              child: QrImageView(
                data: qrPayload,
                version: QrVersions.auto,
                size: 200.0,
                backgroundColor: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              "Show this QR code at office entry/exit",
              style: TextStyle(fontSize: 11, color: Colors.black45),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("Close"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("Employees Directory", style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: Colors.blueAccent,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text("Add Employee", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        onPressed: _showAddEmployeeDialog,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _employees.isEmpty
              ? const Center(
                  child: Text("No employees registered yet.\nTap '+ Add Employee' to create one.",
                      textAlign: TextAlign.center, style: TextStyle(color: Colors.white60)),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(14),
                  itemCount: _employees.length,
                  itemBuilder: (ctx, i) {
                    final emp = _employees[i];
                    return Card(
                      color: const Color(0xFF1E293B),
                      margin: const EdgeInsets.only(bottom: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Colors.blue.shade900,
                          child: Text(
                            emp.name.isNotEmpty ? emp.name[0].toUpperCase() : 'E',
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                          ),
                        ),
                        title: Text(emp.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                        subtitle: Text("${emp.empId} • ${emp.department}", style: const TextStyle(color: Colors.white60, fontSize: 12)),
                        trailing: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blueAccent.withOpacity(0.2),
                            foregroundColor: Colors.blueAccent,
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          ),
                          icon: const Icon(Icons.qr_code, size: 16),
                          label: const Text("QR", style: TextStyle(fontSize: 12)),
                          onPressed: () => _showQrDialog(emp),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
