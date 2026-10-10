import os

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add handleSnapshotScan method
target_method = "  const compressImage = (file: File): Promise<string> => {"

snapshot_method = """  const handleSnapshotScan = async () => {
    if (aiLoading) return;
    
    const video = document.querySelector('#reader video') as HTMLVideoElement;
    if (!video) {
      alert("Camera feed not found. Please wait for the camera to start.");
      return;
    }

    setAiLoading(true);
    try {
      const canvas = document.createElement('canvas');
      let width = video.videoWidth;
      let height = video.videoHeight;
      
      const MAX_DIM = 1024;
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
      ctx?.drawImage(video, 0, 0, width, height);
      
      const base64 = canvas.toDataURL('image/jpeg', 0.6);
      
      // Flash effect
      const flash = document.createElement('div');
      flash.className = 'absolute inset-0 bg-white z-[100] animate-pulse';
      document.getElementById('reader-container')?.appendChild(flash);
      setTimeout(() => flash.remove(), 200);

      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ images: [base64] })
      });
      
      if (!res.ok) {
        let errorTxt = "Unknown error";
        try {
          const errData = await res.json();
          errorTxt = errData.error || errData.message || res.statusText;
        } catch(e) {
          errorTxt = await res.text();
        }
        alert("Server Error: " + errorTxt.substring(0, 100));
        setAiLoading(false);
        return;
      }
      
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

      window.dispatchEvent(new CustomEvent('ai_scan_result', { detail: data }));
    } catch (err: any) {
      alert("AI Scan failed: " + err.message);
      setAiLoading(false);
    }
  };
"""

code = code.replace(target_method, snapshot_method + '\n' + target_method)

# 2. Add id="reader-container" to the container and the button
old_camera_container = """        {/* Embedded Square Camera Viewport */}
        <div className="relative w-full aspect-square bg-gray-100 rounded-[32px] overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.12)] border-[6px] border-[#EAF3FF] z-10 mb-8 mt-4">
          
          <div id="reader" className="w-full h-full [&>video]:object-cover [&>video]:w-full [&>video]:h-full"></div>
          
          {/* Cyan Brackets Overlay */}
          <div className="absolute inset-0 pointer-events-none p-6">"""

new_camera_container = """        {/* Embedded Square Camera Viewport */}
        <div id="reader-container" className="relative w-full aspect-square bg-gray-100 rounded-[32px] overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.12)] border-[6px] border-[#EAF3FF] z-10 mb-8 mt-4">
          
          <div id="reader" className="w-full h-full [&>video]:object-cover [&>video]:w-full [&>video]:h-full"></div>
          
          {/* Cyan Brackets Overlay */}
          <div className="absolute inset-0 pointer-events-none p-6">"""
code = code.replace(old_camera_container, new_camera_container)

# Put the camera button at the bottom of the camera container
old_brackets_end = """              <div className="absolute bottom-0 right-0 w-12 h-12 border-b-[4px] border-r-[4px] border-[#38bdf8] rounded-br-3xl"></div>
            </div>
          </div>
        </div>"""

new_brackets_end = """              <div className="absolute bottom-0 right-0 w-12 h-12 border-b-[4px] border-r-[4px] border-[#38bdf8] rounded-br-3xl"></div>
            </div>
          </div>

          {/* AI Snapshot Button */}
          <button
            onClick={handleSnapshotScan}
            disabled={aiLoading}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 w-16 h-16 bg-white/90 backdrop-blur-md rounded-full shadow-xl border-4 border-[#38bdf8] flex items-center justify-center active:scale-95 transition-all z-20 disabled:opacity-50"
          >
            {aiLoading ? <Loader2 size={28} className="text-[#38bdf8] animate-spin" /> : <Camera size={28} className="text-[#38bdf8]" />}
          </button>
        </div>"""
code = code.replace(old_brackets_end, new_brackets_end)


# 3. Remove the old purple button at the bottom
old_bottom_button = """        <div className="relative w-full mt-4">
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

code = code.replace(old_bottom_button, "")

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
