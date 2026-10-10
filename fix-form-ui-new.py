import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

target = """                <div className="flex space-x-3">
                  <div className="w-1/2">
                    <label className="block text-xs font-bold text-gray-500 mb-1">
                      {category === 'Visitor' ? 'Purpose/Org' : category === 'Parcel' ? 'Tracking # / Desc' : 'Department'}
                    </label>
                    <input 
                      type="text" 
                      value={department} 
                      onChange={e => setDepartment(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div className="w-1/2">
                    <label className="block text-xs font-bold text-gray-500 mb-1">Phone Number</label>
                    <input 
                      type="text" 
                      value={phone} 
                      onChange={e => setPhone(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              )}"""

new_ui = """                <div className="flex space-x-3">
                  <div className="w-1/2">
                    <label className="block text-xs font-bold text-gray-500 mb-1">
                      {category === 'Visitor' ? 'Purpose/Org' : category === 'Parcel' ? 'Tracking # / Desc' : 'Department'}
                    </label>
                    <input 
                      type="text" 
                      value={department} 
                      onChange={e => setDepartment(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div className="w-1/2">
                    <label className="block text-xs font-bold text-gray-500 mb-1">Phone Number</label>
                    <input 
                      type="text" 
                      value={phone} 
                      onChange={e => setPhone(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                {category !== 'Parcel' && (
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
                )}
              )}"""

if target in code:
    code = code.replace(target, new_ui)
    print("Success")
else:
    print("Target not found")
    
with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
