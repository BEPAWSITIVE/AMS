import os
import re

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'\s*\{\/\* Button \*\/\}\s*<div className="w-full bg-\[#EAF3FF\] py-4 px-4 rounded-\[20px\] flex items-center justify-between shadow-sm z-10 \s*mb-3">\s*<div className="flex items-center">\s*<div className="bg-\[#3B82F6\] text-white p-2.5 rounded-xl mr-4 shadow-sm">\s*<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" \s*strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"><\/rect><rect x="7" \s*y="7" width="3" height="3"><\/rect><rect x="14" y="7" width="3" height="3"><\/rect><rect x="7" y="14" width="3" \s*height="3"><\/rect><rect x="14" y="14" width="3" height="3"><\/rect><\/svg>\s*<\/div>\s*<span className="text-\[#1E293B\] font-bold text-\[13px\]">Point camera at employee QR badge<\/span>\s*<\/div>\s*<\/div>'

new_code = re.sub(pattern, '', code)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Done")
