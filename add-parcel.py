import os

# 1. Update EmployeesTab.tsx (Upload fix + Parcel category)
emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

# Add Parcel option
emp = emp.replace('<option value="Vehicle">Rescue Vehicle</option>', '<option value="Vehicle">Rescue Vehicle</option>\n                <option value="Parcel">Parcel / Delivery</option>')

# Update generateNewId
emp = emp.replace("const prefix = cat === 'Staff' ? 'EMP' : cat === 'Visitor' ? 'VIS' : 'VEH';", "const prefix = cat === 'Staff' ? 'EMP' : cat === 'Visitor' ? 'VIS' : cat === 'Parcel' ? 'PAR' : 'VEH';")

# Fix Document Upload Bug
old_upload = """    if (documentFile) {
      if (!navigator.onLine) {
        alert("You must be online to upload ID documents.");
        setIsUploading(false);
        return;
      }
      const fileName = `${empId}_${Date.now()}_${documentFile.name}`;
      const { data, error } = await supabase.storage.from('documents').upload(fileName, documentFile);
      if (error) {
        alert("Failed to upload document: " + error.message);
        setIsUploading(false);
        return;
      }
      const { data: { publicUrl } } = supabase.storage.from('documents').getPublicUrl(fileName);
      document_url = publicUrl;
    }"""

new_upload = """    if (documentFile) {
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
    }"""
emp = emp.replace(old_upload, new_upload)

# Form labels for Parcel
old_name_label = """                  {category === 'Vehicle' ? 'Vehicle Name *' : 'Full Name *'}"""
new_name_label = """                  {category === 'Vehicle' ? 'Vehicle Name *' : category === 'Parcel' ? 'Courier / Delivery Svc *' : 'Full Name *'}"""
emp = emp.replace(old_name_label, new_name_label)

old_dept_label = """                    {category === 'Visitor' ? 'Purpose/Org' : 'Department'}"""
new_dept_label = """                    {category === 'Visitor' ? 'Purpose/Org' : category === 'Parcel' ? 'Tracking # / Desc' : 'Department'}"""
emp = emp.replace(old_dept_label, new_dept_label)

# ID Card UI for Parcel
emp = emp.replace("const bannerTitle = emp.category === 'Vehicle' ? 'VEHICLE PASS' : emp.category === 'Visitor' ? 'VISITOR PASS' : 'STAFF ID CARD';", "const bannerTitle = emp.category === 'Vehicle' ? 'VEHICLE PASS' : emp.category === 'Visitor' ? 'VISITOR PASS' : emp.category === 'Parcel' ? 'PARCEL TRACKER' : 'STAFF ID CARD';")
emp = emp.replace("emp.category === 'Vehicle' ? '#f59e0b' : emp.category === 'Visitor' ? '#10b981' : '#2563eb'", "emp.category === 'Vehicle' ? '#f59e0b' : emp.category === 'Visitor' ? '#10b981' : emp.category === 'Parcel' ? '#8b5cf6' : '#2563eb'")

emp = emp.replace("selectedEmployee.category === 'Vehicle' ? 'VEHICLE PASS' : selectedEmployee.category === 'Visitor' ? 'VISITOR PASS' : 'STAFF PASS'", "selectedEmployee.category === 'Vehicle' ? 'VEHICLE PASS' : selectedEmployee.category === 'Visitor' ? 'VISITOR PASS' : selectedEmployee.category === 'Parcel' ? 'PARCEL TRACKER' : 'STAFF PASS'")
emp = emp.replace("selectedEmployee.category === 'Vehicle' ? 'bg-amber-100 text-amber-700' : \n                  selectedEmployee.category === 'Visitor' ? 'bg-emerald-100 text-emerald-700' : \n                  'bg-blue-100 text-blue-700'", "selectedEmployee.category === 'Vehicle' ? 'bg-amber-100 text-amber-700' : \n                  selectedEmployee.category === 'Visitor' ? 'bg-emerald-100 text-emerald-700' : \n                  selectedEmployee.category === 'Parcel' ? 'bg-purple-100 text-purple-700' : \n                  'bg-blue-100 text-blue-700'")

# List UI for Parcel
emp = emp.replace("emp.category === 'Vehicle' ? 'bg-amber-100 text-amber-700' : \n                    emp.category === 'Visitor' ? 'bg-emerald-100 text-emerald-700' : \n                    'bg-blue-100 text-blue-700'", "emp.category === 'Vehicle' ? 'bg-amber-100 text-amber-700' : \n                    emp.category === 'Visitor' ? 'bg-emerald-100 text-emerald-700' : \n                    emp.category === 'Parcel' ? 'bg-purple-100 text-purple-700' : \n                    'bg-blue-100 text-blue-700'")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(emp)


