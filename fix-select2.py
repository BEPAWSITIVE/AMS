import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'<select\s+value=\{category\}\s+onChange=\{handleCategoryChange\}[^>]*>.*?<\/select>'

replacement = """<select 
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
                </select>"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done")
