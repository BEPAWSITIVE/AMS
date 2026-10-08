"use client";
import { useState, useEffect } from "react";
import { supabase, AttendanceRecord } from "@/lib/supabase";
import { CalendarDays, Clock, Users, FileBarChart2 } from "lucide-react";

export default function ReportsTab() {
  const [logs, setLogs] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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

  // Simple aggregation
  const employeeStats = logs.reduce((acc: any, log: AttendanceRecord) => {
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
    
    // Attempt to parse totalHours (e.g., "08:30" format)
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

  return (
    <div className="p-4 pb-20 max-w-md mx-auto space-y-4">
      <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center">
        <FileBarChart2 size={24} className="mr-2 text-blue-600" /> Reports
      </h2>

      {loading ? (
        <div className="text-center py-10 text-gray-400">Crunching numbers...</div>
      ) : (
        <div className="space-y-4">
          
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-5 rounded-2xl shadow-md text-white">
            <h3 className="text-sm font-medium opacity-80 mb-1">Total Active Personnel</h3>
            <div className="text-4xl font-extrabold">{statsList.length}</div>
          </div>

          <h3 className="font-bold text-gray-700 mt-6 mb-2">Individual Performance</h3>
          
          {statsList.length === 0 ? (
            <div className="text-center py-10 text-gray-400 bg-white rounded-2xl border border-dashed border-gray-200">
              No completed attendance records found.
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
                      {stat.workingDays} Days
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
