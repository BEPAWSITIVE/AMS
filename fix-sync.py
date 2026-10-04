import os

settings = open('components/SettingsTab.tsx', 'r', encoding='utf-8').read()

old_handle_online = """    // Auto-sync when coming online
    const handleOnline = async () => {
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
    };
    window.addEventListener('online', handleOnline);

    return () => {
      window.removeEventListener('online', checkOffline);
      window.removeEventListener('offline', checkOffline);
      window.removeEventListener('online', handleOnline);
    }
  }, []);"""

new_handle_online = """    const handleOnline = async () => {
      checkOffline();
      
      // Sync Employees first
      const emps = await localdb.employeeQueue.toArray();
      if (emps.length > 0) {
        for (const emp of emps) {
          const { error } = await supabase.from('employees').upsert(emp);
          if (!error) {
            await localdb.employeeQueue.delete(emp.empId);
          } else {
            console.error("Sync emp error:", error);
          }
        }
      }
      
      // Sync Attendance
      const records = await localdb.syncQueue.toArray();
      if (records.length > 0) {
        for (const record of records) {
          const { error } = await supabase.from('attendance').upsert(record);
          if (!error) {
            await localdb.syncQueue.delete(record.recordId);
          } else {
            console.error("Sync attendance error:", error);
          }
        }
      }
      
      checkQueue();
    };
    
    // Auto-sync immediately if online on mount
    if (navigator.onLine) {
      handleOnline();
    }
    
    window.addEventListener('online', handleOnline);

    return () => {
      window.removeEventListener('online', checkOffline);
      window.removeEventListener('offline', checkOffline);
      window.removeEventListener('online', handleOnline);
    }
  }, []);"""

settings = settings.replace(old_handle_online, new_handle_online)

# Add manual sync button
old_pending_ui = """        {pendingSync > 0 && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
            <p className="font-bold">{pendingSync} records waiting to sync.</p>
          </div>
        )}"""

new_pending_ui = """        {pendingSync > 0 && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm flex items-center justify-between">
            <span className="font-bold text-blue-800">{pendingSync} records waiting to sync.</span>
            <button 
              onClick={() => {
                if (navigator.onLine) {
                  // Re-trigger the same sync logic manually
                  const event = new Event('online');
                  window.dispatchEvent(event);
                } else {
                  alert("You are still offline!");
                }
              }}
              className="bg-blue-600 text-white px-3 py-1.5 rounded-lg font-medium text-xs shadow-sm hover:bg-blue-700"
            >
              Sync Now
            </button>
          </div>
        )}"""

settings = settings.replace(old_pending_ui, new_pending_ui)

with open('components/SettingsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(settings)

print("Done")
