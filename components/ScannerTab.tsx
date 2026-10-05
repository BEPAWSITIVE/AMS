"use client";
import { useEffect, useState, useRef } from "react";
import { Html5Qrcode } from "html5-qrcode";
import { supabase, AttendanceRecord, Employee } from "@/lib/supabase";
import { localdb } from "@/lib/localdb";
import { CheckCircle2, AlertCircle, X, Truck, Package } from "lucide-react";

export default function ScannerTab() {
  const [scanResult, setScanResult] = useState<{ success: boolean; msg: string; isVehicle?: boolean } | null>(null);
  const [parcelModal, setParcelModal] = useState<{ profile: Employee; lastRecord: AttendanceRecord } | null>(null);
  const [pickerName, setPickerName] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  
  const [vehicleModal, setVehicleModal] = useState<{
    profile: Employee;
    lastRecord: AttendanceRecord | null;
  } | null>(null);
  const [parcelModal, setParcelModal] = useState<{ profile: Employee; lastRecord: AttendanceRecord } | null>(null);
  const [pickerName, setPickerName] = useState("");
  
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
    if (cameraActive) {
      startScanner();
    } else {
      stopScanner();
    }
    return () => {
      stopScanner();
    };
  }, [cameraActive]);

  const onScanSuccess = async (decodedText: string) => {
    try {
      const data = JSON.parse(decodedText);
      const empId = data.empId;
      if (!empId) throw new Error("Invalid format");

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
        setVehicleModal({ profile: emp, lastRecord });
        return; 
      }
      
      if (emp.category === 'Parcel' && lastRecord && lastRecord.status === 'IN') {
        setParcelModal({ profile: emp, lastRecord });
        return;
      }

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
    const isDispatching = !lastRecord || lastRecord.status === 'OUT'; 
    
    const today = new Date();
    const dateStr = today.toISOString().split("T")[0];
    const timeStr = today.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (isDispatching) {
      const newRecord = {
        recordId: crypto.randomUUID(),
        empId: profile.empId,
        empName: profile.name,
        department: profile.department,
        category: profile.category,
        date: dateStr,
        inTime: timeStr,
        inTimestamp: today.getTime(),
        status: 'IN',
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
      const meterOut = lastRecord.meter_out || 0;
      const meterIn = parseFloat(meterReading);
      const consumed = meterIn >= meterOut ? meterIn - meterOut : 0;
      
      const updatedRecord = {
        ...lastRecord,
        outTime: timeStr,
        outTimestamp: today.getTime(),
        meter_in: meterIn,
        totalHours: `${consumed} units consumed`,
        status: 'OUT',
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

    const handleParcelSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!parcelModal) return;
    
    const { profile, lastRecord } = parcelModal;
    const today = new Date();
    const timeStr = today.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const updatedRecord = {
      ...lastRecord,
      outTime: timeStr,
      outTimestamp: today.getTime(),
      driver_name: pickerName, // Overload driver_name to store picker name
      status: 'OUT',
      isSynced: navigator.onLine ? 1 : 0,
      updatedAt: today.toISOString()
    };

    if (navigator.onLine) {
      await supabase.from('attendance').update(updatedRecord).eq('recordId', lastRecord.recordId);
    } else {
      await localdb.syncQueue.put(updatedRecord);
    }
    
    setScanResult({ success: true, msg: `Parcel picked up by ${pickerName}` + (navigator.onLine ? '' : ' (Offline)') });
    setParcelModal(null);
    setPickerName("");
    
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
    <div className="w-full h-full flex flex-col relative bg-transparent">
      
      {/* Background decorations for empty state */}
      {!cameraActive && (
        <>
          <div className="fixed bottom-32 -left-6 opacity-80 pointer-events-none z-0">
            <svg width="120" height="150" viewBox="0 0 100 150" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 150C10 100 40 70 80 50" stroke="#34D399" strokeWidth="4" strokeLinecap="round" />
              <path d="M40 100C30 80 15 70 0 70C15 90 20 100 40 100Z" fill="#34D399" />
              <path d="M60 70C50 50 35 40 20 40C35 60 40 70 60 70Z" fill="#34D399" />
              <path d="M80 50C70 30 55 20 40 20C55 40 60 50 80 50Z" fill="#10B981" />
            </svg>
          </div>
          <div className="fixed bottom-40 -left-4 w-20 h-12 bg-blue-100 rounded-full opacity-60 mix-blend-multiply blur-sm z-0"></div>
        </>
      )}

      {/* Main Scanner Container */}
      <div className={`flex-1 flex flex-col items-center justify-center ${cameraActive ? 'bg-black fixed inset-0 z-[100]' : 'z-10'}`}>
        
        {cameraActive && (
          <div className="absolute top-12 right-6 z-50">
            <button 
              onClick={() => setCameraActive(false)}
              className="bg-white/20 backdrop-blur-md p-3 rounded-full text-white hover:bg-white/30 transition-colors shadow-lg border border-white/10"
            >
              <X size={24} />
            </button>
          </div>
        )}

        {/* Scanner Viewport */}
        <div className={`${cameraActive ? 'absolute inset-0 flex items-center justify-center z-0' : 'hidden'}`}>
          <div id="reader" className="w-full h-full [&>video]:object-cover"></div>
          {cameraActive && <div className="absolute inset-0 border-[40px] border-black/40 pointer-events-none"></div>}
        </div>

        {/* Empty State / Button */}
        {!cameraActive && (
          <div className="absolute bottom-6 left-0 right-0 px-6 animate-fade-in z-20">
            <button 
              onClick={() => setCameraActive(true)}
              className="w-full bg-[#EAF3FF] hover:bg-[#dce9fa] transition-colors py-4 px-4 rounded-[20px] flex items-center justify-between shadow-sm"
            >
              <div className="flex items-center">
                <div className="bg-[#3B82F6] text-white p-2.5 rounded-xl mr-4 shadow-sm">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><rect x="7" y="7" width="3" height="3"></rect><rect x="14" y="7" width="3" height="3"></rect><rect x="7" y="14" width="3" height="3"></rect><rect x="14" y="14" width="3" height="3"></rect></svg>
                </div>
                <span className="text-[#1E293B] font-bold text-[13px]">Point camera at employee QR badge</span>
              </div>
              <div className="text-[#3B82F6]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
              </div>
            </button>
          </div>
        )}
      </div>

      {/* Result Toast */}
      {scanResult && !vehicleModal && (
        <div className="fixed top-8 left-0 right-0 px-4 z-[110] flex justify-center animate-bounce-in">
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

            {/* Parcel Action Modal */}
      {parcelModal && (
        <div className="fixed inset-0 z-[120] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white w-full max-w-sm rounded-3xl overflow-hidden shadow-2xl relative">
            <div className="bg-purple-500 p-6 text-white text-center">
              <Package size={40} className="mx-auto mb-2 opacity-90" />
              <h3 className="text-xl font-bold">{parcelModal.profile.name}</h3>
              <p className="opacity-80 text-sm font-mono mt-1">{parcelModal.profile.empId}</p>
            </div>
            
            <form onSubmit={handleParcelSubmit} className="p-6 space-y-4">
              <div className="bg-purple-50 text-purple-800 p-3 rounded-lg text-sm font-bold text-center mb-2">
                Parcel Pickup Authorization
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">Name of Person Picking Up *</label>
                <input 
                  type="text" 
                  value={pickerName}
                  onChange={e => setPickerName(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>

              <div className="flex space-x-3 pt-2">
                <button 
                  type="button" 
                  onClick={() => { setParcelModal(null); setPickerName(""); if (scannerRef.current) scannerRef.current.resume(); }}
                  className="flex-1 bg-gray-100 text-gray-600 py-3 rounded-xl font-bold"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="flex-1 bg-purple-500 hover:bg-purple-600 text-white py-3 rounded-xl font-bold shadow-md"
                >
                  Confirm Pickup
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Vehicle Action Modal */}
      {vehicleModal && (
        <div className="fixed inset-0 z-[120] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
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
    </div>
  );
}
