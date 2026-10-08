import os

# 1. Update EmployeesTab.tsx
with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('export default function EmployeesTab({ role = "guard" }: { role?: "admin" | "guard" }) {', 'export default function EmployeesTab({ role = "guard", initialAiData, onAiDataConsumed }: { role?: "admin" | "guard", initialAiData?: any, onAiDataConsumed?: () => void }) {')

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

code = code.replace('  useEffect(() => {\n    loadEmployees();\n  }, []);', '  useEffect(() => {\n    loadEmployees();\n  }, []);\n' + effect_code)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)


# 2. Update ParcelsTab.tsx
with open('components/ParcelsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('export default function ParcelsTab({ role = "guard" }: { role?: "admin" | "guard" }) {', 'export default function ParcelsTab({ role = "guard", initialAiData, onAiDataConsumed }: { role?: "admin" | "guard", initialAiData?: any, onAiDataConsumed?: () => void }) {')

effect_code2 = """
  useEffect(() => {
    if (initialAiData) {
      setCompanyName(initialAiData.company_name || "");
      setTargetPerson(initialAiData.recipient_name || "");
      setShowForm(true);
      if (onAiDataConsumed) onAiDataConsumed();
    }
  }, [initialAiData]);
"""

code = code.replace('  useEffect(() => {\n    loadParcels();\n  }, []);', '  useEffect(() => {\n    loadParcels();\n  }, []);\n' + effect_code2)

with open('components/ParcelsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
