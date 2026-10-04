import sys

content = """"use client";
import { Database, CheckCircle2 } from "lucide-react";

export default function SettingsTab() {
  return (
    <div className="p-6 pb-20 max-w-md mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Settings</h2>

      <div className="bg-white p-5 rounded-xl border shadow-sm space-y-4">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-green-100 text-green-600 rounded-lg">
            <Database size={24} />
          </div>
          <div>
            <h3 className="font-bold text-gray-800">Database Connection</h3>
            <p className="text-xs text-green-600 font-medium flex items-center">
              <CheckCircle2 size={14} className="mr-1" /> Connected to Supabase
            </p>
          </div>
        </div>
        
        <p className="text-sm text-gray-500">
          This application is now directly connected to your Supabase PostgreSQL database. 
          All employee and attendance records are synced in real-time.
        </p>
      </div>

      <div className="text-center mt-10">
        <p className="text-xs text-gray-400">Attendance Manager v2.0 (Supabase)</p>
      </div>
    </div>
  );
}
"""
open('components/SettingsTab.tsx', 'w', encoding='utf-8').write(content)
print("Done")
