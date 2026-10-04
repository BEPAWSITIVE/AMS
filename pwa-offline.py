import os

# 1. Create manifest.json
manifest = """{
  "name": "Attendance Manager",
  "short_name": "Attendance",
  "description": "Employee Attendance Manager",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#F4F9FF",
  "theme_color": "#3B82F6",
  "icons": [
    {
      "src": "/logo.jpg",
      "sizes": "192x192",
      "type": "image/jpeg"
    },
    {
      "src": "/logo.jpg",
      "sizes": "512x512",
      "type": "image/jpeg"
    }
  ]
}
"""
with open('public/manifest.json', 'w') as f:
    f.write(manifest)

# 2. Create sw.js
sw = """
self.addEventListener('install', (e) => {
  self.skipWaiting();
});
self.addEventListener('activate', (e) => {
  return self.clients.claim();
});
self.addEventListener('fetch', (e) => {
  // Simple pass-through fetch for now
});
"""
with open('public/sw.js', 'w') as f:
    f.write(sw)

# 3. Update app/layout.tsx
layout = open('app/layout.tsx', 'r').read()
if '<link rel="manifest"' not in layout:
    # insert before </head>
    # If no head, just put it inside html or add head.
    # Actually Next.js App router handles metadata differently, we can just add a manifest.json to the app root or public folder. Next.js 14 auto-detects it or we can add it to metadata.
    # We will inject a Script in the body to register the SW.
    layout = layout.replace('</body>', """
        <script dangerouslySetInnerHTML={{__html: `
          if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
              navigator.serviceWorker.register('/sw.js').then(function(registration) {
                console.log('ServiceWorker registration successful');
              }, function(err) {
                console.log('ServiceWorker registration failed: ', err);
              });
            });
          }
        `}} />
      </body>""")
    open('app/layout.tsx', 'w').write(layout)


# 4. Update SettingsTab.tsx
settings = """"use client";
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
      const count = await localdb.syncQueue.count();
      setPendingSync(count);
    };
    checkQueue();
    
    // Auto-sync when coming online
    const handleOnline = async () => {
      checkOffline();
      const records = await localdb.syncQueue.toArray();
      if (records.length > 0) {
        // Simple sync: push all records
        for (const record of records) {
          const { error } = await supabase.from('attendance').upsert(record);
          if (!error) {
            await localdb.syncQueue.delete(record.recordId);
          }
        }
        checkQueue();
      }
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
"""
with open('components/SettingsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(settings)

# 5. Update ScannerTab.tsx with offline capability
scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()
if "localdb" not in scanner:
    scanner = scanner.replace('import { supabase } from "@/lib/supabase";', 'import { supabase } from "@/lib/supabase";\nimport { localdb } from "@/lib/localdb";')
    
    # We replace the checking/checkout logic.
    old_logic = """        if (lastRecord && lastRecord.status === 'IN') {
          // Check out
          const outTimestamp = today.getTime();
          const diffMs = outTimestamp - lastRecord.inTimestamp;
          const hrs = Math.floor(diffMs / 3600000);
          const mins = Math.floor((diffMs % 3600000) / 60000);
          
          await supabase.from('attendance').update({
            outTime: timeStr,
            outTimestamp: outTimestamp,
            totalHours: `${hrs}h ${mins}m`,
            status: 'OUT',
            isSynced: 1,
            updatedAt: today.toISOString()
          }).eq('recordId', lastRecord.recordId);
          
          setScanResult({ success: true, msg: `${emp.name} Checked OUT at ${timeStr}` });
        } else {
          // Check in
          await supabase.from('attendance').insert([{
            empId: emp.empId,
            empName: emp.name,
            department: emp.department,
            date: dateStr,
            inTime: timeStr,
            inTimestamp: today.getTime(),
            status: 'IN',
            isSynced: 1,
            updatedAt: today.toISOString()
          }]);
          
          setScanResult({ success: true, msg: `${emp.name} Checked IN at ${timeStr}` });
        }"""
        
    new_logic = """        if (lastRecord && lastRecord.status === 'IN') {
          // Check out
          const outTimestamp = today.getTime();
          const diffMs = outTimestamp - lastRecord.inTimestamp;
          const hrs = Math.floor(diffMs / 3600000);
          const mins = Math.floor((diffMs % 3600000) / 60000);
          
          const updatedRecord = {
            ...lastRecord,
            outTime: timeStr,
            outTimestamp: outTimestamp,
            totalHours: `${hrs}h ${mins}m`,
            status: 'OUT',
            isSynced: navigator.onLine ? 1 : 0,
            updatedAt: today.toISOString()
          };

          if (navigator.onLine) {
            await supabase.from('attendance').update(updatedRecord).eq('recordId', lastRecord.recordId);
          } else {
            await localdb.syncQueue.put(updatedRecord);
          }
          
          setScanResult({ success: true, msg: `${emp.name} Checked OUT at ${timeStr}` + (navigator.onLine ? '' : ' (Offline)') });
        } else {
          // Check in
          const newRecord = {
            recordId: crypto.randomUUID(),
            empId: emp.empId,
            empName: emp.name,
            department: emp.department,
            date: dateStr,
            inTime: timeStr,
            inTimestamp: today.getTime(),
            status: 'IN',
            isSynced: navigator.onLine ? 1 : 0,
            updatedAt: today.toISOString()
          };

          if (navigator.onLine) {
            await supabase.from('attendance').insert([newRecord]);
          } else {
            await localdb.syncQueue.put(newRecord);
          }
          
          setScanResult({ success: true, msg: `${emp.name} Checked IN at ${timeStr}` + (navigator.onLine ? '' : ' (Offline)') });
        }"""
    
    scanner = scanner.replace(old_logic, new_logic)
    with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
        f.write(scanner)

print("Done")
