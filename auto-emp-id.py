import sys

content = open('components/EmployeesTab.tsx', 'r').read()

# Add handleOpenForm function
function_to_inject = """  function handleOpenForm() {
    const newId = "EMP-" + Math.random().toString(36).substring(2, 6).toUpperCase();
    setEmpId(newId);
    setShowForm(true);
  }

  async function handleAdd(e: React.FormEvent) {"""
content = content.replace("  async function handleAdd(e: React.FormEvent) {", function_to_inject)

# Change the Add Employee button
content = content.replace("onClick={() => setShowForm(true)}", "onClick={handleOpenForm}")

# Update the Employee ID input to be readOnly
old_input = '<input required value={empId} onChange={e=>setEmpId(e.target.value)} className="w-full border rounded p-2" />'
new_input = '<input required value={empId} readOnly className="w-full border rounded p-2 bg-gray-50 text-gray-500 font-mono" />'
content = content.replace(old_input, new_input)

open('components/EmployeesTab.tsx', 'w').write(content)
print('Done')
