import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix the useEffect hook for initialAiData
target_use_effect = r"(\s*)useEffect\(\(\) => \{\s*if \(initialAiData\) \{\s*setCategory\('Visitor'\);\s*generateNewId\('Visitor'\);\s*setName\(initialAiData\.name \|\| \"\"\);\s*setDepartment\(initialAiData\.address \|\| \"\"\);\s*setPhone\(\"\+91 \"\);\s*setVehiclePlate\(\"\"\);\s*setDocumentFile\(null\);\s*setGroupMembers\(\[initialAiData\.id_number \|\| \"\"\]\);\s*setShowForm\(true\);\s*if \(onAiDataConsumed\) onAiDataConsumed\(\);\s*\}\s*\}, \[initialAiData\]\);"

new_use_effect = r"""\1useEffect(() => {
\1  if (initialAiData) {
\1    setCategory('Visitor');
\1    generateNewId('Visitor');
\1    setName(initialAiData.name || "");
\1    setDepartment(initialAiData.address || "");
\1    setPhone("+91 ");
\1    setVehiclePlate(initialAiData.id_number || "");
\1    setGroupMembers([""]);
\1    
\1    if (initialAiData.capturedImage) {
\1      fetch(initialAiData.capturedImage)
\1        .then(res => res.arrayBuffer())
\1        .then(buf => {
\1          const file = new File([buf], "ai_scan_capture.jpg", { type: "image/jpeg" });
\1          setDocumentFile(file);
\1        }).catch(err => console.error("Error creating file from image", err));
\1    } else {
\1      setDocumentFile(null);
\1    }
\1    
\1    setShowForm(true);
\1    if (onAiDataConsumed) onAiDataConsumed();
\1  }
\1}, [initialAiData]);"""

if re.search(target_use_effect, code):
    code = re.sub(target_use_effect, new_use_effect, code)
    print("Fixed useEffect")
else:
    print("Failed to find useEffect")

# Also, there's a handleBatchAiScan target that I missed?
# Let's check handleBatchAiScan
batch_target = r"if \(category === 'Vehicle'\) setVehiclePlate\(draft\.id_number \|\| \"\"\);\s*else setGroupMembers\(\[draft\.id_number \|\| \"\"\]\);"
batch_new = r"setVehiclePlate(draft.id_number || \"\");\n                      setGroupMembers([\"\"]);"

if re.search(batch_target, code):
    code = re.sub(batch_target, batch_new, code)
    print("Fixed batch scan mapping")
else:
    print("Failed to find batch mapping (maybe it was already fixed?)")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
