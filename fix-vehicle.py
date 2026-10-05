import os

emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

emp = emp.replace('<option value="Vehicle">Rescue Vehicle</option>', '<option value="Vehicle">Vehicle</option>')

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(emp)

print("Done")
