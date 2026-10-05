import os

scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

# Add cameraActive state
if "cameraActive" not in scanner:
    scanner = scanner.replace('const [isScanning, setIsScanning] = useState(false);', 
                              'const [isScanning, setIsScanning] = useState(false);\n  const [cameraActive, setCameraActive] = useState(false);')

# Prevent startScanner if !cameraActive
old_start = """  useEffect(() => {
    startScanner();
    return () => {
      stopScanner();
    };
  }, []);"""

new_start = """  useEffect(() => {
    if (cameraActive) {
      startScanner();
    } else {
      stopScanner();
    }
    return () => {
      stopScanner();
    };
  }, [cameraActive]);"""
scanner = scanner.replace(old_start, new_start)

# Add Leaf SVG and layout based on cameraActive
old_return = """  return (
    <div className="absolute inset-0 bg-black z-0 overflow-hidden pb-20">
      
      {/* Scanner Viewport */}
      <div className="absolute inset-0 flex items-center justify-center z-0">
        <div id="reader" className="w-full h-full [&>video]:object-cover"></div>
      </div>"""

new_return = """  return (
    <div className="w-full h-full flex flex-col relative">
      
      {/* Background decorations for empty state */}
      {!cameraActive && (
        <>
          <div className="absolute bottom-10 -left-6 opacity-80 pointer-events-none">
            <svg width="120" height="150" viewBox="0 0 100 150" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 150C10 100 40 70 80 50" stroke="#34D399" strokeWidth="4" strokeLinecap="round" />
              <path d="M40 100C30 80 15 70 0 70C15 90 20 100 40 100Z" fill="#34D399" />
              <path d="M60 70C50 50 35 40 20 40C35 60 40 70 60 70Z" fill="#34D399" />
              <path d="M80 50C70 30 55 20 40 20C55 40 60 50 80 50Z" fill="#10B981" />
            </svg>
          </div>
          <div className="absolute bottom-20 -left-4 w-20 h-12 bg-blue-100 rounded-full opacity-60 mix-blend-multiply blur-sm"></div>
        </>
      )}

      {/* Main Scanner Container */}
      <div className={`flex-1 flex flex-col items-center justify-center ${cameraActive ? 'bg-black absolute inset-0 z-50' : ''}`}>
        
        {cameraActive && (
          <div className="absolute top-4 right-4 z-50">
            <button 
              onClick={() => setCameraActive(false)}
              className="bg-white/20 backdrop-blur-md p-2 rounded-full text-white hover:bg-white/30"
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
          <div className="absolute bottom-12 left-0 right-0 px-6 animate-fade-in">
            <button 
              onClick={() => setCameraActive(true)}
              className="w-full bg-[#EAF3FF] hover:bg-[#dce9fa] transition-colors py-4 px-4 rounded-[20px] flex items-center justify-between shadow-sm"
            >
              <div className="flex items-center">
                <div className="bg-[#3B82F6] text-white p-2.5 rounded-xl mr-4 shadow-sm">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><rect x="7" y="7" width="3" height="3"></rect><rect x="14" y="7" width="3" height="3"></rect><rect x="7" y="14" width="3" height="3"></rect><rect x="14" y="14" width="3" height="3"></rect></svg>
                </div>
                <span className="text-[#1E293B] font-bold text-sm">Point camera at employee QR badge</span>
              </div>
              <div className="text-[#3B82F6]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
              </div>
            </button>
          </div>
        )}
      </div>"""

scanner = scanner.replace(old_return, new_return)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scanner)

print("Done")
