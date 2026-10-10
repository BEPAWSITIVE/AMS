import os
import re

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'(<div className="absolute bottom-0 right-0 w-12 h-12 border-b-\[4px\] border-r-\[4px\] border-\[#38bdf8\] rounded-br-3xl"><\/div>\s*<\/div>\s*<\/div>\s*)'

button_jsx = """
          {/* AI Snapshot Button */}
          <button
            onClick={handleSnapshotScan}
            disabled={aiLoading}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 w-16 h-16 bg-white/90 backdrop-blur-md rounded-full shadow-[0_10px_20px_-10px_rgba(56,189,248,0.5)] border-[3px] border-[#38bdf8] flex items-center justify-center active:scale-95 transition-all z-[100] disabled:opacity-50 hover:bg-white"
          >
            {aiLoading ? <Loader2 size={28} className="text-[#38bdf8] animate-spin" /> : <Camera size={28} className="text-[#38bdf8]" fill="currentColor" fillOpacity="0.2" />}
          </button>
"""

new_code = re.sub(pattern, r'\1' + button_jsx, code)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Done")
