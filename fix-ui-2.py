import os

emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

old_photo_ui = """                  <div className="text-blue-600 font-bold flex flex-col items-center">
                    <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                    {documentFile ? "Photo Ready! (" + documentFile.name + ")" : "Tap to open Camera & snap ID"}
                  </div>"""

new_photo_ui = """                  <div className="text-blue-600 font-bold flex flex-col items-center justify-center w-full">
                    {documentFile ? (
                      <>
                        <svg className="w-8 h-8 mb-1 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        <span className="text-green-600">Photo Ready!</span>
                        <span className="text-xs text-gray-500 mt-1 max-w-full truncate px-4">{documentFile.name}</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                        Tap to open Camera & snap ID
                      </>
                    )}
                  </div>"""

emp = emp.replace(old_photo_ui, new_photo_ui)
with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(emp)


scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

old_scanner_layout = """    <div className="relative h-screen bg-black overflow-hidden">
      
      {/* Scanner Viewport */}
      <div className="absolute inset-0 z-0 flex items-center justify-center">
        <div id="reader" className="w-full h-full [&>video]:object-cover"></div>
        
        {/* Safe Area Overlay for aesthetic */}
        <div className="absolute inset-0 border-[40px] border-black/40 pointer-events-none"></div>
      </div>"""

new_scanner_layout = """    <div className="relative min-h-screen bg-black flex flex-col items-center justify-center overflow-hidden pb-16">
      
      {/* Scanner Viewport */}
      <div className="w-full max-w-md mx-auto aspect-[3/4] flex items-center justify-center relative bg-gray-900 rounded-3xl overflow-hidden shadow-2xl">
        <div id="reader" className="w-full h-full flex items-center justify-center [&>video]:object-cover"></div>
      </div>"""

scanner = scanner.replace(old_scanner_layout, new_scanner_layout)
with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scanner)

print("Done")
