import os

# 1. Update EmployeesTab.tsx to save employees to localStorage when fetched
emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()
if "localStorage.setItem" not in emp:
    old_fetch = """  async function fetchEmployees() {
    const { data, error } = await supabase.from('employees').select('*').order('createdAt', { ascending: false });
    if (!error && data) {
      setEmployees(data);
    }
    setLoading(false);
  }"""
    new_fetch = """  async function fetchEmployees() {
    if (navigator.onLine) {
      const { data, error } = await supabase.from('employees').select('*').order('createdAt', { ascending: false });
      if (!error && data) {
        setEmployees(data);
        localStorage.setItem('cached_employees', JSON.stringify(data));
      }
    } else {
      const cached = localStorage.getItem('cached_employees');
      if (cached) setEmployees(JSON.parse(cached));
    }
    setLoading(false);
  }"""
    emp = emp.replace(old_fetch, new_fetch)
    with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
        f.write(emp)

# 2. Update ScannerTab.tsx to use localStorage fallback for employees
scan = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()
if "localStorage.getItem('cached_employees')" not in scan:
    old_lookup = """      const { data: empData, error: empError } = await supabase.from('employees').select('*').eq('empId', empId).single();
      
      if (empError || !empData) {"""
      
    new_lookup = """      let empData = null;
      let existingRecords: any[] | null = null;
      
      if (navigator.onLine) {
        const { data } = await supabase.from('employees').select('*').eq('empId', empId).single();
        empData = data;
        const { data: existing } = await supabase
          .from('attendance')
          .select('*')
          .eq('date', dateStr)
          .eq('empId', empId)
          .order('inTimestamp', { ascending: true });
        existingRecords = existing;
      } else {
        const cached = localStorage.getItem('cached_employees');
        if (cached) {
          const employees = JSON.parse(cached);
          empData = employees.find((e: any) => e.empId === empId);
        }
        // If offline, check local sync queue for existing IN records today
        const queue = await localdb.syncQueue.where({ empId: empId, date: dateStr }).toArray();
        existingRecords = queue;
      }
      
      if (!empData) {"""
      
    # First, let's remove the second fetch of existingRecords since we integrated it above
    old_second_fetch = """        const { data: existingRecords } = await supabase
          .from('attendance')
          .select('*')
          .eq('date', dateStr)
          .eq('empId', empId)
          .order('inTimestamp', { ascending: true });"""
    
    scan = scan.replace(old_lookup, new_lookup).replace(old_second_fetch, "")
    with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
        f.write(scan)

print("Done")
