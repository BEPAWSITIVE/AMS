"use client";
import { useState, useEffect } from "react";
import { Database, CheckCircle2, Download, CloudOff, Info, Share, PlusSquare } from "lucide-react";
import { localdb } from "@/lib/localdb";
import { supabase } from "@/lib/supabase";

export default function SettingsTab() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isOffline, setIsOffline] = useState(false);
  const [pendingSync, setPendingSync] = useState(0);
  const [showIosInstructions, setShowIosInstructions] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Check if installed
    if (window.matchMedia('(display-mode: standalone)').matches || (window.navigator as any).standalone === true) {
      setIsStandalone(true);
    }
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
    
    const handleOnline = async () => {
      checkOffline();
      
      // Sync Employees first
      const emps = await localdb.employeeQueue.toArray();
      if (emps.length > 0) {
        for (const emp of emps) {
          const { error } = await supabase.from('employees').upsert(emp);
          if (!error) {
            await localdb.employeeQueue.delete(emp.empId);
          } else {
            console.error("Sync emp error:", error);
          }
        }
      }
      
      // Sync Attendance
      const records = await localdb.syncQueue.toArray();
      if (records.length > 0) {
        for (const record of records) {
          const { error } = await supabase.from('attendance').upsert(record);
          if (!error) {
            await localdb.syncQueue.delete(record.recordId);
          } else {
            console.error("Sync attendance error:", error);
          }
        }
      }
      
      checkQueue();
    };
    
    // Auto-sync immediately if online on mount
    if (navigator.onLine) {
      handleOnline();
    }
    
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
        setIsStandalone(true);
      }
    } else {
      setShowIosInstructions(true);
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
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm flex items-center justify-between">
            <span className="font-bold text-blue-800">{pendingSync} records waiting to sync.</span>
            <button 
              onClick={() => {
                if (navigator.onLine) {
                  // Re-trigger the same sync logic manually
                  const event = new Event('online');
                  window.dispatchEvent(event);
                } else {
                  alert("You are still offline!");
                }
              }}
              className="bg-blue-600 text-white px-3 py-1.5 rounded-lg font-medium text-xs shadow-sm hover:bg-blue-700"
            >
              Sync Now
            </button>
          </div>
        )}
      </div>

      {!isStandalone ? (
        <button 
          onClick={handleInstallClick}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl font-bold shadow-md flex items-center justify-center transition-colors active:scale-95"
        >
          <Download size={20} className="mr-2" />
          Download App to Home Screen
        </button>
      ) : (
        <div className="w-full bg-green-50 text-green-700 border border-green-200 p-4 rounded-xl font-bold flex items-center justify-center">
          <CheckCircle2 size={20} className="mr-2" />
          App Successfully Installed
        </div>
      )}

      {showIosInstructions && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl relative mt-4">
          <button onClick={() => setShowIosInstructions(false)} className="absolute top-2 right-2 text-blue-400 hover:text-blue-600">×</button>
          <h4 className="font-bold text-blue-900 flex items-center mb-2"><Info size={18} className="mr-2" /> Apple iOS Instructions</h4>
          <p className="text-sm text-blue-800 mb-3">To install this app on your iPhone or iPad, please follow these 2 quick steps:</p>
          <ol className="text-sm text-blue-800 space-y-2 ml-1">
            <li className="flex items-center">1. Tap the <Share size={16} className="mx-2 bg-white p-0.5 rounded shadow-sm text-blue-600" /> Share icon at the bottom of Safari.</li>
            <li className="flex items-center">2. Scroll down and tap <PlusSquare size={16} className="mx-2 text-gray-700" /> <b>Add to Home Screen</b>.</li>
          </ol>
        </div>
      )}

      <div className="text-center mt-10">
        <p className="text-xs text-gray-400">Attendance Manager v2.1 (Offline-Ready)</p>
      </div>
    </div>
  );
}
