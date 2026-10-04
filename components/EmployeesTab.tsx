"use client";
import { useState, useEffect } from "react";
import { supabase, Employee } from "@/lib/supabase";
import { localdb } from "@/lib/localdb";
import { QRCodeCanvas } from "qrcode.react";
import { MessageCircle, X } from "lucide-react";

export default function EmployeesTab() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  
  const [empId, setEmpId] = useState("");
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [phone, setPhone] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);

  useEffect(() => {
    fetchEmployees();
    
    const channel = supabase
      .channel('employees_changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'employees' },
        (payload) => {
          fetchEmployees();
        }
      )
      .subscribe();

    const interval = setInterval(() => {
      if (navigator.onLine) fetchEmployees();
    }, 30000);

    return () => {
      supabase.removeChannel(channel);
      clearInterval(interval);
    };
  }, []);

  async function fetchEmployees() {
    let allEmps: Employee[] = [];
    if (navigator.onLine) {
      const { data, error } = await supabase.from('employees').select('*').order('createdAt', { ascending: false });
      if (!error && data) {
        allEmps = data;
        localStorage.setItem('cached_employees', JSON.stringify(data));
      }
    } else {
      const cached = localStorage.getItem('cached_employees');
      if (cached) allEmps = JSON.parse(cached);
    }
    
    // Merge any offline queued employees that might not be synced yet
    const queuedEmps = await localdb.employeeQueue.toArray();
    const merged = [...queuedEmps, ...allEmps].reduce((acc, curr) => {
      if (!acc.find(item => item.empId === curr.empId)) acc.push(curr);
      return acc;
    }, [] as Employee[]);
    
    merged.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    setEmployees(merged);
    setLoading(false);
  }

  function generateCardCanvas(qrCanvas: HTMLCanvasElement, employee: any): HTMLCanvasElement {
    const canvas = document.createElement("canvas");
    canvas.width = 600;
    canvas.height = 800;
    const ctx = canvas.getContext("2d")!;
    
    // Background
    ctx.fillStyle = "#F4F9FF";
    ctx.fillRect(0, 0, 600, 800);
    
    // Card Shadow
    ctx.shadowColor = "rgba(0, 0, 0, 0.08)";
    ctx.shadowBlur = 30;
    ctx.shadowOffsetY = 10;
    
    // Card Body
    ctx.fillStyle = "#FFFFFF";
    // Rounded rect
    const x = 40, y = 40, w = 520, h = 720, r = 32;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    ctx.fill();
    
    // Reset shadow for text/images
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
    ctx.shadowOffsetY = 0;
    
    ctx.textAlign = "center";
    
    // Header
    ctx.fillStyle = "#3B82F6";
    ctx.font = "bold 20px sans-serif";
    ctx.letterSpacing = "2px";
    ctx.fillText("ATTENDANCE PASS", 300, 120);
    
    // Name
    ctx.fillStyle = "#1E293B";
    ctx.font = "bold 46px sans-serif";
    ctx.fillText(employee.name, 300, 190);
    
    // Department & ID
    ctx.fillStyle = "#64748B";
    ctx.font = "24px sans-serif";
    ctx.fillText(`${employee.department} - ${employee.empId}`, 300, 240);
    
    // Draw QR
    // QR size is 320x320
    const qrSize = 340;
    ctx.drawImage(qrCanvas, 300 - qrSize/2, 290, qrSize, qrSize);
    
    // Footer
    ctx.fillStyle = "#94A3B8";
    ctx.font = "18px sans-serif";
    ctx.fillText("Scan this code at the entrance to mark attendance", 300, 700);
    
    // Logo text at very bottom
    ctx.fillStyle = "#CBD5E1";
    ctx.font = "bold 16px sans-serif";
    ctx.fillText("Attendance Manager", 300, 740);

    return canvas;
  }

  function handleOpenForm() {
    const newId = "EMP-" + Math.random().toString(36).substring(2, 6).toUpperCase();
    setEmpId(newId);
    setShowForm(true);
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!empId || !name) return;
    
    const newEmp = {
      empId, name, department, phone, createdAt: new Date().toISOString()
    };
    
    if (navigator.onLine) {
      try {
        const { error } = await supabase.from('employees').insert([newEmp]);
        if (error) throw error;
      } catch (err: any) {
        alert("Error adding employee: " + err.message);
        return;
      }
    } else {
      // Save locally if offline
      await localdb.employeeQueue.put(newEmp);
      // Also update the cached list so they show up immediately
      const cached = localStorage.getItem('cached_employees');
      const currentList = cached ? JSON.parse(cached) : [];
      currentList.unshift(newEmp);
      localStorage.setItem('cached_employees', JSON.stringify(currentList));
    }
    
    setShowForm(false);
    setEmpId(""); setName(""); setDepartment(""); setPhone("");
    fetchEmployees();
  }

  async function handleDelete(id: string) {
    if(confirm("Delete this employee?")) {
      await supabase.from('employees').delete().eq('empId', id);
      fetchEmployees();
    }
  }

  return (
    <div className="pb-20">
      {showForm ? (
        <div className="p-4 bg-white rounded-xl shadow-md border m-4">
          <h2 className="text-xl font-bold mb-4">Register Employee</h2>
          <form onSubmit={handleAdd} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-500 mb-1">Employee ID *</label>
              <input required value={empId} readOnly className="w-full border rounded p-2 bg-gray-50 text-gray-500 font-mono" />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Full Name *</label>
              <input required value={name} onChange={e=>setName(e.target.value)} className="w-full border rounded p-2" />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Department</label>
              <input value={department} onChange={e=>setDepartment(e.target.value)} className="w-full border rounded p-2" />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">WhatsApp Phone (Optional)</label>
              <input value={phone} onChange={e=>setPhone(e.target.value)} placeholder="+1234567890" className="w-full border rounded p-2" />
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-500">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded shadow">Save</button>
            </div>
          </form>
        </div>
      ) : (
        <>
          <div className="p-4 flex justify-between items-center">
            <h2 className="text-lg font-bold text-gray-700">Staff List</h2>
            <button onClick={handleOpenForm} className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm shadow">
              + Add Employee
            </button>
          </div>
          
          <div className="px-4 space-y-3">
            {loading ? (
               <p className="text-center text-gray-500 py-10">Loading...</p>
            ) : employees.length === 0 ? (
              <p className="text-center text-gray-500 py-10">No employees found. Add one to generate a QR code.</p>
            ) : (
              employees.map(emp => (
                <div key={emp.empId} className="bg-white p-3 rounded-lg border shadow-sm flex justify-between items-center">
                  <div>
                    <h3 className="font-bold text-gray-800">{emp.name}</h3>
                    <p className="text-sm text-gray-500">{emp.empId} - {emp.department}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button onClick={() => setSelectedEmployee(emp)} className="bg-blue-50 text-blue-600 px-3 py-1.5 rounded text-sm font-medium">
                      Show QR
                    </button>
                    <button onClick={() => handleDelete(emp.empId)} className="text-red-400 p-1.5 hover:bg-red-50 rounded-full transition-colors">
                      <X size={18} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}

      {selectedEmployee && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white p-6 rounded-2xl w-full max-w-xs flex flex-col items-center relative shadow-xl">
            <button onClick={() => setSelectedEmployee(null)} className="absolute top-3 right-4 text-gray-400 hover:text-gray-600 text-xl font-bold">
              <X size={20} />
            </button>
            
            <h3 className="font-bold text-blue-600 mb-1 tracking-widest text-sm">ATTENDANCE PASS</h3>
            <p className="text-gray-800 font-bold text-lg mb-4">{selectedEmployee.name}</p>
            
            <div className="p-2 bg-white border-2 border-gray-100 rounded-xl mb-4">
              <QRCodeCanvas 
                id="qr-canvas" 
                value={JSON.stringify({ empId: selectedEmployee.empId, name: selectedEmployee.name })} 
                size={200} 
              />
            </div>
            
            <button 
              onClick={() => {
                const qrCanvas = document.getElementById("qr-canvas") as HTMLCanvasElement;
                if (!qrCanvas) return;
                
                const cardCanvas = generateCardCanvas(qrCanvas, selectedEmployee);
                
                cardCanvas.toBlob(async (blob) => {
                  if (!blob) return;
                  const file = new File([blob], `${selectedEmployee.name.replace(/\s+/g, '_')}_Pass.png`, { type: "image/png" });
                  
                  const useDirectWhatsApp = selectedEmployee.phone && selectedEmployee.phone.length > 5;
                  
                  if (useDirectWhatsApp) {
                    if (!navigator.onLine) {
                      alert("You must be online to generate and upload the cloud link for this pass.");
                      return;
                    }
                    
                    try {
                      // Show uploading state (simple alert for now)
                      const fileName = `${selectedEmployee.empId}_${Date.now()}.png`;
                      
                      const { data, error } = await supabase
                        .storage
                        .from('qr-passes')
                        .upload(fileName, file, {
                          cacheControl: '3600',
                          upsert: false
                        });

                      if (error) {
                        console.error("Upload error", error);
                        alert("Failed to upload image. Did you create the 'qr-passes' public bucket in Supabase?");
                        return;
                      }

                      const { data: { publicUrl } } = supabase
                        .storage
                        .from('qr-passes')
                        .getPublicUrl(fileName);

                      const cleanPhone = (selectedEmployee.phone || '').replace(/\D/g,'');
                      const msg = `Hello ${selectedEmployee.name}, here is your digital Attendance QR Pass!\n\nClick the secure link below to view and download your pass:\n${publicUrl}`;
                      const waUrl = `https://wa.me/${cleanPhone}?text=` + encodeURIComponent(msg);
                      
                      window.open(waUrl, "_blank");
                      
                    } catch (err) {
                      alert("An error occurred while uploading the pass.");
                    }
                    
                  } else if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    try {
                      await navigator.share({
                        title: 'Attendance QR',
                        text: `Here is the Attendance QR Pass for ${selectedEmployee.name}.`,
                        files: [file]
                      });
                    } catch (err: any) {
                      console.log("Share cancelled or failed", err);
                    }
                  } else {
                    alert("Please add a phone number for this employee to share via WhatsApp.");
                  }
                }, "image/png");
              }}
              className="w-full bg-[#25D366] hover:bg-[#1DA851] text-white py-3 rounded-xl flex items-center justify-center font-bold shadow-md transition-colors text-sm"
            >
              <MessageCircle size={18} className="mr-2" /> Share to WhatsApp
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
