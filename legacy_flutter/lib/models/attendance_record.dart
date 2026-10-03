class AttendanceRecord {
  final String recordId; // e.g. 2026-10-02_EMP101
  final String empId;
  final String empName;
  final String department;
  final String date; // YYYY-MM-DD
  final String inTime;
  final int inTimestamp;
  String? outTime;
  int? outTimestamp;
  String? totalHours;
  String status; // Checked In, Completed
  int isSynced; // 0 = Pending local, 1 = Synced to Google Sheet
  String updatedAt;

  AttendanceRecord({
    required this.recordId,
    required this.empId,
    required this.empName,
    required this.department,
    required this.date,
    required this.inTime,
    required this.inTimestamp,
    this.outTime,
    this.outTimestamp,
    this.totalHours,
    required this.status,
    required this.isSynced,
    required this.updatedAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'recordId': recordId,
      'empId': empId,
      'empName': empName,
      'department': department,
      'date': date,
      'inTime': inTime,
      'inTimestamp': inTimestamp,
      'outTime': outTime,
      'outTimestamp': outTimestamp,
      'totalHours': totalHours,
      'status': status,
      'isSynced': isSynced,
      'updatedAt': updatedAt,
    };
  }

  factory AttendanceRecord.fromMap(Map<String, dynamic> map) {
    return AttendanceRecord(
      recordId: map['recordId'] ?? '',
      empId: map['empId'] ?? '',
      empName: map['empName'] ?? '',
      department: map['department'] ?? '',
      date: map['date'] ?? '',
      inTime: map['inTime'] ?? '',
      inTimestamp: map['inTimestamp'] ?? 0,
      outTime: map['outTime'],
      outTimestamp: map['outTimestamp'],
      totalHours: map['totalHours'],
      status: map['status'] ?? 'Checked In',
      isSynced: map['isSynced'] ?? 0,
      updatedAt: map['updatedAt'] ?? '',
    );
  }
}
