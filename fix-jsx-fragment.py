import os

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the start of the branch
target_start = """) : (
              <div className="flex space-x-3">
                <div className="w-1/2">"""

replacement_start = """) : (
              <div className="space-y-4">
                <div className="flex space-x-3">
                  <div className="w-1/2">"""

code = code.replace(target_start, replacement_start)

# Replace the end of the branch
target_end = """                {category !== 'Parcel' && (
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
)}"""

replacement_end = """                {category !== 'Parcel' && (
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
              </div>
            )}"""

code = code.replace(target_end, replacement_end)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Done!")
