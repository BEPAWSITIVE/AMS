import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()


# 3. Button Injection
button_pattern = r'<div className="flex items-center justify-between mb-2">\s*<h2 className="text-2xl font-bold text-gray-800">Registry<\/h2>\s*<button \s*onClick=\{handleOpenForm\}\s*className="bg-blue-900 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center shadow-md active:scale-95 transition-transform"\s*>\s*\+ Add New\s*<\/button>\s*<\/div>'

new_button = """        <div className="flex items-center justify-between mb-2">
          <h2 className="text-2xl font-bold text-gray-800">Registry</h2>
          <div className="flex items-center space-x-2">
            {role === 'admin' && (
              <>
                <input 
                  type="file" 
                  accept="image/*"
                  capture="environment"
                  ref={fileInputRef}
                  onChange={handleBatchAiScan}
                  className="hidden"
                />
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  disabled={aiLoading}
                  className="bg-purple-100 text-purple-700 px-3 py-2 rounded-xl text-sm font-bold flex items-center shadow-sm active:scale-95 transition-transform border border-purple-200"
                >
                  {aiLoading ? <Loader2 size={18} className="animate-spin mr-1.5" /> : <Camera size={18} className="mr-1.5" />}
                  AI Scan
                </button>
              </>
            )}
            <button 
              onClick={handleOpenForm}
              className="bg-blue-900 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center shadow-md active:scale-95 transition-transform"
            >
              + Add New
            </button>
          </div>
        </div>"""

if re.search(button_pattern, code):
    code = re.sub(button_pattern, new_button, code)
else:
    print("Failed to find button target via regex")


# 4. List header injection (where to put the batch Drafts UI)
list_header_pattern = r'\{\/\* List \*\/\}\s*<div className="space-y-4 pb-20">'

batch_ui = """      {/* Batch Drafts */}
      {batchDrafts.length > 0 && !showForm && (
        <div className="mb-6 p-4 bg-purple-50 rounded-2xl border border-purple-100 shadow-sm animate-fade-in">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-bold text-purple-800 flex items-center"><Sparkles size={16} className="mr-2"/> AI Extracted ({batchDrafts.length})</h3>
            <button onClick={() => setBatchDrafts([])} className="text-purple-400 hover:text-purple-600"><X size={20}/></button>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {batchDrafts.map((draft) => (
              <div key={draft._tempId} className="bg-white p-3 rounded-xl flex justify-between items-center shadow-sm border border-purple-100">
                <div className="overflow-hidden">
                  <p className="font-bold text-sm text-gray-800 truncate">{draft.name || 'Unknown Name'}</p>
                  <p className="text-[11px] text-gray-500 font-medium truncate">{draft.phone || 'No Phone'} • {draft.id_number || 'No ID'}</p>
                </div>
                <button 
                  onClick={() => {
                    handleOpenForm();
                    setName(draft.name || "");
                    setPhone(draft.phone?.startsWith("+91") ? draft.phone : "+91 " + (draft.phone || ""));
                    if (category === 'Vehicle') setVehiclePlate(draft.id_number || "");
                    else setGroupMembers([draft.id_number || ""]);
                    setDepartment(draft.address || "");
                    // Remove from drafts so it's not processed twice
                    setBatchDrafts(prev => prev.filter(d => d._tempId !== draft._tempId));
                  }}
                  className="ml-2 px-3 py-1.5 bg-purple-600 text-white text-xs font-bold rounded-lg shadow-sm whitespace-nowrap active:scale-95"
                >
                  Review & Save
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* List */}
      <div className="space-y-4 pb-20">"""

if re.search(list_header_pattern, code):
    code = re.sub(list_header_pattern, batch_ui, code)
else:
    # If {/* List */} is missing, maybe it's something else. Let's find: `<div className="relative">` below `<div className="mb-4">`
    fallback_pattern = r'<div className="mb-4">\s*<div className="relative">'
    if re.search(fallback_pattern, code):
         code = re.sub(fallback_pattern, batch_ui.replace('{/* List */}\n      <div className="space-y-4 pb-20">', '<div className="mb-4">\n        <div className="relative">'), code)
    else:
         print("Failed to find list header target via regex")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
