import os

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

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
                  className={`w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-medium ${role === 'guard' ? 'opacity-70 cursor-not-allowed' : ''}`}
                  disabled={role === 'guard'}
                >
                  {role === 'admin' && <option value="Staff">Staff</option>}
                  <option value="Visitor">Visitor</option>
                  {role === 'admin' && <option value="Volunteer">Volunteer</option>}
                  {role === 'admin' && <option value="Workexchange">Work Exchange</option>}
                  {role === 'admin' && <option value="Vehicle">Vehicle</option>}
                </select>
              </div>"""

if old_select in code:
    code = code.replace(old_select, new_select)
else:
    print("WARNING: Could not find old select block exactly.")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
