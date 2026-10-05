import os

# 1. Fix typo in ParcelsTab
parcels_tab = open('components/ParcelsTab.tsx', 'r', encoding='utf-8').read()
parcels_tab = parcels_tab.replace('p.recipientName', 'p.recipient_name')
with open('components/ParcelsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(parcels_tab)

# 2. Add Parcels to app/page.tsx
page = open('app/page.tsx', 'r', encoding='utf-8').read()

if "import ParcelsTab" not in page:
    page = page.replace("import SettingsTab from '@/components/SettingsTab';", "import SettingsTab from '@/components/SettingsTab';\nimport ParcelsTab from '@/components/ParcelsTab';\nimport { Package } from 'lucide-react';")

    page = page.replace('{activeTab === "settings" && <SettingsTab />}', '{activeTab === "settings" && <SettingsTab />}\n        {activeTab === "parcels" && <ParcelsTab />}')

    # Update nav bar
    old_nav = """        <button onClick={() => setActiveTab("logs")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "logs" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <ClipboardList size={24} className={activeTab === "logs" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Logs</span>
        </button>"""

    new_nav = """        <button onClick={() => setActiveTab("parcels")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "parcels" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Package size={24} className={activeTab === "parcels" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Parcels</span>
        </button>
        <button onClick={() => setActiveTab("logs")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "logs" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <ClipboardList size={24} className={activeTab === "logs" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Logs</span>
        </button>"""

    page = page.replace(old_nav, new_nav)
    
    # Since we have 5 icons, they might be cramped. Nav width is full. 70px each = 350px. Max-w-md is 448px. It fits fine.
    
    with open('app/page.tsx', 'w', encoding='utf-8') as f:
        f.write(page)

# 3. Clean EmployeesTab
emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()
emp = emp.replace('<option value="Parcel">Parcel / Delivery</option>', '')
with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(emp)

print("Done")
