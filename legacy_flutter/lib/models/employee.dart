class Employee {
  final String empId;
  final String name;
  final String department;
  final String phone;
  final String createdAt;

  Employee({
    required this.empId,
    required this.name,
    required this.department,
    required this.phone,
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'empId': empId,
      'name': name,
      'department': department,
      'phone': phone,
      'createdAt': createdAt,
    };
  }

  factory Employee.fromMap(Map<String, dynamic> map) {
    return Employee(
      empId: map['empId'] ?? '',
      name: map['name'] ?? '',
      department: map['department'] ?? 'General',
      phone: map['phone'] ?? '',
      createdAt: map['createdAt'] ?? '',
    );
  }
}
