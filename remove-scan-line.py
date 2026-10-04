import sys

content = open('components/ScannerTab.tsx', 'r').read()

scan_line_block = """          {/* Glowing Scan Line overlay */}
          <div className="absolute top-1/2 left-0 w-full h-[2px] bg-blue-400 shadow-[0_0_15px_5px_rgba(59,130,246,0.5)] z-10 opacity-70 animate-pulse"></div>"""

content = content.replace(scan_line_block, "")

open('components/ScannerTab.tsx', 'w').write(content)
print('Done')
