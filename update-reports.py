import os
import re

with open('components/ReportsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update the EmployeeStats logic to sum distance for vehicles
target_reduce = """  const employeeStats = filteredLogs.reduce((acc: any, log: AttendanceRecord) => {
    if (!acc[log.empId]) {
      acc[log.empId] = {
        empId: log.empId,
        name: log.empName,
        category: log.category || 'Staff',
        daysSet: new Set(),
        totalHours: 0
      };
    }"""

new_reduce = """  const employeeStats = filteredLogs.reduce((acc: any, log: AttendanceRecord) => {
    if (!acc[log.empId]) {
      acc[log.empId] = {
        empId: log.empId,
        name: log.empName,
        category: log.category || 'Staff',
        daysSet: new Set(),
        totalHours: 0,
        totalDistance: 0,
        logs: []
      };
    }
    
    acc[log.empId].logs.push(log);
    
    // Calculate distance for vehicles
    if (log.category === 'Vehicle') {
      const min = Number(log.meter_in) || 0;
      const mout = Number(log.meter_out) || 0;
      if (min > 0 && mout > 0 && min > mout) {
        acc[log.empId].totalDistance += (min - mout);
      }
    }
"""
code = code.replace(target_reduce, new_reduce)

# 2. Add Selected modal state and UI
import_target = 'import { CalendarDays, Clock, Users, FileBarChart2, ChevronDown , Search } from "lucide-react";'
new_imports = 'import { CalendarDays, Clock, Users, FileBarChart2, ChevronDown , Search, X, MapPin, Navigation } from "lucide-react";'
code = code.replace(import_target, new_imports)

state_target = '  const [employeesMap, setEmployeesMap] = useState<Record<string, any>>({});'
new_state = '  const [employeesMap, setEmployeesMap] = useState<Record<string, any>>({});\n  const [selectedReport, setSelectedReport] = useState<any>(null);'
code = code.replace(state_target, new_state)

# 3. Update the Card rendering to include onClick and new Vehicle stats
# And inject the modal at the very end
card_target = r'<div key=\{stat\.empId\} className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex justify-between items-center">'
new_card = r'<div key={stat.empId} onClick={() => setSelectedReport(stat)} className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex justify-between items-center cursor-pointer hover:border-blue-300 transition-colors">'
code = re.sub(card_target, new_card, code)

# Let's completely replace the mapping inside `statsList.length === 0 ? ... : ...`
stats_list_target = """        {statsList.length === 0 ? (
          <div className="text-center py-10 text-gray-400 bg-white rounded-2xl border border-dashed border-gray-200">
            No records found for the selected criteria.
          </div>
        ) : (
          statsList.map((stat: any) => (
            <div key={stat.empId} className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-gray-800 text-lg flex items-center">
                  {stat.name}
                  <span className={`ml-2 text-[10px] px-2 py-0.5 rounded-full font-bold ${
                    stat.category === 'Staff' ? 'bg-blue-100 text-blue-700' :
                    stat.category === 'Visitor' ? 'bg-emerald-100 text-emerald-700' :
                    stat.category === 'Vehicle' ? 'bg-amber-100 text-amber-700' :
                    'bg-purple-100 text-purple-700'
                  }`}>
                    {stat.category}
                  </span>
                </h3>
                <p className="text-xs text-gray-500 font-medium">ID: {stat.empId} {stat.phone ? `• ${stat.phone}` : ''} {stat.vehicle_plate ? `• Plate: ${stat.vehicle_plate}` : ''}</p>
                <div className="flex items-center space-x-3 mt-2 text-gray-600 text-sm">
                  <div className="flex items-center font-semibold bg-gray-50 px-2 py-1 rounded-lg">
                    <CalendarDays size={14} className="mr-1.5 text-blue-500" />
                    {stat.workingDays} Days
                  </div>
                  <div className="flex items-center font-semibold bg-gray-50 px-2 py-1 rounded-lg">
                    <Clock size={14} className="mr-1.5 text-blue-500" />
                    {stat.totalHoursFormatted}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}"""

new_stats_list = """        {statsList.length === 0 ? (
          <div className="text-center py-10 text-gray-400 bg-white rounded-2xl border border-dashed border-gray-200">
            No records found for the selected criteria.
          </div>
        ) : (
          statsList.map((stat: any) => (
            <div key={stat.empId} onClick={() => setSelectedReport(stat)} className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex justify-between items-center cursor-pointer hover:border-blue-300 transition-colors">
              <div>
                <h3 className="font-bold text-gray-800 text-lg flex items-center">
                  {stat.name}
                  <span className={`ml-2 text-[10px] px-2 py-0.5 rounded-full font-bold ${
                    stat.category === 'Staff' ? 'bg-blue-100 text-blue-700' :
                    stat.category === 'Visitor' ? 'bg-emerald-100 text-emerald-700' :
                    stat.category === 'Vehicle' ? 'bg-amber-100 text-amber-700' :
                    'bg-purple-100 text-purple-700'
                  }`}>
                    {stat.category}
                  </span>
                </h3>
                <p className="text-xs text-gray-500 font-medium">ID: {stat.empId} {stat.phone ? `• ${stat.phone}` : ''} {stat.vehicle_plate ? `• Plate: ${stat.vehicle_plate}` : ''}</p>
                <div className="flex items-center space-x-3 mt-2 text-gray-600 text-sm">
                  <div className="flex items-center font-semibold bg-gray-50 px-2 py-1 rounded-lg">
                    <CalendarDays size={14} className="mr-1.5 text-blue-500" />
                    {stat.workingDays}/{daysInMonth} Days
                  </div>
                  {stat.category === 'Vehicle' ? (
                    <div className="flex items-center font-semibold bg-gray-50 px-2 py-1 rounded-lg text-amber-700">
                      <Navigation size={14} className="mr-1.5 text-amber-500" />
                      {stat.totalDistance} km
                    </div>
                  ) : (
                    <div className="flex items-center font-semibold bg-gray-50 px-2 py-1 rounded-lg">
                      <Clock size={14} className="mr-1.5 text-blue-500" />
                      {stat.totalHoursFormatted}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        
        {/* Detail Modal */}
        {selectedReport && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex flex-col p-4 animate-fade-in pb-safe">
            <div className="bg-white rounded-3xl w-full max-w-md mx-auto flex flex-col overflow-hidden shadow-2xl h-full max-h-[90vh]">
              <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50 shrink-0">
                <div>
                  <h3 className="font-bold text-xl text-gray-800">{selectedReport.name}</h3>
                  <p className="text-sm text-gray-500 font-medium">{selectedReport.empId} • {selectedReport.category}</p>
                </div>
                <button onClick={() => setSelectedReport(null)} className="p-2 bg-white text-gray-500 rounded-full hover:bg-gray-200 shadow-sm">
                  <X size={20} />
                </button>
              </div>
              
              <div className="p-5 overflow-y-auto flex-1 space-y-4">
                <div className="bg-blue-50 border border-blue-100 p-4 rounded-2xl flex justify-around text-center">
                  <div>
                    <p className="text-xs text-blue-600 font-bold uppercase tracking-wider mb-1">Active Days</p>
                    <p className="text-2xl font-black text-blue-900">{selectedReport.workingDays}<span className="text-sm font-bold text-blue-400">/{daysInMonth}</span></p>
                  </div>
                  {selectedReport.category === 'Vehicle' ? (
                    <div>
                      <p className="text-xs text-amber-600 font-bold uppercase tracking-wider mb-1">Distance</p>
                      <p className="text-2xl font-black text-amber-900">{selectedReport.totalDistance}<span className="text-sm font-bold text-amber-400"> km</span></p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-xs text-blue-600 font-bold uppercase tracking-wider mb-1">Total Hours</p>
                      <p className="text-lg font-black text-blue-900 mt-1">{selectedReport.totalHoursFormatted}</p>
                    </div>
                  )}
                </div>

                <div>
                  <h4 className="font-bold text-gray-800 mb-3 flex items-center">
                    <Clock size={16} className="mr-2 text-gray-400" /> Activity Log ({selectedMonth})
                  </h4>
                  <div className="space-y-3">
                    {selectedReport.logs.sort((a: any, b: any) => b.inTimestamp - a.inTimestamp).map((log: any) => (
                      <div key={log.recordId} className="bg-white border border-gray-100 p-3 rounded-xl shadow-sm">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-bold text-gray-700">{log.date}</span>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${log.status === 'IN' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600'}`}>{log.status}</span>
                        </div>
                        <div className="flex justify-between text-xs font-medium text-gray-500">
                          <div>
                            <p>IN: <span className="text-gray-800">{log.inTime}</span></p>
                            {selectedReport.category === 'Vehicle' && log.meter_out ? <p className="mt-0.5">Meter: {log.meter_out}</p> : null}
                          </div>
                          <div className="text-right">
                            <p>OUT: <span className="text-gray-800">{log.outTime || '--:--'}</span></p>
                            {selectedReport.category === 'Vehicle' && log.meter_in ? <p className="mt-0.5">Meter: {log.meter_in}</p> : null}
                          </div>
                        </div>
                        {selectedReport.category === 'Vehicle' && (log.meter_in > 0 && log.meter_out > 0) && (
                          <div className="mt-2 pt-2 border-t border-gray-50 text-xs font-bold text-amber-600 text-right">
                            Trip: {log.meter_in - log.meter_out} km
                          </div>
                        )}
                        {selectedReport.category === 'Vehicle' && log.location && (
                          <div className="mt-2 pt-2 border-t border-gray-50 text-xs font-medium text-gray-500 flex items-center">
                            <MapPin size={12} className="mr-1" /> {log.location}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}"""
code = code.replace(stats_list_target, new_stats_list)


with open('components/ReportsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
