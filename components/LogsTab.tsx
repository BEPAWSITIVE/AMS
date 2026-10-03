"use client";
import { useLiveQuery } from "dexie-react-hooks";
import { db } from "@/lib/db";
import { CloudOff, CheckCircle2 } from "lucide-react";

export default function LogsTab() {
  const records = useLiveQuery(() => db.attendance.orderBy('inTimestamp').reverse().toArray());

  return (
    <div className="pb-20 p-4">
      <h2 className="text-lg font-bold text-gray-700 mb-4">Recent Scans</h2>
      
      {records?.length === 0 && (
        <p className="text-center text-gray-500 py-10">No attendance logs yet.</p>
      )}

      <div className="space-y-3">
        {records?.map(rec => (
          <div key={rec.recordId} className="bg-white border rounded-xl p-3 shadow-sm flex flex-col">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-bold text-gray-800">{rec.empName}</h3>
                <p className="text-xs text-gray-500">{rec.date} • {rec.department}</p>
              </div>
              <div className="flex flex-col items-end">
                <span className={`text-xs px-2 py-0.5 rounded font-bold ${rec.isSynced ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'}`}>
                  {rec.isSynced ? <span className="flex items-center gap-1"><CheckCircle2 size={12}/> Synced</span> : <span className="flex items-center gap-1"><CloudOff size={12}/> Pending</span>}
                </span>
                <span className={`text-sm font-bold mt-1 ${rec.status === 'IN' ? 'text-green-600' : 'text-blue-600'}`}>{rec.status}</span>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded p-2 text-sm flex justify-between border">
              <div className="text-green-600 font-medium">In: {rec.inTime}</div>
              <div className="text-blue-600 font-medium">Out: {rec.outTime || '--'}</div>
              <div className="text-gray-500">Total: {rec.totalHours || '--'}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
