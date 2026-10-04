"use client";
import { useEffect, useRef, useState } from "react";
import { supabase } from "@/lib/supabase";
import { localdb } from "@/lib/localdb";
import { CheckCircle2, XCircle, ChevronRight, QrCode, ClipboardList } from "lucide-react";

export default function ScannerTab() {
  const [scanResult, setScanResult] = useState<{success: boolean, msg: string} | null>(null);
  const scannerRef = useRef<any>(null);
  const [greeting, setGreeting] = useState("Good Morning!");

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good Morning!");
    else if (hour < 17) setGreeting("Good Afternoon!");
    else setGreeting("Good Evening!");
  }, []);

  useEffect(() => {
    let html5QrCode: any;

    const timer = setTimeout(() => {
      import("html5-qrcode").then(({ Html5Qrcode }) => {
        html5QrCode = new Html5Qrcode("reader");
        
        html5QrCode.start(
          { facingMode: "environment" },
          { 
            fps: 10, 
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0 
          },
          onScanSuccess,
          onScanFailure
        ).then(() => {
          scannerRef.current = html5QrCode;
        }).catch((err: any) => {
          console.error("Camera start failed automatically", err);
        });
      });
    }, 100);

    return () => {
      clearTimeout(timer);
      if (scannerRef.current) {
        try {
          if (scannerRef.current.isScanning) {
            scannerRef.current.stop().then(() => {
              scannerRef.current?.clear();
              scannerRef.current = null;
            }).catch((e: any) => console.error("Failed to stop scanner", e));
          } else {
            scannerRef.current.clear();
            scannerRef.current = null;
          }
        } catch(e: any) {}
      } else if (html5QrCode) {
        try { html5QrCode.clear(); } catch(e: any) {}
      }
    };
  }, []);

  async function onScanSuccess(decodedText: string) {
    if (scannerRef.current) scannerRef.current.pause(true);
    
    try {
      const data = JSON.parse(decodedText);
      const empId = data.empId;
      if (!empId) throw new Error("Invalid format");

      let empData = null;
      let existingRecords: any[] | null = null;
      
      if (navigator.onLine) {
        const { data } = await supabase.from('employees').select('*').eq('empId', empId).single();
        empData = data;
        const { data: existing } = await supabase
          .from('attendance')
          .select('*')
          .eq('date', dateStr)
          .eq('empId', empId)
          .order('inTimestamp', { ascending: true });
        existingRecords = existing;
      } else {
        const cached = localStorage.getItem('cached_employees');
        if (cached) {
          const employees = JSON.parse(cached);
          empData = employees.find((e: any) => e.empId === empId);
        }
        // If offline, check local sync queue for existing IN records today
        const queue = await localdb.syncQueue.where({ empId: empId, date: dateStr }).toArray();
        existingRecords = queue;
      }
      
      if (!empData) {
        setScanResult({ success: false, msg: `Employee ${empId} not found.` });
      } else {
        const emp = empData;
        const today = new Date();
        const dateStr = today.toISOString().split("T")[0];
        const timeStr = today.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        

          
        let lastRecord = existingRecords && existingRecords.length > 0 ? existingRecords[existingRecords.length - 1] : null;

        if (lastRecord && lastRecord.status === 'IN') {
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
        }
      }
    } catch (err: any) {
      setScanResult({ success: false, msg: "Invalid QR Code" });
    }

    setTimeout(() => {
      setScanResult(null);
      if (scannerRef.current) scannerRef.current.resume();
    }, 3000);
  }

  function onScanFailure() { /* ignore */ }

  return (
    <div className="flex flex-col items-center px-4 pt-2 space-y-6">
      
      {/* Greeting Banner */}
      <div className="w-full bg-gradient-to-r from-[#E0EFFF] to-[#E8F3FF] rounded-2xl p-4 flex items-center justify-between shadow-sm border border-blue-50/50">
        <div className="flex items-start space-x-3">
          <span className="text-2xl mt-1">👋</span>
          <div>
            <h2 className="text-[#1E293B] font-bold text-[17px]">{greeting}</h2>
            <p className="text-[#64748B] text-xs mt-0.5">Scan the QR code to mark attendance</p>
          </div>
        </div>
        <div className="w-12 h-12 relative flex-shrink-0">
          <ClipboardList className="w-10 h-10 text-blue-500 opacity-20 absolute -right-2 -bottom-2" />
          <ClipboardList className="w-10 h-10 text-blue-900 absolute right-0 bottom-0" />
        </div>
      </div>

      {/* Main Scanner Container */}
      <div className="relative w-full max-w-[320px] aspect-square rounded-[2rem] p-3 bg-[#EAF3FF] shadow-sm">
        <div className="relative w-full h-full rounded-[1.5rem] overflow-hidden bg-[#161B2E] shadow-inner">
          
          {/* html5-qrcode video container */}
          {/* We use CSS to hide the default UI of html5-qrcode and only show the video */}
          <style dangerouslySetInnerHTML={{__html: `
            #reader { border: none !important; }
            #reader video { object-fit: cover !important; border-radius: 1.5rem; }
            #reader__dashboard_section_csr { display: none !important; }
            #reader__dashboard_section_swaplink { display: none !important; }
            #reader__scan_region { background: transparent !important; }
          `}} />
          
          <div id="reader" className="w-full h-full absolute inset-0 opacity-80 mix-blend-screen"></div>

          {/* Overlay Result Message */}
          {scanResult && (
            <div className="absolute inset-x-0 bottom-4 mx-4 z-20">
              <div className={`p-3 rounded-xl w-full flex items-center justify-center space-x-2 text-white shadow-lg backdrop-blur-md ${scanResult.success ? 'bg-green-600/90' : 'bg-red-500/90'}`}>
                {scanResult.success ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
                <span className="font-semibold text-sm">{scanResult.msg}</span>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Bottom Information Button */}
      <div className="w-full bg-[#EAF3FF] rounded-2xl p-3 flex items-center justify-between shadow-sm cursor-pointer hover:bg-blue-50 transition-colors">
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 rounded-xl bg-blue-500 flex items-center justify-center text-white shadow-md">
            <QrCode size={20} />
          </div>
          <span className="text-[#1E293B] font-medium text-sm">Point camera at employee QR badge</span>
        </div>
        <ChevronRight className="text-gray-400" size={20} />
      </div>

    </div>
  );
}
