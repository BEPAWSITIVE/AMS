import os

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

target = """  const handleAiScan = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAiLoading(true);
    try {
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

        window.dispatchEvent(new CustomEvent('ai_scan_result', { detail: data }));
      };
    } catch (err) {
      alert("AI Scan failed.");
      setAiLoading(false);
    }
  };"""

replacement = """  const compressImage = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        
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
        ctx?.drawImage(img, 0, 0, width, height);
        
        resolve(canvas.toDataURL('image/jpeg', 0.6));
      };
      img.src = URL.createObjectURL(file);
    });
  };

  const handleAiScan = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAiLoading(true);
    try {
      const base64 = await compressImage(file);
      
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
  };"""

code = code.replace(target, replacement)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
