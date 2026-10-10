import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. State Injection
target_state = '  const [showForm, setShowForm] = useState(false);'
state_injection = """  const [showForm, setShowForm] = useState(false);
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
"""
if target_state in code:
    code = code.replace(target_state, state_injection)
else:
    print("Failed to find state target")


# 2. Imports
code = code.replace('import { useState, useEffect }', 'import { useState, useEffect, useRef }')
code = code.replace('import { MessageCircle, X, Download, UserPlus, FileText, Truck, Shield, Camera, Loader2, Sparkles, CheckCircle2 } from "lucide-react";', 'import { MessageCircle, X, Download, UserPlus, FileText, Truck, Shield, Camera, Loader2, Sparkles, CheckCircle2 } from "lucide-react";')


# 3. Button Injection
old_button = """        <div className="flex items-center justify-between mb-2">
          <h2 className="text-2xl font-bold text-gray-800">Registry</h2>
          <button 
            onClick={handleOpenForm}
            className="bg-blue-900 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center shadow-md active:scale-95 transition-transform"
          >
            + Add New
          </button>
        </div>"""

new_button = """        <div className="flex items-center justify-between mb-2">
          <h2 className="text-2xl font-bold text-gray-800">Registry</h2>
          <div className="flex items-center space-x-2">
            {role === 'admin' && (
              <>
                <input 
                  type="file" 
                  accept="image/*"
                  capture="environment"
                  ref={fileInputRef}
                  onChange={handleBatchAiScan}
                  className="hidden"
                />
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  disabled={aiLoading}
                  className="bg-purple-100 text-purple-700 px-3 py-2 rounded-xl text-sm font-bold flex items-center shadow-sm active:scale-95 transition-transform border border-purple-200"
                >
                  {aiLoading ? <Loader2 size={18} className="animate-spin mr-1.5" /> : <Camera size={18} className="mr-1.5" />}
                  AI Scan
                </button>
              </>
            )}
            <button 
              onClick={handleOpenForm}
              className="bg-blue-900 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center shadow-md active:scale-95 transition-transform"
            >
              + Add New
            </button>
          </div>
        </div>"""
if old_button in code:
    code = code.replace(old_button, new_button)
else:
    print("Failed to find button target")

# 4. Batch UI Injection
target_list_header = """      <div className="mb-4">
        <div className="relative">"""

batch_ui = """      {/* Batch Drafts */}
      {batchDrafts.length > 0 && !showForm && (
        <div className="mb-6 p-4 bg-purple-50 rounded-2xl border border-purple-100 shadow-sm animate-fade-in">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-bold text-purple-800 flex items-center"><Sparkles size={16} className="mr-2"/> AI Extracted ({batchDrafts.length})</h3>
            <button onClick={() => setBatchDrafts([])} className="text-purple-400 hover:text-purple-600"><X size={20}/></button>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {batchDrafts.map((draft) => (
              <div key={draft._tempId} className="bg-white p-3 rounded-xl flex justify-between items-center shadow-sm border border-purple-100">
                <div className="overflow-hidden">
                  <p className="font-bold text-sm text-gray-800 truncate">{draft.name || 'Unknown Name'}</p>
                  <p className="text-[11px] text-gray-500 font-medium truncate">{draft.phone || 'No Phone'} • {draft.id_number || 'No ID'}</p>
                </div>
                <button 
                  onClick={() => {
                    handleOpenForm();
                    setName(draft.name || "");
                    setPhone(draft.phone?.startsWith("+91") ? draft.phone : "+91 " + (draft.phone || ""));
                    if (category === 'Vehicle') setVehiclePlate(draft.id_number || "");
                    else setGroupMembers([draft.id_number || ""]);
                    setDepartment(draft.address || "");
                    // Remove from drafts so it's not processed twice
                    setBatchDrafts(prev => prev.filter(d => d._tempId !== draft._tempId));
                  }}
                  className="ml-2 px-3 py-1.5 bg-purple-600 text-white text-xs font-bold rounded-lg shadow-sm whitespace-nowrap active:scale-95"
                >
                  Review & Save
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

"""
if target_list_header in code:
    code = code.replace(target_list_header, batch_ui + target_list_header)
else:
    print("Failed to find list header target")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
