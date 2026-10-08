import os

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add aiLoading state
code = code.replace('const [isSearching, setIsSearching] = useState(false);', 'const [isSearching, setIsSearching] = useState(false);\n  const [aiLoading, setAiLoading] = useState(false);')

# 2. Add handleAiScan method
target = '  const handleManualSearch = (e: React.FormEvent) => { e.preventDefault(); };'

ai_scan_method = """  const handleAiScan = async (e: React.ChangeEvent<HTMLInputElement>) => {
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

code = code.replace(target, ai_scan_method + '\n\n' + target)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
