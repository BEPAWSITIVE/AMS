import os

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

target = "const generateNewId = (cat: string) => {"

effect_code = """
  useEffect(() => {
    if (initialAiData) {
      setCategory('Visitor');
      generateNewId('Visitor');
      setName(initialAiData.name || "");
      setDepartment(initialAiData.address || "");
      setPhone("+91 ");
      setVehiclePlate("");
      setDocumentFile(null);
      setGroupMembers([initialAiData.id_number || ""]);
      setShowForm(true);
      if (onAiDataConsumed) onAiDataConsumed();
    }
  }, [initialAiData]);
"""

code = code.replace(target, effect_code + '\n  ' + target)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
