import os

emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()
emp = emp.replace('acc.find(item => item.empId === curr.empId)', 'acc.find((item: Employee) => item.empId === curr.empId)')
with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(emp)

print("Done")
