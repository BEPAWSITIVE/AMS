import Dexie, { Table } from 'dexie';
import { AttendanceRecord } from './supabase';

// We'll use Dexie just for queuing attendance records when offline
export class OfflineDatabase extends Dexie {
  syncQueue!: Table<AttendanceRecord, string>;

  constructor() {
    super('AttendanceOfflineDB');
    this.version(1).stores({
      syncQueue: 'recordId, empId, date'
    });
  }
}

export const localdb = new OfflineDatabase();
