import sys

content = """"use client";
import { useEffect, useState } from "react";
import { supabase, AttendanceRecord } from "@/lib/supabase";
import { User, LogIn, LogOut, CheckCircle2, CloudOff, ClipboardList } from "lucide-react";

export default function LogsTab() {
  const [logs, setLogs] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogs();
  }, []);

  async function fetchLogs() {
    const { data, error } = await supabase.from('attendance').select('*').order('inTimestamp', { ascending: false });
    if (!error && data) {
      setLogs(data);
    }
    setLoading(false);
  }

  return (
    <div className="pb-20">
      <div className="p-4 bg-white shadow-sm border-b sticky top-0 z-10 flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-800">Recent Scans</h2>
        <span className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded font-medium">Today</span>
      </div>

      <div className="px-4 pt-4 space-y-4">
        {loading ? (
           <p className="text-center text-gray-500 py-10">Loading...</p>
        ) : logs.length === 0 ? (
          <div className="text-center py-10 text-gray-400">
            <ClipboardList className="mx-auto mb-2 opacity-50" size={40} />
            <p>No attendance logs yet.</p>
          </div>
        ) : (
          logs.map(log => (
            <div key={log.recordId} className="bg-white p-4 rounded-xl border shadow-sm relative">
              <div className="absolute top-4 right-4">
                {log.isSynced ? (
                  <CheckCircle2 size={16} className="text-green-500" />
                ) : (
                  <CloudOff size={16} className="text-orange-400" />
                )}
              </div>
              
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                  <User size={20} />
                </div>
                <div>
                  <h3 className="font-bold text-gray-800">{log.empName}</h3>
                  <p className="text-xs text-gray-500">{log.department} - {log.empId}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 bg-gray-50 p-3 rounded-lg border border-gray-100">
                <div className="flex items-center space-x-2">
                  <LogIn size={16} className="text-green-600" />
                  <div>
                    <p className="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Time In</p>
                    <p className="text-sm font-semibold text-gray-700">{log.inTime}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <LogOut size={16} className="text-red-500" />
                  <div>
                    <p className="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Time Out</p>
                    <p className="text-sm font-semibold text-gray-700">{log.outTime || '--:--'}</p>
                  </div>
                </div>
              </div>

              {log.totalHours && (
                <div className="mt-3 text-center text-xs font-medium text-blue-600 bg-blue-50 py-1.5 rounded-md">
                  Total Session: {log.totalHours}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
"""
open('components/LogsTab.tsx', 'w', encoding='utf-8').write(content)
print("Done")
