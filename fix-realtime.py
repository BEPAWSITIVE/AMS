import os

# Update LogsTab.tsx
logs = open('components/LogsTab.tsx', 'r', encoding='utf-8').read()
if "supabase.channel" not in logs:
    old_useeffect = """  useEffect(() => {
    fetchLogs();
  }, []);"""
  
    new_useeffect = """  useEffect(() => {
    fetchLogs();
    
    const channel = supabase
      .channel('attendance_changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'attendance' },
        (payload) => {
          fetchLogs();
        }
      )
      .subscribe();

    // Fallback polling every 30 seconds just in case realtime isn't enabled in dashboard
    const interval = setInterval(() => {
      if (navigator.onLine) fetchLogs();
    }, 30000);

    return () => {
      supabase.removeChannel(channel);
      clearInterval(interval);
    };
  }, []);"""
  
    logs = logs.replace(old_useeffect, new_useeffect)
    with open('components/LogsTab.tsx', 'w', encoding='utf-8') as f:
        f.write(logs)

# Update EmployeesTab.tsx
emps = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()
if "supabase.channel" not in emps:
    old_useeffect = """  useEffect(() => {
    fetchEmployees();
  }, []);"""
  
    new_useeffect = """  useEffect(() => {
    fetchEmployees();
    
    const channel = supabase
      .channel('employees_changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'employees' },
        (payload) => {
          fetchEmployees();
        }
      )
      .subscribe();

    const interval = setInterval(() => {
      if (navigator.onLine) fetchEmployees();
    }, 30000);

    return () => {
      supabase.removeChannel(channel);
      clearInterval(interval);
    };
  }, []);"""
  
    emps = emps.replace(old_useeffect, new_useeffect)
    with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
        f.write(emps)

print("Done")
