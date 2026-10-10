import os
import re

with open('components/ReportsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'<h3 className="font-bold text-gray-700 mt-6 mb-2">Individual Performance<\/h3>[\s\S]*?\)\}\s*<\/div>\s*\)\}\s*<\/div>\s*\);\s*\}'

replacement = """<h3 className="font-bold text-gray-700 mt-6 mb-2">Individual Performance</h3>
          
          {statsList.length === 0 ? (
            <div className="text-center py-10 text-gray-400 bg-white rounded-2xl border border-dashed border-gray-200">
              No records found for {formatMonthName(selectedMonth)}.
            </div>
          ) : (
            <div className="space-y-3">
              {statsList.map((stat: any, idx: number) => (
                <div key={idx} onClick={() => setSelectedReport(stat)} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between cursor-pointer hover:border-blue-300 transition-colors">
                  <div>
                    <h4 className="font-bold text-gray-800">{stat.name}</h4>
                    <div className="flex items-center space-x-2 mt-0.5">
                      <span className="text-[10px] uppercase font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded-md">
                        {stat.category}
                      </span>
                      {stat.phone && <span className="text-[10px] text-gray-500 font-mono">{stat.phone}</span>}
                      {stat.vehicle_plate && <span className="text-[10px] text-gray-500 font-mono">{stat.vehicle_plate}</span>}
                    </div>
                  </div>
                  <div className="text-right flex flex-col space-y-1">
                    <span className="flex items-center text-xs font-bold text-gray-600 justify-end">
                      <CalendarDays size={12} className="mr-1 text-gray-400" />
                      {stat.workingDays} / {daysInMonth} Days
                    </span>
                    {stat.category === 'Vehicle' ? (
                      <span className="flex items-center text-xs font-bold text-amber-600 justify-end">
                        <Navigation size={12} className="mr-1 text-amber-500" />
                        {stat.totalDistance} km
                      </span>
                    ) : (
                      <span className="flex items-center text-xs font-bold text-gray-600 justify-end">
                        <Clock size={12} className="mr-1 text-gray-400" />
                        {stat.totalHoursFormatted}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Detail Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex flex-col p-4 animate-fade-in pb-safe">
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
                  <Clock size={16} className="mr-2 text-gray-400" /> Activity Log ({formatMonthName(selectedMonth)})
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
                          {selectedReport.category === 'Vehicle' && log.meter_in ? <p className="mt-0.5">Meter: {log.meter_in}</p> : null}
                        </div>
                        <div className="text-right">
                          <p>OUT: <span className="text-gray-800">{log.outTime || '--:--'}</span></p>
                          {selectedReport.category === 'Vehicle' && log.meter_out ? <p className="mt-0.5">Meter: {log.meter_out}</p> : null}
                        </div>
                      </div>
                      {selectedReport.category === 'Vehicle' && (Number(log.meter_in) > 0 && Number(log.meter_out) > 0 && Number(log.meter_in) > Number(log.meter_out)) && (
                        <div className="mt-2 pt-2 border-t border-gray-50 text-xs font-bold text-amber-600 text-right">
                          Trip: {Number(log.meter_in) - Number(log.meter_out)} km
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
      )}
    </div>
  );
}"""

if re.search(pattern, code):
    code = re.sub(pattern, replacement, code)
else:
    print("Failed to replace")

with open('components/ReportsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Done")
