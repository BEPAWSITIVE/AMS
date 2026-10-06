import os
scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

# 1. Imports
if "import { CheckCircle2, AlertCircle, X, Truck, Package, Search } from 'lucide-react';" not in scanner:
    scanner = scanner.replace('import { CheckCircle2, AlertCircle, X, Truck, Package } from "lucide-react";', 'import { CheckCircle2, AlertCircle, X, Truck, Package, Search, ChevronRight } from "lucide-react";')

# 2. Add playSuccessSound outside component
play_sound = """const playSuccessSound = () => {
  try {
    const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1760, ctx.currentTime + 0.1);
    
    gainNode.gain.setValueAtTime(0, ctx.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.5, ctx.currentTime + 0.05);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
    
    osc.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    osc.start();
    osc.stop(ctx.currentTime + 0.5);
  } catch (err) {
    console.error("Audio not supported", err);
  }
};

export default function ScannerTab() {"""
scanner = scanner.replace("export default function ScannerTab() {", play_sound)

# 3. Add states
states = """  const [manualModalOpen, setManualModalOpen] = useState(false);
  const [searchPhone, setSearchPhone] = useState("+91 ");
  const [searchResults, setSearchResults] = useState<Employee[]>([]);
  const [isSearching, setIsSearching] = useState(false);"""
scanner = scanner.replace('const [isScanning, setIsScanning] = useState(false);', 'const [isScanning, setIsScanning] = useState(false);\n' + states)

# 4. Add playSuccessSound to success logic
scanner = scanner.replace('setScanResult({ success: true, msg: `${emp.name} Checked OUT', 'playSuccessSound();\n        setScanResult({ success: true, msg: `${emp.name} Checked OUT')
scanner = scanner.replace('setScanResult({ success: true, msg: `${emp.name} Checked IN', 'playSuccessSound();\n        setScanResult({ success: true, msg: `${emp.name} Checked IN')
scanner = scanner.replace('setScanResult({ success: true, isVehicle: true, msg: `Vehicle ${profile.name} Dispatched', 'playSuccessSound();\n      setScanResult({ success: true, isVehicle: true, msg: `Vehicle ${profile.name} Dispatched')
scanner = scanner.replace('setScanResult({ success: true, isVehicle: true, msg: `Vehicle ${profile.name} Returned', 'playSuccessSound();\n      setScanResult({ success: true, isVehicle: true, msg: `Vehicle ${profile.name} Returned')
scanner = scanner.replace('setScanResult({ success: true, msg: `Parcel picked up by', 'playSuccessSound();\n    setScanResult({ success: true, msg: `Parcel picked up by')

# 5. Add Manual Search Logic
manual_logic = """  const handleManualSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSearching(true);
    setSearchResults([]);
    
    const cleanPhone = searchPhone.trim().replace('+91 ', '');
    if (!cleanPhone) {
      setIsSearching(false);
      return;
    }
    
    let results: Employee[] = [];
    
    if (navigator.onLine) {
      const { data } = await supabase.from('employees').select('*').ilike('phone', `%${cleanPhone}%`);
      if (data) results = data;
    } else {
      const cached = localStorage.getItem('cached_employees');
      if (cached) {
        const emps: Employee[] = JSON.parse(cached);
        results = emps.filter(e => e.phone && e.phone.includes(cleanPhone));
      }
    }
    
    setSearchResults(results);
    setIsSearching(false);
  };

  const handleManualSelect = (empId: string) => {
    setManualModalOpen(false);
    setSearchPhone("+91 ");
    setSearchResults([]);
    onScanSuccess(JSON.stringify({ empId }));
  };"""
scanner = scanner.replace('const cancelVehicleScan = () => {', manual_logic + '\n\n  const cancelVehicleScan = () => {')

# 6. UI Update
old_btn = """      {/* Button */}
      <div className="w-full bg-[#EAF3FF] py-4 px-4 rounded-[20px] flex items-center justify-between shadow-sm z-10">
        <div className="flex items-center">
          <div className="bg-[#3B82F6] text-white p-2.5 rounded-xl mr-4 shadow-sm">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><rect x="7" y="7" width="3" height="3"></rect><rect x="14" y="7" width="3" height="3"></rect><rect x="7" y="14" width="3" height="3"></rect><rect x="14" y="14" width="3" height="3"></rect></svg>
          </div>
          <span className="text-[#1E293B] font-bold text-[13px]">Point camera at employee QR badge</span>
        </div>
        <div className="text-[#3B82F6]">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </div>
      </div>"""