# 2. Update ScannerTab.tsx
scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

if "parcelModal" not in scanner:
    scanner = scanner.replace('import { CheckCircle2, AlertCircle, X, Truck } from "lucide-react";', 'import { CheckCircle2, AlertCircle, X, Truck, Package } from "lucide-react";')
    scanner = scanner.replace('} | null>(null);', '} | null>(null);\n  const [parcelModal, setParcelModal] = useState<{ profile: Employee; lastRecord: AttendanceRecord } | null>(null);\n  const [pickerName, setPickerName] = useState("");')

    old_scan_logic = """      if (emp.category === 'Vehicle') {
        setVehicleModal({ profile: emp, lastRecord });
        return; 
      }

      if (lastRecord && lastRecord.status === 'IN') {"""
      
    new_scan_logic = """      if (emp.category === 'Vehicle') {
        setVehicleModal({ profile: emp, lastRecord });
        return; 
      }
      
      if (emp.category === 'Parcel' && lastRecord && lastRecord.status === 'IN') {
        setParcelModal({ profile: emp, lastRecord });
        return;
      }

      if (lastRecord && lastRecord.status === 'IN') {"""
    scanner = scanner.replace(old_scan_logic, new_scan_logic)

    # Add handleParcelSubmit
    parcel_submit = """  const handleParcelSubmit = async (e: React.FormEvent) => {
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
  };"""
    scanner = scanner.replace('const cancelVehicleScan = () => {', parcel_submit + '\n\n  const cancelVehicleScan = () => {')

    # Add Parcel Modal UI
    parcel_modal_ui = """      {/* Parcel Action Modal */}
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
      )}"""
    scanner = scanner.replace('{/* Vehicle Action Modal */}', parcel_modal_ui + '\n\n      {/* Vehicle Action Modal */}')
    
    with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
        f.write(scanner)


# 3. Update LogsTab.tsx
logs = open('components/LogsTab.tsx', 'r', encoding='utf-8').read()

logs = logs.replace('import { Clock, CheckCircle2, UserPlus, Truck, Shield } from "lucide-react";', 'import { Clock, CheckCircle2, UserPlus, Truck, Shield, Package } from "lucide-react";')

logs = logs.replace("if (cat === 'Vehicle') return <Truck size={16} className=\"text-amber-500\" />;\n    if (cat === 'Visitor') return <UserPlus size={16} className=\"text-emerald-500\" />;", "if (cat === 'Vehicle') return <Truck size={16} className=\"text-amber-500\" />;\n    if (cat === 'Parcel') return <Package size={16} className=\"text-purple-500\" />;\n    if (cat === 'Visitor') return <UserPlus size={16} className=\"text-emerald-500\" />;")

old_status_badge = """                {log.category !== 'Vehicle' && (
                  <div className={`px-2 py-1 rounded-md text-xs font-bold ${log.status === 'IN' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                    {log.status === 'IN' ? 'Active' : 'Completed'}
                  </div>
                )}"""
new_status_badge = """                {log.category !== 'Vehicle' && log.category !== 'Parcel' && (
                  <div className={`px-2 py-1 rounded-md text-xs font-bold ${log.status === 'IN' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                    {log.status === 'IN' ? 'Active' : 'Completed'}
                  </div>
                )}
                {log.category === 'Parcel' && (
                  <div className={`px-2 py-1 rounded-md text-xs font-bold ${log.status === 'IN' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'}`}>
                    {log.status === 'IN' ? 'At Gate' : 'Picked Up'}
                  </div>
                )}"""
logs = logs.replace(old_status_badge, new_status_badge)

old_card_body = """              {log.category === 'Vehicle' ? ("""
new_card_body = """              {log.category === 'Parcel' ? (
                <div className="flex items-center space-x-2 mt-1">
                  <div className="flex-1 bg-purple-50 p-2 rounded-xl text-center border border-purple-100">
                    <span className="block text-[10px] text-purple-600 uppercase font-bold tracking-widest">Received</span>
                    <span className="font-bold text-gray-800">{log.inTime}</span>
                  </div>
                  <div className="flex-1 bg-gray-50 p-2 rounded-xl text-center border border-gray-100">
                    <span className="block text-[10px] text-gray-500 uppercase font-bold tracking-widest">{log.driver_name ? `Given to ${log.driver_name}` : 'Awaiting Pickup'}</span>
                    <span className="font-bold text-gray-800">{log.outTime || "--:--"}</span>
                  </div>
                </div>
              ) : log.category === 'Vehicle' ? ("""
logs = logs.replace(old_card_body, new_card_body)

with open('components/LogsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(logs)

print("Done")
