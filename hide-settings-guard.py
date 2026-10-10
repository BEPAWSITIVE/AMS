import os

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update the tab render
target_tab = '{activeTab === "settings" && <SettingsTab />}'
replacement_tab = '{activeTab === "settings" && role === "admin" && <SettingsTab />}'
code = code.replace(target_tab, replacement_tab)

# 2. Update the Nav bar settings button
target_nav = """        <button onClick={() => setActiveTab("settings")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "settings" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Settings size={24} className={activeTab === "settings" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Settings</span>
        </button>"""

replacement_nav = """        {role === 'admin' && (
          <button onClick={() => setActiveTab("settings")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "settings" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
            <Settings size={24} className={activeTab === "settings" ? "stroke-2" : "stroke-2"} />
            <span className="text-[10px] mt-1 font-semibold">Settings</span>
          </button>
        )}"""
code = code.replace(target_nav, replacement_nav)

with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
