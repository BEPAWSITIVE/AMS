import os

with open('components/ReportsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_code = """"use client";
import { useState, useEffect } from "react";
import { supabase, AttendanceRecord } from "@/lib/supabase";
import { CalendarDays, Clock, Users, FileBarChart2, ChevronDown } from "lucide-react";

export default function ReportsTab() {
  const [logs, setLogs] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState("");

  useEffect(() => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    setSelectedMonth(`${yyyy}-${mm}`);

    if (navigator.onLine) {
      supabase.from('attendance').select('*').order('inTimestamp', { ascending: false })
        .then(({ data }) => {
          if (data) setLogs(data);
          setLoading(false);
        });
    } else {
      const cached = localStorage.getItem('cached_logs');
      if (cached) setLogs(JSON.parse(cached));
      setLoading(false);
    }
  }, []);

  const availableMonths = Array.from(new Set(logs.map(l => l.date.substring(0, 7)))).sort().reverse();
  if (selectedMonth && !availableMonths.includes(selectedMonth)) {
    availableMonths.unshift(selectedMonth); // ensure current month is always an option
  }

  const filteredLogs = logs.filter(l => l.date.startsWith(selectedMonth));

  let daysInMonth = 30;
  if (selectedMonth) {
    const [y, m] = selectedMonth.split('-');
    daysInMonth = new Date(parseInt(y), parseInt(m), 0).getDate();
  }

  const employeeStats = filteredLogs.reduce((acc: any, log: AttendanceRecord) => {
    if (log.category === 'Vehicle' || log.category === 'Parcel') return acc;
    
    if (!acc[log.empId]) {
      acc[log.empId] = {
        name: log.empName,
        category: log.category || 'Staff',
        daysSet: new Set(),
        totalHours: 0
      };
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

  const statsList = Object.values(employeeStats).map((stat: any) => ({
    ...stat,
    workingDays: stat.daysSet.size,
    totalHoursFormatted: Math.floor(stat.totalHours) + 'h ' + Math.round((stat.totalHours % 1) * 60) + 'm'
  })).sort((a: any, b: any) => b.totalHours - a.totalHours);

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
                <div key={idx} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-gray-800">{stat.name}</h4>
                    <span className="text-[10px] uppercase font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded-md">
                      {stat.category}
                    </span>
                  </div>
                  <div className="text-right flex flex-col space-y-1">
                    <span className="flex items-center text-xs font-bold text-gray-600 justify-end">
                      <CalendarDays size={12} className="mr-1 text-gray-400" />
                      {stat.workingDays} / {daysInMonth} Days
                    </span>
                    <span className="flex items-center text-xs font-bold text-gray-600 justify-end">
                      <Clock size={12} className="mr-1 text-gray-400" />
                      {stat.totalHoursFormatted}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
"""

with open('components/ReportsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Done")
