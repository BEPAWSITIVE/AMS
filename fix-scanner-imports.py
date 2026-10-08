import os

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('from "lucide-react";', ', Loader2, Sparkles } from "lucide-react";')

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
