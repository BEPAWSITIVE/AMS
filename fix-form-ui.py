import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the specific UI block
form_pattern = r'\{\s*category === \'Vehicle\' \? \([\s\S]*?className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono uppercase"\s*placeholder="e.g. MH-12-AB-1234"\s*\/>\s*<\/div>\s*\)\s*:\s*category !== \'Parcel\' \? \(\s*<div>\s*<label className="block text-xs font-bold text-gray-500 mb-1">Department \/ Company<\/label>\s*<input \s*type="text" \s*value=\{department\} \s*onChange=\{e => setDepartment\(e\.target\.value\)\}\s*className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"\s*\/>\s*<\/div>\s*\)\s*:\s*null\s*\}'

new_form = """              {category === 'Vehicle' ? (
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-1">License Plate Number</label>
                  <input 
                    type="text" 
                    value={vehiclePlate} 
                    onChange={e => setVehiclePlate(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono uppercase"
                    placeholder="e.g. MH-12-AB-1234"
                  />
                </div>
              ) : category !== 'Parcel' ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Department / Company</label>
                    <input 
                      type="text" 
                      value={department} 
                      onChange={e => setDepartment(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Identity ID No. (Aadhar, PAN, etc.)</label>
                    <input 
                      type="text" 
                      value={vehiclePlate} 
                      onChange={e => setVehiclePlate(e.target.value)}
                      placeholder="e.g. 1234-5678-9012"
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono uppercase"
                    />
                  </div>
                </div>
              ) : null}"""

if re.search(form_pattern, code):
    code = re.sub(form_pattern, new_form, code)
    print("Form replaced successfully")
else:
    print("Failed to find form pattern")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
