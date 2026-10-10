import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'(<label className="block text-xs font-bold text-gray-500 mb-1">Phone Number<\/label>\s*<input \s*type="tel" \s*value=\{phone\} \s*onChange=\{e => setPhone\(e\.target\.value\)\}\s*className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"\s*\/>\s*<\/div>\s*<\/div>\s*)'

replacement = r"""\1
                {category !== 'Parcel' && (
                  <div className="pt-2">
                    <label className="block text-xs font-bold text-gray-500 mb-1">Identity ID No. (Aadhar, PAN, etc.)</label>
                    <input 
                      type="text" 
                      value={vehiclePlate} 
                      onChange={e => setVehiclePlate(e.target.value)}
                      placeholder="e.g. 1234-5678-9012"
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono uppercase"
                    />
                  </div>
                )}
"""

if re.search(pattern, code):
    code = re.sub(pattern, replacement, code)
    print("Success")
else:
    print("Failed")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
