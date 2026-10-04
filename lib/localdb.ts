import Dexie, { Table } from 'dexie';
import { AttendanceRecord, Employee } from './supabase';

export class OfflineDatabase extends Dexie {
  syncQueue!: Table<AttendanceRecord, string>;
  employeeQueue!: Table<Employee, string>;

  constructor() {
    super('AttendanceOfflineDB');
    this.version(1).stores({
      syncQueue: 'recordId, empId, date'
    });
    this.version(2).stores({
      syncQueue: 'recordId, empId, date',
      employeeQueue: 'empId'
    });
  }
}

export const localdb = new OfflineDatabase();
