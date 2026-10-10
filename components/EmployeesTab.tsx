"use client";
import { useState, useEffect, useRef } from "react";
import { supabase, Employee } from "@/lib/supabase";
import { localdb } from "@/lib/localdb";
import { QRCodeCanvas } from "qrcode.react";
import { MessageCircle, X, Download, UserPlus, FileText, Truck, Shield, Camera, Loader2, Sparkles, CheckCircle2 } from "lucide-react";

export default function EmployeesTab({ role = "admin", initialAiData, onAiDataConsumed }: { role?: "admin" | "guard", initialAiData?: any, onAiDataConsumed?: () => void }) {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [batchDrafts, setBatchDrafts] = useState<any[]>([]);
  const [aiLoading, setAiLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const compressImage = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        
        const MAX_DIM = 1200;
        if (width > height && width > MAX_DIM) {
          height *= MAX_DIM / width;
          width = MAX_DIM;
        } else if (height > MAX_DIM) {
          width *= MAX_DIM / height;
          height = MAX_DIM;
        }
        
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(img, 0, 0, width, height);
        
        resolve(canvas.toDataURL('image/jpeg', 0.6));
      };
      img.src = URL.createObjectURL(file);
    });
  };

  const handleBatchAiScan = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAiLoading(true);
    try {
      const base64 = await compressImage(file);
      
      const res = await fetch('/api/analyze-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ images: [base64], category: category })
      });
      
      const data = await res.json();
      setAiLoading(false);
      
      if (data.error) {
        alert("AI Error: " + data.error);
        return;
      }
      
      if (!data.records || data.records.length === 0) {
        alert("No records could be extracted from this image.");
        return;
      }

      setBatchDrafts(data.records.map((r: any, idx: number) => ({ ...r, _tempId: Date.now() + idx })));
    } catch (err: any) {
      alert("AI Scan failed: " + err.message);
      setAiLoading(false);
    }
  };

  
  // Form states
  const [category, setCategory] = useState("Staff"); // Staff, Visitor, Vehicle
  const [empId, setEmpId] = useState("");
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [phone, setPhone] = useState("+91 ");
  const [vehiclePlate, setVehiclePlate] = useState("");

  useEffect(() => {
    if (role === 'guard' && category !== 'Visitor') {
      setCategory('Visitor');
    }
  }, [role, category]);

  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [groupMembers, setGroupMembers] = useState<string[]>([""]);
  
  const [isUploading, setIsUploading] = useState(false);
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
    
    const queuedEmps = await localdb.employeeQueue.toArray();
    const merged = [...queuedEmps, ...allEmps].reduce((acc: Employee[], curr: any) => {
      const current = curr as Employee;
      if (!acc.find((item: Employee) => item.empId === current.empId)) acc.push(current);
      return acc;
    }, [] as Employee[]);
    
    merged.sort((a: Employee, b: Employee) => new Date(b.createdAt || 0).getTime() - new Date(a.createdAt || 0).getTime());
    setEmployees(merged);
    setLoading(false);
  }

  
  useEffect(() => {
    if (initialAiData) {
      setCategory('Visitor');
      generateNewId('Visitor');
      setName(initialAiData.name || "");
      setDepartment(initialAiData.address || "");
      setPhone("+91 ");
      setVehiclePlate("");
      setDocumentFile(null);
      setGroupMembers([initialAiData.id_number || ""]);
      setShowForm(true);
      if (onAiDataConsumed) onAiDataConsumed();
    }
  }, [initialAiData]);

  const generateNewId = (cat: string) => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < 4; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    const prefix = cat === 'Staff' ? 'EMP' : cat === 'Visitor' ? 'VIS' : cat === 'Parcel' ? 'PAR' : 'VEH';
    setEmpId(`${prefix}-${result}`);
  };

  const handleOpenForm = () => {
    const defaultCat = role === 'guard' ? 'Visitor' : 'Staff';
    setCategory(defaultCat);
    generateNewId(defaultCat);
    setName("");
    setDepartment("");
    setPhone("+91 ");
    setVehiclePlate("");
    setDocumentFile(null);
    setGroupMembers([""]);
    setShowForm(true);
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const cat = e.target.value;
    setCategory(cat);
    generateNewId(cat);
    if (cat === 'Vehicle') {
      setDepartment("Logistics"); // Default for vehicles
    }
  };

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!empId || !name) return;
    
    setIsUploading(true);
    let document_url = "";
    
    if (documentFile) {
      if (!navigator.onLine) {
        alert("You must be online to upload ID documents.");
        setIsUploading(false);
        return;
      }
      try {
        const fileExt = documentFile.name.split('.').pop() || 'jpg';
        const fileName = `${empId}_${Date.now()}.${fileExt}`.replace(/\s+/g, '_');
        const { data, error } = await supabase.storage.from('documents').upload(fileName, documentFile, { cacheControl: '3600', upsert: false });
        if (error) throw error;
        const { data: { publicUrl } } = supabase.storage.from('documents').getPublicUrl(fileName);
        document_url = publicUrl;
      } catch (err: any) {
        alert("Upload failed. Make sure 'documents' bucket exists and has public INSERT policy. Error: " + err.message);
        setIsUploading(false);
        return;
      }
    }
    
    const filteredGroup = groupMembers.filter(m => m.trim() !== "");
    const newEmp: Employee = {
      empId, 
      name, 
      department, 
      phone, 
      category,
      document_url: document_url || undefined,
      vehicle_plate: category === 'Vehicle' ? vehiclePlate : undefined,
      group_members: filteredGroup.length > 0 ? filteredGroup.join(", ") : undefined,
      createdAt: new Date().toISOString()
    };
    
    if (navigator.onLine) {
      try {
        const { error } = await supabase.from('employees').insert([newEmp]);
        if (error) throw error;
      } catch (err: any) {
        alert("Error adding profile: " + err.message);
        setIsUploading(false);
        return;
      }
    } else {
      await localdb.employeeQueue.put(newEmp);
      const cached = localStorage.getItem('cached_employees');
      const currentList = cached ? JSON.parse(cached) : [];
      currentList.unshift(newEmp);
      localStorage.setItem('cached_employees', JSON.stringify(currentList));
    }
    
    setIsUploading(false);
    setShowForm(false);
    fetchEmployees();
  }

  // Draw a beautiful ID card
  const generateCardCanvas = (qrCanvas: HTMLCanvasElement, emp: Employee): HTMLCanvasElement => {
    const canvas = document.createElement('canvas');
    canvas.width = 600;
    canvas.height = 800;
    const ctx = canvas.getContext('2d');
    if (!ctx) return qrCanvas;

    // Background gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#ffffff');
    gradient.addColorStop(1, '#f0f7ff');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Header Banner
    ctx.fillStyle = emp.category === 'Vehicle' ? '#f59e0b' : emp.category === 'Visitor' ? '#10b981' : emp.category === 'Parcel' ? '#8b5cf6' : '#2563eb';
    ctx.fillRect(0, 0, canvas.width, 140);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 44px sans-serif';
    ctx.textAlign = 'center';
    const bannerTitle = emp.category === 'Vehicle' ? 'VEHICLE PASS' : emp.category === 'Visitor' ? 'VISITOR PASS' : emp.category === 'Parcel' ? 'PARCEL TRACKER' : 'STAFF ID CARD';
    ctx.fillText(bannerTitle, canvas.width / 2, 85);

    // Card Body
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = 'rgba(0,0,0,0.1)';
    ctx.shadowBlur = 20;
    ctx.shadowOffsetY = 10;
    ctx.roundRect(40, 180, 520, 580, 30);
    ctx.fill();
    ctx.shadowColor = 'transparent';

    // QR Code
    ctx.drawImage(qrCanvas, (canvas.width - 250) / 2, 220, 250, 250);

    // Profile Details
    ctx.fillStyle = '#1e293b';
    ctx.font = 'bold 38px sans-serif';
    ctx.fillText(emp.name.toUpperCase(), canvas.width / 2, 530);

    ctx.fillStyle = '#64748b';
    ctx.font = '24px sans-serif';
    ctx.fillText(emp.department.toUpperCase(), canvas.width / 2, 570);

    // Divider
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(100, 610);
    ctx.lineTo(500, 610);
    ctx.stroke();

    // Footer Info
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 28px monospace';
    ctx.fillText(`ID: ${emp.empId}`, canvas.width / 2, 660);
    
    if (emp.category === 'Vehicle' && emp.vehicle_plate) {
      ctx.fillStyle = '#0f172a';
      ctx.font = 'bold 24px monospace';
      ctx.fillText(`PLATE: ${emp.vehicle_plate}`, canvas.width / 2, 700);
    } else if (emp.phone) {
      ctx.fillStyle = '#0f172a';
      ctx.font = 'bold 24px monospace';
      ctx.fillText(`PH: ${emp.phone}`, canvas.width / 2, 700);
    }

    return canvas;
  };

  const getCategoryIcon = (cat?: string) => {
    if (cat === 'Vehicle') return <Truck size={16} className="text-amber-500" />;
    if (cat === 'Visitor') return <UserPlus size={16} className="text-emerald-500" />;
    return <Shield size={16} className="text-blue-500" />;
  };

  return (
    <div className="p-4 pb-20 max-w-md mx-auto space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-2xl font-bold text-gray-800">Registry</h2>
        <button 
          onClick={handleOpenForm}
          className="bg-blue-900 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center shadow-md active:scale-95 transition-transform"
        >
          + Add New
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-5 rounded-2xl shadow-lg border border-gray-100 mb-6 animate-fade-in relative">
          <button onClick={() => setShowForm(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-700">
            <X size={20} />
          </button>
          
          <h3 className="text-lg font-bold mb-4 text-gray-800">Register Profile</h3>
          <form onSubmit={handleAdd} className="space-y-4">
            
            <div>
              <label className="block text-xs font-bold text-gray-500 mb-1">Category</label>
              <select 
                  value={category}
                  onChange={handleCategoryChange}
                  className={`w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-medium ${role === 'guard' ? 'opacity-70 cursor-not-allowed' : ''}`}
                  disabled={role === 'guard'}
                >
                  {role === 'admin' && <option value="Staff">Staff</option>}
                  <option value="Visitor">Visitor</option>
                  {role === 'admin' && <option value="Volunteer">Volunteer</option>}
                  {role === 'admin' && <option value="Workexchange">Work Exchange</option>}
                  {role === 'admin' && <option value="Vehicle">Vehicle</option>}
                </select>
            </div>

            <div className="flex space-x-3">
              <div className="w-1/2">
                <label className="block text-xs font-bold text-gray-500 mb-1">ID *</label>
                <input 
                  type="text" 
                  value={empId} 
                  onChange={e => setEmpId(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono"
                  required
                />
              </div>
              <div className="w-1/2">
                <label className="block text-xs font-bold text-gray-500 mb-1">
                  {category === 'Vehicle' ? 'Vehicle Name *' : category === 'Parcel' ? 'Courier / Delivery Svc *' : 'Full Name *'}
                </label>
                <input 
                  type="text" 
                  value={name} 
                  onChange={e => setName(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>

            {category === 'Vehicle' ? (
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">License Plate Number</label>
                <input 
                  type="text" 
                  value={vehiclePlate} 
                  onChange={e => setVehiclePlate(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono uppercase"
                  placeholder="e.g. MH-12-AB-1234"
                />
              </div>
            ) : (
              <div className="flex space-x-3">
                <div className="w-1/2">
                  <label className="block text-xs font-bold text-gray-500 mb-1">
                    {category === 'Visitor' ? 'Purpose/Org' : category === 'Parcel' ? 'Tracking # / Desc' : 'Department'}
                  </label>
                  <input 
                    type="text" 
                    value={department} 
                    onChange={e => setDepartment(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="w-1/2">
                  <label className="block text-xs font-bold text-gray-500 mb-1">Phone Number</label>
                  <input 
                    type="tel" 
                    value={phone} 
                    onChange={e => setPhone(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            )}

            {category === 'Visitor' && (
              <>
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-1">ID Document (Optional Photo)</label>
                  <div className="relative w-full bg-blue-50 border-2 border-dashed border-blue-200 p-4 rounded-xl text-center hover:bg-blue-100 transition-colors">
                    <input 
                      type="file" 
                      accept="image/*"
                      capture="environment"
                      onChange={e => e.target.files && setDocumentFile(e.target.files[0])}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <div className="text-blue-600 font-bold flex flex-col items-center justify-center w-full">
                      {documentFile ? (
                        <>
                          <svg className="w-8 h-8 mb-1 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                          <span className="text-green-600">Photo Ready!</span>
                          <span className="text-xs text-gray-500 mt-1 max-w-full truncate px-4">{documentFile.name}</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                          Tap to open Camera (Optional)
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-gray-100">
                  <label className="block text-xs font-bold text-gray-500">Group Members (Optional)</label>
                  {groupMembers.map((member, idx) => (
                    <div key={idx} className="flex space-x-2">
                      <input 
                        type="text" 
                        value={member}
                        onChange={(e) => {
                          const newMembers = [...groupMembers];
                          newMembers[idx] = e.target.value;
                          setGroupMembers(newMembers);
                        }}
                        placeholder={`Member ${idx + 1} Name`}
                        className="flex-1 bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                    </div>
                  ))}
                  <button 
                    type="button" 
                    onClick={() => setGroupMembers([...groupMembers, ""])}
                    className="text-xs font-bold text-blue-600 hover:text-blue-800 bg-blue-50 px-3 py-1.5 rounded-lg"
                  >
                    + Add another person
                  </button>
                </div>
              </>
            )}

            <div className="flex space-x-3 pt-2">
              <button 
                type="button" 
                onClick={() => setShowForm(false)}
                className="flex-1 bg-gray-100 text-gray-600 py-3 rounded-xl font-bold"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                disabled={isUploading}
                className="flex-1 bg-blue-900 text-white py-3 rounded-xl font-bold shadow-md disabled:opacity-50"
              >
                {isUploading ? "Uploading..." : "Save Profile"}
              </button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="text-center py-10 text-gray-400">Loading registry...</div>
      ) : employees.length === 0 ? (
        <div className="text-center py-10 text-gray-400 bg-white rounded-2xl border border-dashed border-gray-200">
          No profiles registered yet.
        </div>
      ) : (
        <div className="space-y-3">
          {employees.map(emp => (
            <div 
              key={emp.empId} 
              onClick={() => setSelectedEmployee(emp)}
              className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between cursor-pointer hover:border-blue-300 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg
                  ${emp.category === 'Vehicle' ? 'bg-amber-100 text-amber-700' : 
                    emp.category === 'Visitor' ? 'bg-emerald-100 text-emerald-700' : 
                    emp.category === 'Parcel' ? 'bg-purple-100 text-purple-700' : 
                    'bg-blue-100 text-blue-700'}`}>
                  {emp.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-gray-800">{emp.name}</h3>
                    <span className="flex items-center text-[10px] uppercase tracking-wider font-bold bg-gray-100 text-gray-500 px-2 py-0.5 rounded-md">
                      {getCategoryIcon(emp.category)} <span className="ml-1">{emp.category || 'Staff'}</span>
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-0.5 font-mono text-xs">{emp.empId} • {emp.category === 'Vehicle' ? emp.vehicle_plate : emp.department}</p>
                </div>
              </div>
              
              {emp.document_url && (
                <div className="text-emerald-500 bg-emerald-50 p-2 rounded-full" title="Document Attached">
                  <FileText size={18} />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* QR Code Modal */}
      {selectedEmployee && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white rounded-3xl w-full max-w-sm overflow-hidden shadow-2xl relative">
            <button 
              onClick={() => setSelectedEmployee(null)}
              className="absolute top-4 right-4 p-2 bg-gray-100 text-gray-500 rounded-full hover:bg-gray-200 z-10"
            >
              <X size={20} />
            </button>
            
            <div className="p-8 pb-6 flex flex-col items-center">
              <div className={`w-full text-center py-2 mb-6 rounded-lg font-bold text-sm tracking-widest
                ${selectedEmployee.category === 'Vehicle' ? 'bg-amber-100 text-amber-700' : 
                  selectedEmployee.category === 'Visitor' ? 'bg-emerald-100 text-emerald-700' : 
                  selectedEmployee.category === 'Parcel' ? 'bg-purple-100 text-purple-700' : 
                  'bg-blue-100 text-blue-700'}`}>
                {selectedEmployee.category === 'Vehicle' ? 'VEHICLE PASS' : selectedEmployee.category === 'Visitor' ? 'VISITOR PASS' : selectedEmployee.category === 'Parcel' ? 'PARCEL TRACKER' : 'STAFF PASS'}
              </div>

              <div className="bg-white p-4 rounded-2xl shadow-inner border border-gray-100 mb-6 relative">
                {/* Hidden canvas used to generate the final image */}
                <div className="hidden">
                  <QRCodeCanvas 
                    id="qr-canvas"
                    value={JSON.stringify({ empId: selectedEmployee.empId })} 
                    size={200}
                    level="H"
                    includeMargin={true}
                  />
                </div>
                {/* Visible QR Code for display */}
                <QRCodeCanvas 
                  value={JSON.stringify({ empId: selectedEmployee.empId })} 
                  size={180}
                  level="H"
                />
              </div>

              <h2 className="text-2xl font-bold text-gray-800 text-center">{selectedEmployee.name}</h2>
              <p className="text-gray-500 font-mono mt-1">{selectedEmployee.empId}</p>

              {selectedEmployee.group_members && (
                <div className="mt-3 bg-gray-50 p-3 rounded-xl w-full text-center border border-gray-100">
                  <span className="text-xs font-bold text-gray-500 uppercase tracking-wide block mb-1">Group Members</span>
                  <span className="text-sm font-medium text-gray-700">{selectedEmployee.group_members}</span>
                </div>
              )}
              
              {selectedEmployee.document_url && (
                <a 
                  href={selectedEmployee.document_url} 
                  target="_blank" 
                  rel="noreferrer"
                  className="mt-4 text-sm text-blue-600 font-medium flex items-center bg-blue-50 px-4 py-2 rounded-lg"
                >
                  <FileText size={16} className="mr-2" /> View Attached Document
                </a>
              )}
            </div>

            <div className="bg-gray-50 p-4 border-t border-gray-100 px-6">
              <div className="w-full flex space-x-2">
                <button 
                  onClick={() => {
                    const qrCanvas = document.getElementById("qr-canvas") as HTMLCanvasElement;
                    if (!qrCanvas) return;
                    const cardCanvas = generateCardCanvas(qrCanvas, selectedEmployee);
                    const url = cardCanvas.toDataURL("image/png");
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `${selectedEmployee.name.replace(/\s+/g, '_')}_Pass.png`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                  }}
                  className="flex-1 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 py-3 rounded-xl flex items-center justify-center font-bold shadow-sm transition-colors text-sm"
                >
                  <Download size={18} className="mr-1" /> Download
                </button>
                <button 
                  onClick={async () => {
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
                          const fileName = `${selectedEmployee.empId}_${Date.now()}.png`;
                          const { error } = await supabase.storage.from('qr-passes').upload(fileName, file, { cacheControl: '3600', upsert: false });
                          if (error) {
                            alert("Failed to upload image. Did you create the 'qr-passes' public bucket?");
                            return;
                          }
                          const passPageUrl = `${window.location.origin}/pass/${fileName}`;
                          const cleanPhone = (selectedEmployee.phone || '').replace(/\D/g,'');
                          const msg = `Hello ${selectedEmployee.name},\n\nOpen the link to view your QR pass and download it:\n${passPageUrl}`;
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
                        alert("Please add a phone number for this profile to share via WhatsApp.");
                      }
                    }, "image/png");
                  }}
                  className="flex-1 bg-[#25D366] hover:bg-[#1DA851] text-white py-3 rounded-xl flex items-center justify-center font-bold shadow-md transition-colors text-sm"
                >
                  <MessageCircle size={18} className="mr-1" /> WhatsApp
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
