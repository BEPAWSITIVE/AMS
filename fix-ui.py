import os

# 1. Update ScannerTab Layout
scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

old_layout = """    <div className="relative min-h-screen bg-black flex flex-col pb-20">
      
      {/* Scanner Viewport */}
      <div className="flex-1 w-full flex items-center justify-center overflow-hidden relative">
        <div id="reader" className="w-full h-full object-cover"></div>
        
        {/* Safe Area Overlay for aesthetic */}
        <div className="absolute inset-0 border-[40px] border-black/40 pointer-events-none"></div>
      </div>"""

new_layout = """    <div className="relative h-screen bg-black overflow-hidden">
      
      {/* Scanner Viewport */}
      <div className="absolute inset-0 z-0 flex items-center justify-center">
        <div id="reader" className="w-full h-full [&>video]:object-cover"></div>
        
        {/* Safe Area Overlay for aesthetic */}
        <div className="absolute inset-0 border-[40px] border-black/40 pointer-events-none"></div>
      </div>"""

scanner = scanner.replace(old_layout, new_layout)
with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scanner)

# 2. Update EmployeesTab (+91 default and camera UI)
emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

# Default +91
emp = emp.replace('const [phone, setPhone] = useState("");', 'const [phone, setPhone] = useState("+91 ");')
emp = emp.replace('setPhone("");', 'setPhone("+91 ");')

# Camera button
old_camera = """            {category === 'Visitor' && (
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">ID Document (Aadhaar/Photo)</label>
                <input 
                  type="file" 
                  accept="image/*"
                  capture="environment"
                  onChange={e => e.target.files && setDocumentFile(e.target.files[0])}
                  className="w-full bg-gray-50 border border-gray-200 p-2 rounded-xl text-sm"
                />
              </div>
            )}"""

new_camera = """            {category === 'Visitor' && (
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">ID Document (Take Photo)</label>
                <div className="relative w-full bg-blue-50 border-2 border-dashed border-blue-200 p-4 rounded-xl text-center hover:bg-blue-100 transition-colors">
                  <input 
                    type="file" 
                    accept="image/*"
                    capture="environment"
                    onChange={e => e.target.files && setDocumentFile(e.target.files[0])}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    required
                  />
                  <div className="text-blue-600 font-bold flex flex-col items-center">
                    <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                    {documentFile ? "Photo Ready! (" + documentFile.name + ")" : "Tap to open Camera & snap ID"}
                  </div>
                </div>
              </div>
            )}"""

emp = emp.replace(old_camera, new_camera)
with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(emp)

print("Done")
