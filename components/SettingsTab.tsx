"use client";
import { useState, useEffect } from "react";
import { Database, CheckCircle2, Download, CloudOff } from "lucide-react";
import { localdb } from "@/lib/localdb";
import { supabase } from "@/lib/supabase";

export default function SettingsTab() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isOffline, setIsOffline] = useState(false);
  const [pendingSync, setPendingSync] = useState(0);

  useEffect(() => {
    // PWA Install Prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    });

    // Offline Detection
    const checkOffline = () => {
      setIsOffline(!navigator.onLine);
    };
    window.addEventListener('online', checkOffline);
    window.addEventListener('offline', checkOffline);
    checkOffline();

    // Check Sync Queue
    const checkQueue = async () => {
      const attCount = await localdb.syncQueue.count();
      const empCount = await localdb.employeeQueue.count();
      setPendingSync(attCount + empCount);
    };
    checkQueue();
    
    // Auto-sync when coming online
    const handleOnline = async () => {
      checkOffline();
      
      // Sync Employees first
      const emps = await localdb.employeeQueue.toArray();
      if (emps.length > 0) {
        for (const emp of emps) {
          const { error } = await supabase.from('employees').upsert(emp);
          if (!error) await localdb.employeeQueue.delete(emp.empId);
        }
      }
      
      // Sync Attendance
      const records = await localdb.syncQueue.toArray();
      if (records.length > 0) {
        for (const record of records) {
          const { error } = await supabase.from('attendance').upsert(record);
          if (!error) {
            await localdb.syncQueue.delete(record.recordId);
          }
        }
      }
      
      checkQueue();
    };
    window.addEventListener('online', handleOnline);

    return () => {
      window.removeEventListener('online', checkOffline);
      window.removeEventListener('offline', checkOffline);
      window.removeEventListener('online', handleOnline);
    }
  }, []);

  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        setDeferredPrompt(null);
      }
    }
  };

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
        </p>

        {isOffline && (
          <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg flex items-start space-x-2">
            <CloudOff size={18} className="text-orange-500 mt-0.5" />
            <div className="text-sm text-orange-800">
              <p className="font-bold">You are offline.</p>
              <p>Scans will be saved locally and synced automatically when you reconnect.</p>
            </div>
          </div>
        )}

        {pendingSync > 0 && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
            <p className="font-bold">{pendingSync} records waiting to sync.</p>
          </div>
        )}
      </div>

      {deferredPrompt && (
        <button 
          onClick={handleInstallClick}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl font-bold shadow-md flex items-center justify-center transition-colors"
        >
          <Download size={20} className="mr-2" />
          Install App on Phone
        </button>
      )}

      <div className="text-center mt-10">
        <p className="text-xs text-gray-400">Attendance Manager v2.1 (Offline-Ready)</p>
      </div>
    </div>
  );
}
