"use client";
import { useState, useEffect } from "react";
import { useLiveQuery } from "dexie-react-hooks";
import { db } from "@/lib/db";
import { CloudUpload, Save } from "lucide-react";

export default function SettingsTab() {
  const [url, setUrl] = useState("");
  const [isSyncing, setIsSyncing] = useState(false);
  const pendingCount = useLiveQuery(() => db.attendance.where('isSynced').equals(0).count()) || 0;

  useEffect(() => {
    setUrl(localStorage.getItem("webhook_url") || "");
  }, []);

  function saveUrl() {
    localStorage.setItem("webhook_url", url);
    alert("Webhook URL saved!");
  }

  async function syncRecords() {
    if (!url) {
      alert("Please save a Webhook URL first.");
      return;
    }
    
    setIsSyncing(true);
    try {
      const pending = await db.attendance.where('isSynced').equals(0).toArray();
      if (pending.length === 0) {
        alert("No pending records to sync.");
        setIsSyncing(false);
        return;
      }

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "sync_batch", records: pending })
      });

      const result = await response.json();
      if (result.success) {
        // Mark all as synced
        for (const rec of pending) {
          await db.attendance.update(rec.recordId, { isSynced: 1 });
        }
        alert("Sync successful!");
      } else {
        alert("Server rejected sync: " + result.error);
      }
    } catch (err: any) {
      alert("Sync failed: " + err.message);
    }
    setIsSyncing(false);
  }

  async function loadSampleData() {
    await db.employees.bulkPut([
      { empId: "EMP001", name: "Alice Smith", department: "Engineering", phone: "555-0101", createdAt: new Date().toISOString() },
      { empId: "EMP002", name: "Bob Jones", department: "Security", phone: "555-0102", createdAt: new Date().toISOString() },
    ]);
    alert("Samples loaded.");
  }

  return (
    <div className="pb-20 p-4 space-y-6">
      
      <div className="bg-white p-4 rounded-xl shadow-sm border">
        <h2 className="text-lg font-bold text-gray-800 mb-2">Google Sheet Webhook</h2>
        <p className="text-sm text-gray-500 mb-3">Enter the Apps Script deployment URL to sync records to your Google Sheet.</p>
        <input 
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://script.google.com/macros/s/.../exec"
          className="w-full border rounded p-2 mb-3 text-sm text-gray-800"
        />
        <button onClick={saveUrl} className="w-full bg-blue-600 text-white rounded p-2 flex items-center justify-center font-bold shadow">
          <Save size={18} className="mr-2" /> Save URL
        </button>
      </div>

      <div className="bg-white p-4 rounded-xl shadow-sm border">
        <h2 className="text-lg font-bold text-gray-800 mb-2">Offline Sync Queue</h2>
        <div className="flex justify-between items-center mb-4 border-b pb-3">
          <span className="text-sm text-gray-600">Pending Records:</span>
          <span className={`font-bold ${pendingCount > 0 ? 'text-orange-600' : 'text-green-600'}`}>{pendingCount}</span>
        </div>
        
        <button 
          onClick={syncRecords} 
          disabled={isSyncing || pendingCount === 0}
          className="w-full bg-green-600 text-white rounded p-2 flex items-center justify-center font-bold shadow disabled:opacity-50"
        >
          <CloudUpload size={18} className="mr-2" /> 
          {isSyncing ? "Syncing..." : "Sync Pending Records Now"}
        </button>
      </div>

      <button onClick={loadSampleData} className="w-full text-blue-600 p-3 border border-blue-200 rounded-xl bg-blue-50 font-medium">
        Load Sample Employees
      </button>

    </div>
  );
}
