import os

settings = open('components/SettingsTab.tsx', 'r', encoding='utf-8').read()

if "employeeQueue.count" not in settings:
    old_check_queue = """    const checkQueue = async () => {
      const count = await localdb.syncQueue.count();
      setPendingSync(count);
    };"""
    
    new_check_queue = """    const checkQueue = async () => {
      const attCount = await localdb.syncQueue.count();
      const empCount = await localdb.employeeQueue.count();
      setPendingSync(attCount + empCount);
    };"""
    
    settings = settings.replace(old_check_queue, new_check_queue)
    
    old_handle_online = """    const handleOnline = async () => {
      checkOffline();
      const records = await localdb.syncQueue.toArray();
      if (records.length > 0) {
        // Simple sync: push all records
        for (const record of records) {
          const { error } = await supabase.from('attendance').upsert(record);
          if (!error) {
            await localdb.syncQueue.delete(record.recordId);
          }
        }
        checkQueue();
      }
    };"""
    
    new_handle_online = """    const handleOnline = async () => {
      checkOffline();
      
      // Sync Employees first
      const emps = await localdb.employeeQueue.toArray();
      if (emps.length > 0) {
        for (const emp of emps) {
          const { error } = await supabase.from('employees').upsert(emp);
          if (!error) await localdb.employeeQueue.delete(emp.empId);
        }
      }
      
      // Sync Attendance
      const records = await localdb.syncQueue.toArray();
      if (records.length > 0) {
        for (const record of records) {
          const { error } = await supabase.from('attendance').upsert(record);
          if (!error) {
            await localdb.syncQueue.delete(record.recordId);
          }
        }
      }
      
      checkQueue();
    };"""
    
    settings = settings.replace(old_handle_online, new_handle_online)
    with open('components/SettingsTab.tsx', 'w', encoding='utf-8') as f:
        f.write(settings)

print("Done")
