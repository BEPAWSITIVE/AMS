import os

emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

if "employeeQueue" not in emp:
    emp = emp.replace('import { supabase, Employee } from "@/lib/supabase";', 'import { supabase, Employee } from "@/lib/supabase";\nimport { localdb } from "@/lib/localdb";')
    
    old_handle = """  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!empId || !name) return;
    
    const { error } = await supabase.from('employees').insert([{
      empId, name, department, phone
    }]);
    
    if (error) {
      alert("Error adding employee: " + error.message);
      return;
    }
    
    setShowForm(false);
    setEmpId(""); setName(""); setDepartment(""); setPhone("");
    fetchEmployees();
  }"""
  
    new_handle = """  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!empId || !name) return;
    
    const newEmp = {
      empId, name, department, phone, createdAt: new Date().toISOString()
    };
    
    if (navigator.onLine) {
      try {
        const { error } = await supabase.from('employees').insert([newEmp]);
        if (error) throw error;
      } catch (err: any) {
        alert("Error adding employee: " + err.message);
        return;
      }
    } else {
      // Save locally if offline
      await localdb.employeeQueue.put(newEmp);
      // Also update the cached list so they show up immediately
      const cached = localStorage.getItem('cached_employees');
      const currentList = cached ? JSON.parse(cached) : [];
      currentList.unshift(newEmp);
      localStorage.setItem('cached_employees', JSON.stringify(currentList));
    }
    
    setShowForm(false);
    setEmpId(""); setName(""); setDepartment(""); setPhone("");
    fetchEmployees();
  }"""
  
    emp = emp.replace(old_handle, new_handle)
    
    old_fetch = """  async function fetchEmployees() {
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
  
    new_fetch = """  async function fetchEmployees() {
    let allEmps: Employee[] = [];
    if (navigator.onLine) {
      const { data, error } = await supabase.from('employees').select('*').order('createdAt', { ascending: false });
      if (!error && data) {
        allEmps = data;
        localStorage.setItem('cached_employees', JSON.stringify(data));
      }
    } else {
      const cached = localStorage.getItem('cached_employees');
      if (cached) allEmps = JSON.parse(cached);
    }
    
    // Merge any offline queued employees that might not be synced yet
    const queuedEmps = await localdb.employeeQueue.toArray();
    const merged = [...queuedEmps, ...allEmps].reduce((acc, curr) => {
      if (!acc.find(item => item.empId === curr.empId)) acc.push(curr);
      return acc;
    }, [] as Employee[]);
    
    merged.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    setEmployees(merged);
    setLoading(false);
  }"""
  
    emp = emp.replace(old_fetch, new_fetch)
    with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
        f.write(emp)
print("Done")
