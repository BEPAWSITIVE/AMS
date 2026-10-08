import os

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add AI Scan button right after the Forgot QR button
target_str = """          <div className="text-gray-400">
            <ChevronRight size={20} />
          </div>
        </button>"""

new_button = """          <div className="text-gray-400">
            <ChevronRight size={20} />
          </div>
        </button>
        
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

code = code.replace(target_str, new_button)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
