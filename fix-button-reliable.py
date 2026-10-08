import os

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# I will find the exact button tag closure for the manual search button
# Let's search for "ChevronRight size={20} />" and replace up to the next "</button>"

import re

pattern = r'(<ChevronRight size=\{20\} \/>\s*<\/div>\s*<\/button>)'

new_button = """\\1
        
        <div className="relative w-full mt-4">
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
            className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-4 rounded-2xl font-bold shadow-[0_10px_20px_-10px_rgba(99,102,241,0.5)] hover:opacity-90 flex items-center justify-center transition-opacity"
          >
            {aiLoading ? (
              <><Loader2 size={20} className="mr-2 animate-spin" /> Analyzing Image...</>
            ) : (
              <><Sparkles size={20} className="mr-2" /> Auto-Scan ID or Parcel with AI</>
            )}
          </button>
        </div>"""

if re.search(pattern, code):
    new_code = re.sub(pattern, new_button, code)
    with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("SUCCESS: Button injected!")
else:
    print("ERROR: Could not find the pattern!")
