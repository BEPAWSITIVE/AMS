import os

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Main area conditionally render ParcelsTab
old_main = """{activeTab === "parcels" && <ParcelsTab role={role} />}"""
new_main = """{activeTab === "parcels" && role === "guard" && <ParcelsTab role={role} />}"""
code = code.replace(old_main, new_main)

# 2. Bottom nav conditionally render Parcels button
old_nav_button = """        <button onClick={() => setActiveTab("parcels")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "parcels" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Package size={24} className={activeTab === "parcels" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Parcels</span>
        </button>"""
new_nav_button = """        {role === 'guard' && (
          <button onClick={() => setActiveTab("parcels")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "parcels" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
            <Package size={24} className={activeTab === "parcels" ? "stroke-2" : "stroke-2"} />
            <span className="text-[10px] mt-1 font-semibold">Parcels</span>
          </button>
        )}"""
code = code.replace(old_nav_button, new_nav_button)

with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
