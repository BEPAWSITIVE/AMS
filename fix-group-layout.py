import os

emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

# 1. State for group members
if "groupMembers" not in emp:
    emp = emp.replace('const [documentFile, setDocumentFile] = useState<File | null>(null);', 
                      'const [documentFile, setDocumentFile] = useState<File | null>(null);\n  const [groupMembers, setGroupMembers] = useState<string[]>([""]);')

    emp = emp.replace('setDocumentFile(null);', 'setDocumentFile(null);\n    setGroupMembers([""]);')
    
    # 2. Update newEmp payload
    old_payload = """    const newEmp: Employee = {
      empId, 
      name, 
      department, 
      phone, 
      category,
      document_url: document_url || undefined,
      vehicle_plate: category === 'Vehicle' ? vehiclePlate : undefined,
      createdAt: new Date().toISOString()
    };"""
    
    new_payload = """    const filteredGroup = groupMembers.filter(m => m.trim() !== "");
    const newEmp: Employee = {
      empId, 
      name, 
      department, 
      phone, 
      category,
      document_url: document_url || undefined,
      vehicle_plate: category === 'Vehicle' ? vehiclePlate : undefined,
      group_members: filteredGroup.length > 0 ? filteredGroup.join(", ") : undefined,
      createdAt: new Date().toISOString()
    };"""
    
    emp = emp.replace(old_payload, new_payload)

    # 3. Form UI for document and group members
    old_visitor_ui = """            {category === 'Visitor' && (
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
                  <div className="text-blue-600 font-bold flex flex-col items-center justify-center w-full">
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
                  </div>
                </div>
              </div>
            )}"""

    new_visitor_ui = """            {category === 'Visitor' && (
              <>
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-1">ID Document (Optional Photo)</label>
                  <div className="relative w-full bg-blue-50 border-2 border-dashed border-blue-200 p-4 rounded-xl text-center hover:bg-blue-100 transition-colors">
                    <input 
                      type="file" 
                      accept="image/*"
                      capture="environment"
                      onChange={e => e.target.files && setDocumentFile(e.target.files[0])}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <div className="text-blue-600 font-bold flex flex-col items-center justify-center w-full">
                      {documentFile ? (
                        <>
                          <svg className="w-8 h-8 mb-1 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                          <span className="text-green-600">Photo Ready!</span>
                          <span className="text-xs text-gray-500 mt-1 max-w-full truncate px-4">{documentFile.name}</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                          Tap to open Camera (Optional)
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-gray-100">
                  <label className="block text-xs font-bold text-gray-500">Group Members (Optional)</label>
                  {groupMembers.map((member, idx) => (
                    <div key={idx} className="flex space-x-2">
                      <input 
                        type="text" 
                        value={member}
                        onChange={(e) => {
                          const newMembers = [...groupMembers];
                          newMembers[idx] = e.target.value;
                          setGroupMembers(newMembers);
                        }}
                        placeholder={`Member ${idx + 1} Name`}
                        className="flex-1 bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      />
                    </div>
                  ))}
                  <button 
                    type="button" 
                    onClick={() => setGroupMembers([...groupMembers, ""])}
                    className="text-xs font-bold text-blue-600 hover:text-blue-800 bg-blue-50 px-3 py-1.5 rounded-lg"
                  >
                    + Add another person
                  </button>
                </div>
              </>
            )}"""

    emp = emp.replace(old_visitor_ui, new_visitor_ui)

    # 4. Display group members in the ID Card Modal
    old_modal_display = """              <h2 className="text-2xl font-bold text-gray-800 text-center">{selectedEmployee.name}</h2>
              <p className="text-gray-500 font-mono mt-1">{selectedEmployee.empId}</p>
              
              {selectedEmployee.document_url && (
                <a 
                  href={selectedEmployee.document_url} 
                  target="_blank" 
                  rel="noreferrer"
                  className="mt-4 text-sm text-blue-600 font-medium flex items-center bg-blue-50 px-4 py-2 rounded-lg"
                >
                  <FileText size={16} className="mr-2" /> View Attached Document
                </a>
              )}"""

    new_modal_display = """              <h2 className="text-2xl font-bold text-gray-800 text-center">{selectedEmployee.name}</h2>
              <p className="text-gray-500 font-mono mt-1">{selectedEmployee.empId}</p>

              {selectedEmployee.group_members && (
                <div className="mt-3 bg-gray-50 p-3 rounded-xl w-full text-center border border-gray-100">
                  <span className="text-xs font-bold text-gray-500 uppercase tracking-wide block mb-1">Group Members</span>
                  <span className="text-sm font-medium text-gray-700">{selectedEmployee.group_members}</span>
                </div>
              )}
              
              {selectedEmployee.document_url && (
                <a 
                  href={selectedEmployee.document_url} 
                  target="_blank" 
                  rel="noreferrer"
                  className="mt-4 text-sm text-blue-600 font-medium flex items-center bg-blue-50 px-4 py-2 rounded-lg"
                >
                  <FileText size={16} className="mr-2" /> View Attached Document
                </a>
              )}"""
    
    emp = emp.replace(old_modal_display, new_modal_display)

    with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
        f.write(emp)

# 5. Fix Scanner Layout (Full Screen)
scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

old_scanner_layout = """    <div className="relative min-h-screen bg-black flex flex-col items-center justify-center overflow-hidden pb-16">
      
      {/* Scanner Viewport */}
      <div className="w-full max-w-md mx-auto aspect-[3/4] flex items-center justify-center relative bg-gray-900 rounded-3xl overflow-hidden shadow-2xl">
        <div id="reader" className="w-full h-full flex items-center justify-center [&>video]:object-cover"></div>
      </div>"""

new_scanner_layout = """    <div className="fixed inset-0 bg-black z-0 overflow-hidden flex items-center justify-center">
      
      {/* Scanner Viewport */}
      <div id="reader" className="w-full h-full [&>video]:object-cover"></div>"""

scanner = scanner.replace(old_scanner_layout, new_scanner_layout)

# remove the extra closing div of the old flex-col layout?
# wait, my old layout was:
#    <div className="relative min-h-screen bg-black flex flex-col items-center justify-center overflow-hidden pb-16">
#      <div className="...">
#        <div id="reader" className="..."></div>
#      </div>
#      {/* Result Toast */}
# If I change it to `fixed inset-0`, the outer div is fine. But I removed the inner div wrapper, so I must remove its closing div.
# Instead of risking a syntax error with unbalanced divs, I'll just change the classes on the inner div to span full screen.

old_scanner_layout = """    <div className="relative min-h-screen bg-black flex flex-col items-center justify-center overflow-hidden pb-16">
      
      {/* Scanner Viewport */}
      <div className="w-full max-w-md mx-auto aspect-[3/4] flex items-center justify-center relative bg-gray-900 rounded-3xl overflow-hidden shadow-2xl">
        <div id="reader" className="w-full h-full flex items-center justify-center [&>video]:object-cover"></div>
      </div>"""

new_scanner_layout = """    <div className="absolute inset-0 bg-black z-0 overflow-hidden pb-20">
      
      {/* Scanner Viewport */}
      <div className="absolute inset-0 flex items-center justify-center z-0">
        <div id="reader" className="w-full h-full [&>video]:object-cover"></div>
      </div>"""

scanner = scanner.replace(old_scanner_layout, new_scanner_layout)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scanner)

print("Done")
