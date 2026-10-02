import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/employee.dart';
import '../models/attendance_record.dart';

class DBHelper {
  static final DBHelper instance = DBHelper._init();
  static Database? _database;

  DBHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('attendance_manager.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
  }

  Future _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE employees (
        empId TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        phone TEXT,
        createdAt TEXT NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE attendance (
        recordId TEXT PRIMARY KEY,
        empId TEXT NOT NULL,
        empName TEXT NOT NULL,
        department TEXT NOT NULL,
        date TEXT NOT NULL,
        inTime TEXT NOT NULL,
        inTimestamp INTEGER NOT NULL,
        outTime TEXT,
        outTimestamp INTEGER,
        totalHours TEXT,
        status TEXT NOT NULL,
        isSynced INTEGER NOT NULL,
        updatedAt TEXT NOT NULL
      )
    ''');
  }

  // Employee CRUD
  Future<int> insertEmployee(Employee emp) async {
    final db = await instance.database;
    return await db.insert('employees', emp.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<Employee?> getEmployee(String empId) async {
    final db = await instance.database;
    final maps = await db.query(
      'employees',
      where: 'empId = ?',
      whereArgs: [empId],
    );
    if (maps.isNotEmpty) {
      return Employee.fromMap(maps.first);
    }
    return null;
  }

  Future<List<Employee>> getAllEmployees() async {
    final db = await instance.database;
    final result = await db.query('employees', orderBy: 'name ASC');
    return result.map((json) => Employee.fromMap(json)).toList();
  }

  Future<int> deleteEmployee(String empId) async {
    final db = await instance.database;
    return await db.delete('employees', where: 'empId = ?', whereArgs: [empId]);
  }

  // Attendance CRUD
  Future<int> saveAttendance(AttendanceRecord record) async {
    final db = await instance.database;
    return await db.insert('attendance', record.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<AttendanceRecord?> getAttendanceRecord(String recordId) async {
    final db = await instance.database;
    final maps = await db.query(
      'attendance',
      where: 'recordId = ?',
      whereArgs: [recordId],
    );
    if (maps.isNotEmpty) {
      return AttendanceRecord.fromMap(maps.first);
    }
    return null;
  }

  Future<List<AttendanceRecord>> getAttendanceForDate(String dateStr) async {
    final db = await instance.database;
    final result = await db.query(
      'attendance',
      where: 'date = ?',
      whereArgs: [dateStr],
      orderBy: 'inTimestamp DESC',
    );
    return result.map((json) => AttendanceRecord.fromMap(json)).toList();
  }

  Future<List<AttendanceRecord>> getUnsyncedAttendance() async {
    final db = await instance.database;
    final result = await db.query(
      'attendance',
      where: 'isSynced = ?',
      whereArgs: [0],
    );
    return result.map((json) => AttendanceRecord.fromMap(json)).toList();
  }

  Future<int> markRecordsAsSynced(List<String> recordIds) async {
    final db = await instance.database;
    int count = 0;
    for (String id in recordIds) {
      count += await db.update(
        'attendance',
        {'isSynced': 1},
        where: 'recordId = ?',
        whereArgs: [id],
      );
    }
    return count;
  }

  Future<void> clearAll() async {
    final db = await instance.database;
    await db.delete('employees');
    await db.delete('attendance');
  }
}
