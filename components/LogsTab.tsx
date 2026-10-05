"use client";
import { useState, useEffect } from "react";
import { supabase, AttendanceRecord } from "@/lib/supabase";
import { localdb } from "@/lib/localdb";
import { Clock, CheckCircle2, UserPlus, Truck, Shield, Package } from "lucide-react";

export default function LogsTab() {
  const [logs, setLogs] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogs();
    
    const channel = supabase
      .channel('attendance_changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'attendance' },
        (payload) => {
          fetchLogs();
        }
      )
      .subscribe();

    const interval = setInterval(() => {
      if (navigator.onLine) fetchLogs();
    }, 30000);

    return () => {
      supabase.removeChannel(channel);
      clearInterval(interval);
    };
  }, []);

  async function fetchLogs() {
    let allLogs: AttendanceRecord[] = [];
    
    if (navigator.onLine) {
      const { data, error } = await supabase.from('attendance').select('*').order('inTimestamp', { ascending: false });
      if (!error && data) {
        allLogs = data;
        localStorage.setItem('cached_logs', JSON.stringify(data));
      }
    } else {
      const cached = localStorage.getItem('cached_logs');
      if (cached) allLogs = JSON.parse(cached);
    }

    const queue = await localdb.syncQueue.toArray();
    
    const merged = [...queue, ...allLogs].reduce((acc, curr) => {
      if (!acc.find(item => item.recordId === curr.recordId)) {
        acc.push(curr);
      } else {
        const idx = acc.findIndex(item => item.recordId === curr.recordId);
        if (queue.find(q => q.recordId === curr.recordId)) {
          acc[idx] = curr;
        }
      }
      return acc;
    }, [] as AttendanceRecord[]);

    merged.sort((a, b) => b.inTimestamp - a.inTimestamp);
    setLogs(merged);
    setLoading(false);
  }

  const getCategoryIcon = (cat?: string) => {
    if (cat === 'Vehicle') return <Truck size={16} className="text-amber-500" />;
    if (cat === 'Parcel') return <Package size={16} className="text-purple-500" />;
    if (cat === 'Visitor') return <UserPlus size={16} className="text-emerald-500" />;
    return <Shield size={16} className="text-blue-500" />;
  };

  return (
    <div className="p-4 pb-20 max-w-md mx-auto space-y-4">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">Activity Logs</h2>

      {loading ? (
        <div className="text-center py-10 text-gray-400">Loading logs...</div>
      ) : logs.length === 0 ? (
        <div className="text-center py-10 text-gray-400 bg-white rounded-2xl border border-dashed border-gray-200">
          No activity logs found.
        </div>
      ) : (
        <div className="space-y-3">
          {logs.map(log => (
            <div key={log.recordId} className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col relative overflow-hidden">
              {/* Sync Indicator */}
              <div className="absolute top-0 right-0">
                {log.isSynced === 1 ? (
                  <div className="bg-green-100 text-green-600 p-1.5 rounded-bl-xl" title="Synced to Cloud">
                    <CheckCircle2 size={12} />
                  </div>
                ) : (
                  <div className="bg-orange-100 text-orange-600 p-1.5 rounded-bl-xl" title="Pending Sync">
                    <Clock size={12} />
                  </div>
                )}
              </div>

              <div className="flex items-start justify-between mt-1 mb-2">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-gray-800">{log.empName}</h3>
                    <span className="flex items-center text-[10px] uppercase tracking-wider font-bold bg-gray-100 text-gray-500 px-2 py-0.5 rounded-md">
                      {getCategoryIcon(log.category)} <span className="ml-1">{log.category || 'Staff'}</span>
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 font-mono">{log.empId} • {log.date}</p>
                </div>
                
                {log.category !== 'Vehicle' && log.category !== 'Parcel' && (
                  <div className={`px-2 py-1 rounded-md text-xs font-bold ${log.status === 'IN' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                    {log.status === 'IN' ? 'Active' : 'Completed'}
                  </div>
                )}
                {log.category === 'Parcel' && (
                  <div className={`px-2 py-1 rounded-md text-xs font-bold ${log.status === 'IN' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'}`}>
                    {log.status === 'IN' ? 'At Gate' : 'Picked Up'}
                  </div>
                )}
                {log.category === 'Vehicle' && (
                  <div className={`px-2 py-1 rounded-md text-xs font-bold ${log.status === 'IN' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'}`}>
                    {log.status === 'IN' ? 'Dispatched' : 'Returned'}
                  </div>
                )}
              </div>

              {log.category === 'Parcel' ? (
                <div className="flex items-center space-x-2 mt-1">
                  <div className="flex-1 bg-purple-50 p-2 rounded-xl text-center border border-purple-100">
                    <span className="block text-[10px] text-purple-600 uppercase font-bold tracking-widest">Received</span>
                    <span className="font-bold text-gray-800">{log.inTime}</span>
                  </div>
                  <div className="flex-1 bg-gray-50 p-2 rounded-xl text-center border border-gray-100">
                    <span className="block text-[10px] text-gray-500 uppercase font-bold tracking-widest">{log.driver_name ? `Given to ${log.driver_name}` : 'Awaiting Pickup'}</span>
                    <span className="font-bold text-gray-800">{log.outTime || "--:--"}</span>
                  </div>
                </div>
              ) : log.category === 'Vehicle' ? (
                <div className="bg-amber-50/50 rounded-xl p-3 text-sm mt-1 border border-amber-100">
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-500 font-bold text-xs">Driver:</span>
                    <span className="font-bold text-gray-800">{log.driver_name}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <div className="text-center">
                      <span className="block text-[10px] text-gray-400 uppercase font-bold tracking-widest">Out ({log.inTime})</span>
                      <span className="font-mono font-bold text-gray-800">{log.meter_out}</span>
                    </div>
                    <div className="h-px bg-gray-300 w-8 mx-2"></div>
                    <div className="text-center">
                      <span className="block text-[10px] text-gray-400 uppercase font-bold tracking-widest">In ({log.outTime || '--'})</span>
                      <span className="font-mono font-bold text-gray-800">{log.meter_in || '--'}</span>
                    </div>
                  </div>
                  {log.totalHours && (
                    <div className="mt-2 pt-2 border-t border-amber-200/50 text-center font-bold text-amber-800 text-xs">
                      {log.totalHours}
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center space-x-2 mt-1">
                  <div className="flex-1 bg-green-50 p-2 rounded-xl text-center border border-green-100">
                    <span className="block text-[10px] text-green-600 uppercase font-bold tracking-widest">Check In</span>
                    <span className="font-bold text-gray-800">{log.inTime}</span>
                  </div>
                  <div className="flex-1 bg-gray-50 p-2 rounded-xl text-center border border-gray-100">
                    <span className="block text-[10px] text-gray-500 uppercase font-bold tracking-widest">Check Out</span>
                    <span className="font-bold text-gray-800">{log.outTime || "--:--"}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