new_btn = """      {/* Button */}
      <div className="w-full bg-[#EAF3FF] py-4 px-4 rounded-[20px] flex items-center justify-between shadow-sm z-10 mb-3">
        <div className="flex items-center">
          <div className="bg-[#3B82F6] text-white p-2.5 rounded-xl mr-4 shadow-sm">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><rect x="7" y="7" width="3" height="3"></rect><rect x="14" y="7" width="3" height="3"></rect><rect x="7" y="14" width="3" height="3"></rect><rect x="14" y="14" width="3" height="3"></rect></svg>
          </div>
          <span className="text-[#1E293B] font-bold text-[13px]">Point camera at employee QR badge</span>
        </div>
      </div>

      <button 
        onClick={() => { setManualModalOpen(true); if (scannerRef.current) scannerRef.current.pause(); }}
        className="w-full bg-white border border-gray-100 py-3.5 px-4 rounded-[20px] flex items-center justify-between shadow-sm z-10 hover:bg-gray-50 active:scale-95 transition-transform"
      >
        <div className="flex items-center">
          <div className="bg-gray-100 text-gray-500 p-2 rounded-xl mr-4">
            <Search size={20} />
          </div>
          <div className="text-left">
            <span className="block text-gray-800 font-bold text-sm">Forgot QR Code?</span>
            <span className="block text-gray-400 text-[10px] font-bold uppercase tracking-wider mt-0.5">Search by Phone Number</span>
          </div>
        </div>
        <div className="text-gray-400">
          <ChevronRight size={20} />
        </div>
      </button>"""
scanner = scanner.replace(old_btn, new_btn)

# 7. Add Manual Modal UI
manual_modal = """      {/* Manual Search Modal */}
      {manualModalOpen && (
        <div className="fixed inset-0 z-[120] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white w-full max-w-sm rounded-3xl overflow-hidden shadow-2xl relative flex flex-col max-h-[80vh]">
            <div className="bg-gray-50 p-4 border-b border-gray-100 flex justify-between items-center shrink-0">
              <h3 className="font-bold text-gray-800">Manual Entry</h3>
              <button onClick={() => { setManualModalOpen(false); setSearchResults([]); if (scannerRef.current) scannerRef.current.resume(); }} className="text-gray-400 hover:text-gray-800">
                <X size={20} />
              </button>
            </div>
            
            <div className="p-5 shrink-0">
              <form onSubmit={handleManualSearch} className="flex space-x-2">
                <input 
                  type="text" 
                  value={searchPhone}
                  onChange={e => setSearchPhone(e.target.value)}
                  placeholder="+91 Phone Number"
                  className="flex-1 bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  autoFocus
                />
                <button 
                  type="submit" 
                  className="bg-blue-600 text-white p-3 rounded-xl font-bold shadow-md active:scale-95 transition-transform"
                >
                  <Search size={20} />
                </button>
              </form>
            </div>

            <div className="overflow-y-auto p-5 pt-0 flex-1 space-y-3 bg-gray-50/50">
              {isSearching && <div className="text-center text-sm text-gray-400 py-4">Searching...</div>}
              
              {!isSearching && searchResults.length === 0 && searchPhone !== "+91 " && (
                <div className="text-center text-sm text-gray-400 py-4">No profiles found for this number.</div>
              )}
              
              {searchResults.map(emp => (
                <div key={emp.empId} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex justify-between items-center">
                  <div>
                    <h4 className="font-bold text-gray-800">{emp.name}</h4>
                    <span className="text-[10px] font-bold text-blue-500 uppercase tracking-wider">{emp.category || 'Staff'}</span>
                  </div>
                  <button 
                    onClick={() => handleManualSelect(emp.empId)}
                    className="bg-green-100 hover:bg-green-200 text-green-700 px-4 py-2 rounded-lg font-bold text-xs transition-colors"
                  >
                    Select
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}"""
scanner = scanner.replace('{/* Result Toast */}', manual_modal + '\n\n      {/* Result Toast */}')

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scanner)
print("Done")
