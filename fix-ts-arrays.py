import os

# Fix EmployeesTab
emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

old_reduce = """    const merged = [...queuedEmps, ...allEmps].reduce((acc, curr) => {
      if (!acc.find((item: Employee) => item.empId === curr.empId)) acc.push(curr);
      return acc;
    }, [] as Employee[]);
    
    merged.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());"""

new_reduce = """    const merged = [...queuedEmps, ...allEmps].reduce((acc: Employee[], curr: any) => {
      const current = curr as Employee;
      if (!acc.find((item: Employee) => item.empId === current.empId)) acc.push(current);
      return acc;
    }, [] as Employee[]);
    
    merged.sort((a: Employee, b: Employee) => new Date(b.createdAt || 0).getTime() - new Date(a.createdAt || 0).getTime());"""

emp = emp.replace(old_reduce, new_reduce)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(emp)


# Fix ParcelsTab
parcels = open('components/ParcelsTab.tsx', 'r', encoding='utf-8').read()

old_parcels_reduce = """    const merged = [...queuedParcels, ...allParcels].reduce((acc, curr) => {
      const idx = acc.findIndex((item: Parcel) => item.id === curr.id);
      if (idx === -1) {
        acc.push(curr);
      } else if (queuedParcels.find((q: Parcel) => q.id === curr.id)) {
        acc[idx] = curr;
      }
      return acc;
    }, [] as Parcel[]);
    
    merged.sort((a, b) => new Date(b.received_at).getTime() - new Date(a.received_at).getTime());"""

new_parcels_reduce = """    const merged = [...queuedParcels, ...allParcels].reduce((acc: Parcel[], curr: any) => {
      const current = curr as Parcel;
      const idx = acc.findIndex((item: Parcel) => item.id === current.id);
      if (idx === -1) {
        acc.push(current);
      } else if (queuedParcels.find((q: any) => (q as Parcel).id === current.id)) {
        acc[idx] = current;
      }
      return acc;
    }, [] as Parcel[]);
    
    merged.sort((a: Parcel, b: Parcel) => new Date(b.received_at).getTime() - new Date(a.received_at).getTime());"""

parcels = parcels.replace(old_parcels_reduce, new_parcels_reduce)

with open('components/ParcelsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(parcels)


# Check LogsTab just in case
logs = open('components/LogsTab.tsx', 'r', encoding='utf-8').read()
old_logs_reduce = """    const merged = [...queuedLogs, ...allLogs].reduce((acc, curr) => {
      const idx = acc.findIndex(item => item.recordId === curr.recordId);
      if (idx === -1) {
        acc.push(curr);
      } else if (queuedLogs.find(q => q.recordId === curr.recordId)) {
        acc[idx] = curr;
      }
      return acc;
    }, [] as AttendanceRecord[]);
    
    merged.sort((a, b) => b.inTimestamp - a.inTimestamp);"""

new_logs_reduce = """    const merged = [...queuedLogs, ...allLogs].reduce((acc: AttendanceRecord[], curr: any) => {
      const current = curr as AttendanceRecord;
      const idx = acc.findIndex((item: AttendanceRecord) => item.recordId === current.recordId);
      if (idx === -1) {
        acc.push(current);
      } else if (queuedLogs.find((q: any) => (q as AttendanceRecord).recordId === current.recordId)) {
        acc[idx] = current;
      }
      return acc;
    }, [] as AttendanceRecord[]);
    
    merged.sort((a: AttendanceRecord, b: AttendanceRecord) => b.inTimestamp - a.inTimestamp);"""

logs = logs.replace(old_logs_reduce, new_logs_reduce)

with open('components/LogsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(logs)

print("Done")
