import sys

content = open('components/ScannerTab.tsx', 'r').read()

corner_brackets = """          {/* Decorative Corner Brackets */}
          <div className="absolute inset-0 pointer-events-none p-6 flex flex-col justify-between z-10">
            <div className="flex justify-between">
              <div className="w-12 h-12 border-l-4 border-t-4 border-[#3B82F6] rounded-tl-xl"></div>
              <div className="w-12 h-12 border-r-4 border-t-4 border-[#3B82F6] rounded-tr-xl"></div>
            </div>
            <div className="flex justify-between">
              <div className="w-12 h-12 border-l-4 border-b-4 border-[#3B82F6] rounded-bl-xl"></div>
              <div className="w-12 h-12 border-r-4 border-b-4 border-[#3B82F6] rounded-br-xl"></div>
            </div>
          </div>"""

qr_reticle = """          {/* Center QR Reticle Icon */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
            <QrCode className="text-white opacity-40" size={60} strokeWidth={1.5} />
          </div>"""

content = content.replace(corner_brackets, "")
content = content.replace(qr_reticle, "")

open('components/ScannerTab.tsx', 'w').write(content)
print('Done')
