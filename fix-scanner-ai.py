import os

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Import Loader and add to imports
code = code.replace('import { QrCode, Search, ChevronRight, X, AlertCircle } from "lucide-react";', 'import { QrCode, Search, ChevronRight, X, AlertCircle, Sparkles, Loader2, Camera } from "lucide-react";')

# 2. Add AI Scan loading state
code = code.replace('const [searchQuery, setSearchQuery] = useState("");', 'const [searchQuery, setSearchQuery] = useState("");\n  const [aiLoading, setAiLoading] = useState(false);')

# 3. Add handleAiScan method
ai_scan_method = """  const handleAiScan = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAiLoading(true);
    try {
      // Convert to base64
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = async () => {
        const base64 = reader.result as string;
        
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ images: [base64] })
        });
        
        const data = await res.json();
        setAiLoading(false);
        
        if (data.error) {
          alert("AI Error: " + data.error);
          return;
        }
        
        if (data.type === 'unknown') {
          alert("Could not recognize this as an ID or Parcel. Please try again.");
          return;
        }

        // Dispatch to app/page.tsx to switch tabs and pass data
        window.dispatchEvent(new CustomEvent('ai_scan_result', { detail: data }));
      };
    } catch (err) {
      alert("AI Scan failed.");
      setAiLoading(false);
    }
  };"""

code = code.replace('const handleManualSearch = (query: string) => {', ai_scan_method + '\n\n  const handleManualSearch = (query: string) => {')

# 4. Add the UI button to ScannerTab
old_buttons = """        <div className="mt-8 pt-6 border-t border-gray-100">
          <button 
            onClick={() => {
              if (scannerRef.current) {
                try { scannerRef.current.pause(); } catch(e) {}
              }
              setShowManualModal(true);
            }}
            className="w-full bg-white border border-gray-200 text-gray-700 p-4 rounded-xl font-bold shadow-sm hover:bg-gray-50 flex items-center justify-center transition-colors"
          >
            <Search size={20} className="mr-2" />
            Forgot QR Code? Search Manual
          </button>
        </div>"""

new_buttons = """        <div className="mt-8 pt-6 border-t border-gray-100 space-y-3">
          <button 
            onClick={() => {
              if (scannerRef.current) {
                try { scannerRef.current.pause(); } catch(e) {}
              }
              setShowManualModal(true);
            }}
            className="w-full bg-white border border-gray-200 text-gray-700 p-4 rounded-xl font-bold shadow-sm hover:bg-gray-50 flex items-center justify-center transition-colors"
          >
            <Search size={20} className="mr-2" />
            Forgot QR Code? Search Manual
          </button>
          
          <div className="relative w-full">
            <input 
              type="file" 
              accept="image/*"
              capture="environment"
              onChange={handleAiScan}
              disabled={aiLoading}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10 disabled:cursor-not-allowed"
            />
            <button 
              disabled={aiLoading}
              className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-4 rounded-xl font-bold shadow-md hover:opacity-90 flex items-center justify-center transition-opacity"
            >
              {aiLoading ? (
                <><Loader2 size={20} className="mr-2 animate-spin" /> AI Analyzing...</>
              ) : (
                <><Sparkles size={20} className="mr-2" /> Auto-Scan ID or Parcel with AI</>
              )}
            </button>
          </div>
        </div>"""

code = code.replace(old_buttons, new_buttons)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
