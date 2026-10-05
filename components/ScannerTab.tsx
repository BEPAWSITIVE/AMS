"use client";
import { useEffect, useState, useRef } from "react";
import { Html5Qrcode } from "html5-qrcode";
import { supabase, AttendanceRecord, Employee } from "@/lib/supabase";
import { localdb } from "@/lib/localdb";
import { CheckCircle2, AlertCircle, X, Truck } from "lucide-react";

export default function ScannerTab() {
  const [scanResult, setScanResult] = useState<{ success: boolean; msg: string; isVehicle?: boolean } | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  
  const [vehicleModal, setVehicleModal] = useState<{
    profile: Employee;
    lastRecord: AttendanceRecord | null;
  } | null>(null);
  
  const [driverName, setDriverName] = useState("");
  const [meterReading, setMeterReading] = useState("");

  const startScanner = async () => {
    if (isScanning || scannerRef.current) return;
    try {
      const html5QrCode = new Html5Qrcode("reader");
      scannerRef.current = html5QrCode;
      
      await html5QrCode.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        onScanSuccess,
        undefined
      );
      setIsScanning(true);
    } catch (err) {
      console.error("Failed to start scanner", err);
    }
  };

  const stopScanner = async () => {
    if (scannerRef.current && isScanning) {
      try {
        await scannerRef.current.stop();
        scannerRef.current.clear();
        scannerRef.current = null;
        setIsScanning(false);
      } catch (err) {
        console.error("Failed to stop scanner", err);
      }
    }
  };

  useEffect(() => {
    startScanner();
    return () => {
      stopScanner();
    };
  }, []);

  const onScanSuccess = async (decodedText: string) => {
    try {
      const data = JSON.parse(decodedText);
      const empId = data.empId;
      if (!empId) throw new Error("Invalid format");

      // Pause scanner while processing
      if (scannerRef.current) {
        scannerRef.current.pause();
      }

      const today = new Date();
      const dateStr = today.toISOString().split("T")[0];
      const timeStr = today.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      let empData: Employee | null = null;
      let existingRecords: any[] = [];
      
      if (navigator.onLine) {
        const { data: profile } = await supabase.from('employees').select('*').eq('empId', empId).single();
        empData = profile;
        const { data: existing } = await supabase
          .from('attendance')
          .select('*')
          .eq('date', dateStr)
          .eq('empId', empId)
          .order('inTimestamp', { ascending: true });
        if (existing) existingRecords = existing;
      } else {
        const cached = localStorage.getItem('cached_employees');
        if (cached) {
          const employees = JSON.parse(cached);
          empData = employees.find((e: any) => e.empId === empId);
        }
        const queue = await localdb.syncQueue.where({ empId: empId, date: dateStr }).toArray();
        existingRecords = queue;
      }
      
      if (!empData) {
        setScanResult({ success: false, msg: `Profile ${empId} not found.` });
        setTimeout(() => {
          setScanResult(null);
          if (scannerRef.current) scannerRef.current.resume();
        }, 3000);
        return;
      }

      const emp = empData;
      let lastRecord = existingRecords.length > 0 ? existingRecords[existingRecords.length - 1] : null;

      if (emp.category === 'Vehicle') {
        // Vehicle Flow - open modal
        setVehicleModal({ profile: emp, lastRecord });
        return; // wait for user input
      }

      // Standard Staff / Visitor Flow
      if (lastRecord && lastRecord.status === 'IN') {
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
        const newRecord = {
          recordId: crypto.randomUUID(),
          empId: emp.empId,
          empName: emp.name,
          department: emp.department,
          category: emp.category,
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

      setTimeout(() => {
        setScanResult(null);
        if (scannerRef.current) scannerRef.current.resume();
      }, 2500);

    } catch (err) {
      if (scannerRef.current) scannerRef.current.resume();
    }
  };

  const handleVehicleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!vehicleModal) return;
    
    const { profile, lastRecord } = vehicleModal;
    const isDispatching = !lastRecord || lastRecord.status === 'OUT'; // Vehicle is at base, now leaving
    
    const today = new Date();
    const dateStr = today.toISOString().split("T")[0];
    const timeStr = today.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (isDispatching) {
      // Create new OUT record (Trip Started)
      // Note: We use status='IN' to mean 'Trip Active' to match our logic where IN means active session
      const newRecord = {
        recordId: crypto.randomUUID(),
        empId: profile.empId,
        empName: profile.name,
        department: profile.department,
        category: profile.category,
        date: dateStr,
        inTime: timeStr,
        inTimestamp: today.getTime(),
        status: 'IN', // 'IN' means actively on a trip
        driver_name: driverName,
        meter_out: parseFloat(meterReading),
        isSynced: navigator.onLine ? 1 : 0,
        updatedAt: today.toISOString()
      };

      if (navigator.onLine) {
        await supabase.from('attendance').insert([newRecord]);
      } else {
        await localdb.syncQueue.put(newRecord);
      }
      setScanResult({ success: true, isVehicle: true, msg: `Vehicle ${profile.name} Dispatched by ${driverName}` + (navigator.onLine ? '' : ' (Offline)') });
    } else {
      // Vehicle is returning (Trip Complete)
      const meterOut = lastRecord.meter_out || 0;
      const meterIn = parseFloat(meterReading);
      const consumed = meterIn >= meterOut ? meterIn - meterOut : 0;
      
      const updatedRecord = {
        ...lastRecord,
        outTime: timeStr,
        outTimestamp: today.getTime(),
        meter_in: meterIn,
        totalHours: `${consumed} units consumed`,
        status: 'OUT', // 'OUT' means trip finished (back at base)
        isSynced: navigator.onLine ? 1 : 0,
        updatedAt: today.toISOString()
      };

      if (navigator.onLine) {
        await supabase.from('attendance').update(updatedRecord).eq('recordId', lastRecord.recordId);
      } else {
        await localdb.syncQueue.put(updatedRecord);
      }
      setScanResult({ success: true, isVehicle: true, msg: `Vehicle ${profile.name} Returned. ${consumed} units used.` + (navigator.onLine ? '' : ' (Offline)') });
    }

    setVehicleModal(null);
    setDriverName("");
    setMeterReading("");
    
    setTimeout(() => {
      setScanResult(null);
      if (scannerRef.current) scannerRef.current.resume();
    }, 3000);
  };

  const cancelVehicleScan = () => {
    setVehicleModal(null);
    setDriverName("");
    setMeterReading("");
    if (scannerRef.current) scannerRef.current.resume();
  };

  return (
    <div className="relative h-screen bg-black overflow-hidden">
      
      {/* Scanner Viewport */}
      <div className="absolute inset-0 z-0 flex items-center justify-center">
        <div id="reader" className="w-full h-full [&>video]:object-cover"></div>
        
        {/* Safe Area Overlay for aesthetic */}
        <div className="absolute inset-0 border-[40px] border-black/40 pointer-events-none"></div>
      </div>

      {/* Result Toast */}
      {scanResult && !vehicleModal && (
        <div className="absolute top-8 left-0 right-0 px-4 z-20 flex justify-center animate-bounce-in">
          <div className={`px-5 py-4 rounded-2xl shadow-2xl flex items-center space-x-3 w-full max-w-sm
            ${scanResult.success 
              ? (scanResult.isVehicle ? 'bg-amber-500 text-white' : 'bg-emerald-500 text-white')
              : 'bg-red-500 text-white'}`}>
            {scanResult.success 
              ? (scanResult.isVehicle ? <Truck size={24} /> : <CheckCircle2 size={24} />) 
              : <AlertCircle size={24} />}
            <span className="font-bold">{scanResult.msg}</span>
          </div>
        </div>
      )}

      {/* Vehicle Action Modal */}
      {vehicleModal && (
        <div className="absolute inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white w-full max-w-sm rounded-3xl overflow-hidden shadow-2xl relative">
            <div className="bg-amber-500 p-6 text-white text-center">
              <Truck size={40} className="mx-auto mb-2 opacity-90" />
              <h3 className="text-xl font-bold">{vehicleModal.profile.name}</h3>
              <p className="opacity-80 text-sm font-mono mt-1">{vehicleModal.profile.vehicle_plate}</p>
            </div>
            
            <form onSubmit={handleVehicleSubmit} className="p-6 space-y-4">
              {(!vehicleModal.lastRecord || vehicleModal.lastRecord.status === 'OUT') ? (
                <>
                  <div className="bg-amber-50 text-amber-800 p-3 rounded-lg text-sm font-bold text-center mb-2">
                    Dispatching Vehicle (Leaving Base)
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Driver Name *</label>
                    <input 
                      type="text" 
                      value={driverName}
                      onChange={e => setDriverName(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-amber-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Current Meter Reading *</label>
                    <input 
                      type="number" 
                      step="any"
                      value={meterReading}
                      onChange={e => setMeterReading(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-amber-500 font-mono"
                      required
                    />
                  </div>
                </>
              ) : (
                <>
                  <div className="bg-emerald-50 text-emerald-800 p-3 rounded-lg text-sm font-bold text-center mb-2">
                    Returning Vehicle (Arriving at Base)
                  </div>
                  <div className="text-center text-sm text-gray-500 mb-4">
                    Dispatched by: <span className="font-bold text-gray-800">{vehicleModal.lastRecord.driver_name}</span><br/>
                    Previous Meter: <span className="font-mono font-bold text-gray-800">{vehicleModal.lastRecord.meter_out}</span>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Return Meter Reading *</label>
                    <input 
                      type="number" 
                      step="any"
                      value={meterReading}
                      onChange={e => setMeterReading(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-emerald-500 font-mono"
                      required
                    />
                  </div>
                </>
              )}

              <div className="flex space-x-3 pt-2">
                <button 
                  type="button" 
                  onClick={cancelVehicleScan}
                  className="flex-1 bg-gray-100 text-gray-600 py-3 rounded-xl font-bold"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="flex-1 bg-amber-500 hover:bg-amber-600 text-white py-3 rounded-xl font-bold shadow-md"
                >
                  Confirm
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Persistent Bottom UI */}
      <div className="absolute bottom-24 left-0 right-0 px-6">
        <div className="bg-white/10 backdrop-blur-md border border-white/20 p-4 rounded-2xl text-center shadow-lg">
          <p className="text-white font-bold tracking-wide">Ready to Scan</p>
          <p className="text-white/60 text-sm mt-1">Point camera at ID card</p>
        </div>
      </div>
    </div>
  );
}
