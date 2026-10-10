"use client";
import { useState, useEffect } from "react";
import { supabase, AttendanceRecord } from "@/lib/supabase";
import { CalendarDays, Clock, Users, FileBarChart2, ChevronDown , Search, X, MapPin, Navigation } from "lucide-react";

export default function ReportsTab() {
  const [logs, setLogs] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Staff");
  const [searchQuery, setSearchQuery] = useState("");
  const [employeesMap, setEmployeesMap] = useState<Record<string, any>>({});
  const [selectedReport, setSelectedReport] = useState<any>(null);

  useEffect(() => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    setSelectedMonth(`${yyyy}-${mm}`);

    const loadData = async () => {
      if (navigator.onLine) {
        // Fetch employees to get phone numbers and plates
        const { data: emps } = await supabase.from('employees').select('*');
        if (emps) {
          const eMap: Record<string, any> = {};
          emps.forEach(e => eMap[e.empId] = e);
          setEmployeesMap(eMap);
        }

        const { data } = await supabase.from('attendance').select('*').order('inTimestamp', { ascending: false });
        if (data) setLogs(data);
      } else {
        const cached = localStorage.getItem('cached_logs');
        if (cached) setLogs(JSON.parse(cached));
        const cachedE = localStorage.getItem('cached_employees');
        if (cachedE) {
          const emps = JSON.parse(cachedE);
          const eMap: Record<string, any> = {};
          emps.forEach((e: any) => eMap[e.empId] = e);
          setEmployeesMap(eMap);
        }
      }
      setLoading(false);
    };
    
    loadData();
  }, []);

  const availableMonths = Array.from(new Set(logs.map(l => l.date.substring(0, 7)))).sort().reverse();
  if (selectedMonth && !availableMonths.includes(selectedMonth)) {
    availableMonths.unshift(selectedMonth); // ensure current month is always an option
  }

  const filteredLogs = logs.filter(l => {
    if (!l.date.startsWith(selectedMonth)) return false;
    if (l.category === 'Parcel') return false;
    
    const cat = l.category || 'Staff';
    if (selectedCategory === 'All') return true;
    return cat === selectedCategory;
  });

  let daysInMonth = 30;
  if (selectedMonth) {
    const [y, m] = selectedMonth.split('-');
    daysInMonth = new Date(parseInt(y), parseInt(m), 0).getDate();
  }

  const employeeStats = filteredLogs.reduce((acc: any, log: AttendanceRecord) => {
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

    
    acc[log.empId].daysSet.add(log.date);
    
    if (log.totalHours) {
      const [hours, mins] = log.totalHours.split(':').map(Number);
      if (!isNaN(hours) && !isNaN(mins)) {
        acc[log.empId].totalHours += hours + (mins / 60);
      }
    }
    
    return acc;
  }, {});

  const statsList = Object.values(employeeStats).map((stat: any) => {
    const empData = employeesMap[stat.empId] || {};
    return {
      ...stat,
      phone: empData.phone || '',
      vehicle_plate: empData.vehicle_plate || '',
      workingDays: stat.daysSet.size,
      totalHoursFormatted: Math.floor(stat.totalHours) + 'h ' + Math.round((stat.totalHours % 1) * 60) + 'm'
    };
  })
  .filter((stat: any) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      stat.name.toLowerCase().includes(q) ||
      stat.empId.toLowerCase().includes(q) ||
      (stat.phone && stat.phone.toLowerCase().includes(q)) ||
      (stat.vehicle_plate && stat.vehicle_plate.toLowerCase().includes(q))
    );
  })
  .sort((a: any, b: any) => b.totalHours - a.totalHours);

  const formatMonthName = (yyyy_mm: string) => {
    const [y, m] = yyyy_mm.split('-');
    const d = new Date(parseInt(y), parseInt(m) - 1, 1);
    return d.toLocaleString('default', { month: 'long', year: 'numeric' });
  };

  return (
    <div className="p-4 pb-20 max-w-md mx-auto space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          <FileBarChart2 size={24} className="mr-2 text-blue-600" /> Reports
        </h2>
        
        <div className="relative">
          <select 
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="appearance-none bg-blue-50 text-blue-700 font-bold py-2 pl-3 pr-8 rounded-xl border border-blue-100 outline-none focus:ring-2 focus:ring-blue-500 text-sm cursor-pointer"
          >
            {availableMonths.map(m => (
              <option key={m} value={m}>{formatMonthName(m)}</option>
            ))}
          </select>
          <ChevronDown size={14} className="absolute right-3 top-3 text-blue-500 pointer-events-none" />
        </div>
      </div>

      <div className="flex items-center space-x-2 mb-4">
        <div className="relative flex-grow">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search size={16} className="text-gray-400" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Name, ID, Phone, or Plate..."
            className="w-full bg-white border border-gray-200 pl-9 p-2 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm shadow-sm"
          />
        </div>
        <div className="relative w-1/3">
          <select 
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="appearance-none w-full bg-gray-50 text-gray-700 font-bold py-2 pl-3 pr-8 rounded-xl border border-gray-200 outline-none focus:ring-2 focus:ring-blue-500 text-sm cursor-pointer"
          >
            <option value="All">All Categories</option>
            <option value="Staff">Staff</option>
            <option value="Volunteer">Volunteer</option>
            <option value="Workexchange">Work Exchange</option>
            <option value="Vehicle">Vehicle</option>
            <option value="Visitor">Visitor</option>
          </select>
          <ChevronDown size={14} className="absolute right-3 top-3 text-gray-500 pointer-events-none" />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-10 text-gray-400">Crunching numbers...</div>
      ) : (
        <div className="space-y-4">
          
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-5 rounded-2xl shadow-md text-white flex justify-between items-center">
            <div>
              <h3 className="text-sm font-medium opacity-80 mb-1">Active Personnel</h3>
              <div className="text-4xl font-extrabold">{statsList.length}</div>
            </div>
            <div className="text-right">
              <h3 className="text-xs font-medium opacity-80 mb-1">In {formatMonthName(selectedMonth)}</h3>
              <div className="text-sm font-bold opacity-90">{daysInMonth} Total Days</div>
            </div>
          </div>

          <h3 className="font-bold text-gray-700 mt-6 mb-2">Individual Performance</h3>
          
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
}
