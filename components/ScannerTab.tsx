"use client";
import { useEffect, useRef, useState } from "react";
import { Html5QrcodeScanner, Html5Qrcode } from "html5-qrcode";
import { db } from "@/lib/db";
import { CheckCircle2, XCircle } from "lucide-react";

export default function ScannerTab() {
  const [scanResult, setScanResult] = useState<{success: boolean, msg: string} | null>(null);
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);

  useEffect(() => {
    if (!scannerRef.current) {
      scannerRef.current = new Html5QrcodeScanner(
        "reader",
        { fps: 10, qrbox: { width: 250, height: 250 } },
        false
      );
      
      scannerRef.current.render(onScanSuccess, onScanFailure);
    }

    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(e => console.error("Failed to clear scanner", e));
        scannerRef.current = null;
      }
    };
  }, []);

  async function onScanSuccess(decodedText: string) {
    if (scannerRef.current) {
      scannerRef.current.pause(true);
    }
    
    try {
      const data = JSON.parse(decodedText);
      const empId = data.empId;
      if (!empId) throw new Error("Invalid QR code format");

      const emp = await db.employees.get(empId);
      if (!emp) {
        setScanResult({ success: false, msg: `Employee ${empId} not found in local database.` });
      } else {
        const today = new Date();
        const dateStr = today.toISOString().split("T")[0];
        const timeStr = today.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        // Find existing record for today
        const existingRecords = await db.attendance
          .where('date').equals(dateStr)
          .and(rec => rec.empId === empId)
          .sortBy('inTimestamp');
          
        let lastRecord = existingRecords.length > 0 ? existingRecords[existingRecords.length - 1] : null;

        if (lastRecord && lastRecord.status === 'IN') {
          // Check out
          const outTimestamp = today.getTime();
          const diffMs = outTimestamp - lastRecord.inTimestamp;
          const hrs = Math.floor(diffMs / 3600000);
          const mins = Math.floor((diffMs % 3600000) / 60000);
          
          await db.attendance.update(lastRecord.recordId, {
            outTime: timeStr,
            outTimestamp: outTimestamp,
            totalHours: `${hrs}h ${mins}m`,
            status: 'OUT',
            isSynced: 0,
            updatedAt: today.toISOString()
          });
          setScanResult({ success: true, msg: `${emp.name} Checked OUT at ${timeStr}` });
        } else {
          // Check in
          await db.attendance.add({
            recordId: crypto.randomUUID(),
            empId: emp.empId,
            empName: emp.name,
            department: emp.department,
            date: dateStr,
            inTime: timeStr,
            inTimestamp: today.getTime(),
            status: 'IN',
            isSynced: 0,
            updatedAt: today.toISOString()
          });
          setScanResult({ success: true, msg: `${emp.name} Checked IN at ${timeStr}` });
        }
      }
    } catch (err) {
      setScanResult({ success: false, msg: "Invalid QR Code" });
    }

    setTimeout(() => {
      setScanResult(null);
      if (scannerRef.current) scannerRef.current.resume();
    }, 3000);
  }

  function onScanFailure(error: any) {
    // ignore
  }

  return (
    <div className="flex flex-col items-center pt-6 space-y-4">
      <div className="w-full max-w-sm rounded-xl overflow-hidden bg-white shadow-lg border border-gray-100 p-2">
        <div id="reader" className="w-full"></div>
      </div>
      
      {scanResult && (
        <div className={`p-4 rounded-lg w-full max-w-sm flex items-center space-x-3 text-white shadow-md ${scanResult.success ? 'bg-green-600' : 'bg-red-500'}`}>
          {scanResult.success ? <CheckCircle2 /> : <XCircle />}
          <span className="font-medium">{scanResult.msg}</span>
        </div>
      )}
      
      <p className="text-gray-500 text-sm text-center px-4">
        Point the camera at an employee's QR badge to record their IN or OUT time.
      </p>
    </div>
  );
}
