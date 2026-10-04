import os

emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

old_link_logic = """                      const { data: { publicUrl } } = supabase
                        .storage
                        .from('qr-passes')
                        .getPublicUrl(fileName);

                      const cleanPhone = (selectedEmployee.phone || '').replace(/\\D/g,'');
                      const msg = `Hello ${selectedEmployee.name}, here is your digital Attendance QR Pass!\\n\\nClick the secure link below to view and download your pass:\\n${publicUrl}`;
                      const waUrl = `https://wa.me/${cleanPhone}?text=` + encodeURIComponent(msg);"""

new_link_logic = """                      const passPageUrl = `${window.location.origin}/pass/${fileName}`;
                      
                      const cleanPhone = (selectedEmployee.phone || '').replace(/\\D/g,'');
                      const msg = `Hello ${selectedEmployee.name},\\n\\nOpen the link to view your QR pass and download it:\\n${passPageUrl}`;
                      const waUrl = `https://wa.me/${cleanPhone}?text=` + encodeURIComponent(msg);"""

emp = emp.replace(old_link_logic, new_link_logic)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(emp)

print("Done")
