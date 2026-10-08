import os

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add role prop to EmployeesTab
code = code.replace('export default function EmployeesTab() {', 'export default function EmployeesTab({ role = "admin" }: { role?: "admin" | "guard" }) {')

# 2. Add Volunteer / Workexchange options to dropdown, but hide based on role
old_select = """              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">Category</label>
                <select 
                  value={category}
                  onChange={handleCategoryChange}
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-medium"
                >
                  <option value="Staff">Staff</option>
                  <option value="Visitor">Visitor / Volunteer</option>
                  <option value="Vehicle">Vehicle</option>
                  
                </select>
              </div>"""

new_select = """              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">Category</label>
                <select 
                  value={category}
                  onChange={handleCategoryChange}
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-medium"
                  disabled={role === 'guard'}
                >
                  {role === 'admin' && <option value="Staff">Staff</option>}
                  <option value="Visitor">Visitor</option>
                  {role === 'admin' && <option value="Volunteer">Volunteer</option>}
                  {role === 'admin' && <option value="Workexchange">Work Exchange</option>}
                  {role === 'admin' && <option value="Vehicle">Vehicle</option>}
                </select>
              </div>"""
code = code.replace(old_select, new_select)

# 3. UseEffect to force "Visitor" if guard
hook_insert = """
  useEffect(() => {
    if (role === 'guard' && category !== 'Visitor') {
      setCategory('Visitor');
    }
  }, [role, category]);
"""
code = code.replace('const [vehiclePlate, setVehiclePlate] = useState("");', 'const [vehiclePlate, setVehiclePlate] = useState("");\n' + hook_insert)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
