import Dexie, { Table } from 'dexie';

export class AppDB extends Dexie {
  syncQueue!: Table<any, string>; 
  employeeQueue!: Table<any, string>;
  parcelQueue!: Table<any, string>;

  constructor() {
    super('AttendanceDB');
    this.version(3).stores({
      syncQueue: 'recordId, empId, date',
      employeeQueue: 'empId',
      parcelQueue: 'id'
    });
  }
}

export const localdb = new AppDB();
