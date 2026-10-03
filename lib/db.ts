import Dexie, { Table } from 'dexie';

export interface Employee {
  empId: string;
  name: string;
  department: string;
  phone?: string;
  createdAt: string;
}

export interface AttendanceRecord {
  recordId: string;
  empId: string;
  empName: string;
  department: string;
  date: string;
  inTime: string;
  inTimestamp: number;
  outTime?: string;
  outTimestamp?: number;
  totalHours?: string;
  status: string; // 'IN' or 'OUT'
  isSynced: number; // 0 = false, 1 = true
  updatedAt: string;
}

export class AttendanceDatabase extends Dexie {
  employees!: Table<Employee, string>;
  attendance!: Table<AttendanceRecord, string>;

  constructor() {
    super('AttendanceManagerDB');
    this.version(1).stores({
      employees: 'empId, name',
      attendance: 'recordId, empId, date, isSynced, inTimestamp'
    });
  }
}

export const db = new AttendanceDatabase();
