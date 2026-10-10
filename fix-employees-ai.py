import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Modify useEffect for initialAiData to handle capturedImage
useEffect_target = """  useEffect(() => {
    if (initialAiData) {
      const defaultCat = role === 'guard' ? 'Visitor' : 'Staff';
      setCategory(defaultCat);
      generateNewId(defaultCat);
      setName(initialAiData.name || "");
      setDepartment(initialAiData.address || "");
      setPhone("+91 ");
      setVehiclePlate("");
      setDocumentFile(null);
      setGroupMembers([initialAiData.id_number || ""]);
      setShowForm(true);
      if (onAiDataConsumed) onAiDataConsumed();
    }
  }, [initialAiData]);"""

useEffect_new = """  useEffect(() => {
    if (initialAiData) {
      const defaultCat = role === 'guard' ? 'Visitor' : 'Staff';
      setCategory(defaultCat);
      generateNewId(defaultCat);
      setName(initialAiData.name || "");
      setDepartment(initialAiData.address || "");
      setPhone("+91 ");
      setVehiclePlate(initialAiData.id_number || ""); // We store AI id_number in vehiclePlate (Identity ID)
      setGroupMembers([""]); // Reset group members
      
      if (initialAiData.capturedImage) {
        // Convert base64 to File object
        fetch(initialAiData.capturedImage)
          .then(res => res.arrayBuffer())
          .then(buf => {
            const file = new File([buf], "ai_scan_capture.jpg", { type: "image/jpeg" });
            setDocumentFile(file);
          });
      } else {
        setDocumentFile(null);
      }
      
      setShowForm(true);
      if (onAiDataConsumed) onAiDataConsumed();
    }
  }, [initialAiData]);"""
code = code.replace(useEffect_target, useEffect_new)

# 2. Modify the Form UI to show Identity ID No. (we map this to `vehiclePlate` state)
form_target = """              {category === 'Vehicle' ? (
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-1">Vehicle Plate Number *</label>
                  <input 
                    type="text" 
                    value={vehiclePlate} 
                    onChange={e => setVehiclePlate(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono uppercase"
                    required
                  />
                </div>
              ) : category !== 'Parcel' ? (
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-1">Department / Company</label>
                  <input 
                    type="text" 
                    value={department} 
                    onChange={e => setDepartment(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              ) : null}"""

form_new = """              {category === 'Vehicle' ? (
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-1">Vehicle Plate Number *</label>
                  <input 
                    type="text" 
                    value={vehiclePlate} 
                    onChange={e => setVehiclePlate(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono uppercase"
                    required
                  />
                </div>
              ) : category !== 'Parcel' ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Department / Company</label>
                    <input 
                      type="text" 
                      value={department} 
                      onChange={e => setDepartment(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Identity ID No. (Aadhar, PAN, etc.)</label>
                    <input 
                      type="text" 
                      value={vehiclePlate} 
                      onChange={e => setVehiclePlate(e.target.value)}
                      placeholder="e.g. 1234-5678-9012"
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono"
                    />
                  </div>
                </div>
              ) : null}"""
code = code.replace(form_target, form_new)

# 3. Update the handleOpenForm default
open_form_target = """      setPhone("+91 ");
      setVehiclePlate("");
      setDocumentFile(null);
      setGroupMembers([""]);
      setShowForm(true);"""
open_form_new = """      setPhone("+91 ");
      setVehiclePlate(""); // This clears the Identity ID or Vehicle Plate
      setDocumentFile(null);
      setGroupMembers([""]);
      setShowForm(true);"""
code = code.replace(open_form_target, open_form_new)

# 4. Update the handleBatchAiScan so the Batch UI fills vehiclePlate instead of groupMembers for IDs
batch_target = """                    if (category === 'Vehicle') setVehiclePlate(draft.id_number || "");
                    else setGroupMembers([draft.id_number || ""]);"""
batch_new = """                    setVehiclePlate(draft.id_number || ""); // Identity ID / Plate mapping"""
code = code.replace(batch_target, batch_new)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done EmployeesTab")
