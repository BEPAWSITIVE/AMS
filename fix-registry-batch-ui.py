import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

target = r'(<\/form>\s*<\/div>\s*\)\}\s*)({\s*loading \?)'

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
      
      """

if re.search(target, code):
    code = re.sub(target, r'\1' + batch_ui + r'\2', code)
else:
    print("Failed to find target for batch UI")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
