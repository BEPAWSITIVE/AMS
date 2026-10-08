import os

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_func = """  const handleOpenForm = () => {
    setCategory("Staff");
    generateNewId("Staff");
    setName("");
    setDepartment("");
    setPhone("+91 ");
    setVehiclePlate("");
    setDocumentFile(null);
    setGroupMembers([""]);
    setShowForm(true);
  };"""

new_func = """  const handleOpenForm = () => {
    const defaultCat = role === 'guard' ? 'Visitor' : 'Staff';
    setCategory(defaultCat);
    generateNewId(defaultCat);
    setName("");
    setDepartment("");
    setPhone("+91 ");
    setVehiclePlate("");
    setDocumentFile(null);
    setGroupMembers([""]);
    setShowForm(true);
  };"""

code = code.replace(old_func, new_func)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
