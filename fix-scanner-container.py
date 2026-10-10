import os

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

target = '        <div className="relative w-full aspect-square bg-gray-100 rounded-[32px] overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.12)] border-[6px] border-[#EAF3FF] z-10 mb-8 mt-4">'
replacement = '        <div id="reader-container" className="relative w-full aspect-square bg-gray-100 rounded-[32px] overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.12)] border-[6px] border-[#EAF3FF] z-10 mb-8 mt-4">'

code = code.replace(target, replacement)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
