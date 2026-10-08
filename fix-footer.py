import os

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add Settings button to footer navigation for everyone
old_nav_end = """        {role === 'admin' && (
          <button onClick={() => setActiveTab("reports")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "reports" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
            <FileBarChart2 size={24} className={activeTab === "reports" ? "stroke-2" : "stroke-2"} />
            <span className="text-[10px] mt-1 font-semibold">Reports</span>
          </button>
        )}
      </nav>"""

new_nav_end = """        {role === 'admin' && (
          <button onClick={() => setActiveTab("reports")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "reports" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
            <FileBarChart2 size={24} className={activeTab === "reports" ? "stroke-2" : "stroke-2"} />
            <span className="text-[10px] mt-1 font-semibold">Reports</span>
          </button>
        )}
        
        <button onClick={() => setActiveTab("settings")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "settings" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Settings size={24} className={activeTab === "settings" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Settings</span>
        </button>
      </nav>"""
code = code.replace(old_nav_end, new_nav_end)

# Also allow SettingsTab rendering for both roles
old_main = """        {activeTab === "settings" && role === "admin" && <SettingsTab />}"""
new_main = """        {activeTab === "settings" && <SettingsTab />}"""
code = code.replace(old_main, new_main)

# And remove it from the header entirely so it's not duplicated
old_header_settings = """          {role === 'admin' && (
            <button onClick={() => setActiveTab("settings")} className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#334155] hover:text-blue-600 transition-colors">
              <Settings size={18} className="fill-current" />
            </button>
          )}"""
code = code.replace(old_header_settings, "")


with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
