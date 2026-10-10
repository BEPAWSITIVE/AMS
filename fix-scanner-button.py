import os
import re

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add capturedImage to ai_scan_result
event_target = "window.dispatchEvent(new CustomEvent('ai_scan_result', { detail: data }));"
event_replacement = "window.dispatchEvent(new CustomEvent('ai_scan_result', { detail: { ...data, capturedImage: base64 } }));"
code = code.replace(event_target, event_replacement)

# 2. Move the button out of the reader container.
button_pattern = r'\{\/\* AI Snapshot Button \*\/\}\s*<button\s*onClick=\{handleSnapshotScan\}\s*disabled=\{aiLoading\}\s*className="absolute bottom-4 left-1\/2 -translate-x-1\/2 w-16 h-16 bg-white\/90 backdrop-blur-md rounded-full shadow-\[0_10px_20px_-10px_rgba\(56,189,248,0\.5\)\] border-\[3px\] border-\[#38bdf8\] flex items-center justify-center active:scale-95 transition-all z-\[100\] disabled:opacity-50 hover:bg-white"\s*>\s*\{aiLoading \? <Loader2 size=\{28\} className="text-\[#38bdf8\] animate-spin" \/> : <Camera size=\{28\} className="text-\[#38bdf8\]" fill="currentColor" fillOpacity="0\.2" \/>\}\s*<\/button>'

code = re.sub(button_pattern, '', code)

# 3. Insert the button BELOW the Forgot QR code button
forgot_qr_pattern = r'(<span className="block text-gray-800 font-bold text-sm">Forgot QR Code\?<\/span>[\s\S]*?<\/button>)'
new_button = """
        {/* AI Snapshot Button (Moved below scanner) */}
        <button
          onClick={handleSnapshotScan}
          disabled={aiLoading}
          className="w-full bg-gradient-to-r from-purple-500 to-indigo-600 text-white py-4 px-4 rounded-[20px] flex items-center justify-center shadow-md z-10 hover:opacity-90 active:scale-95 transition-all mt-4 disabled:opacity-50"
        >
          {aiLoading ? (
            <><Loader2 size={24} className="animate-spin mr-2" /> <span className="font-bold">Analyzing with AI...</span></>
          ) : (
            <><Camera size={24} className="mr-2" /> <span className="font-bold">Take Photo & AI Scan</span></>
          )}
        </button>"""

if re.search(forgot_qr_pattern, code):
    code = re.sub(forgot_qr_pattern, r'\1' + new_button, code)
else:
    print("Failed to find Forgot QR pattern")

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done ScannerTab")
