import os

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_export = 'export default function EmployeesTab({ role = "admin" }: { role?: "admin" | "guard" }) {'
new_export = 'export default function EmployeesTab({ role = "admin", initialAiData, onAiDataConsumed }: { role?: "admin" | "guard", initialAiData?: any, onAiDataConsumed?: () => void }) {'

code = code.replace(old_export, new_export)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
