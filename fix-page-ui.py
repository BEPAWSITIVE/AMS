import os

page = open('app/page.tsx', 'r', encoding='utf-8').read()

old_title = """          <div className="leading-tight">
            <h1 className="text-[17px] font-extrabold text-[#1E293B] tracking-tight">Attendance</h1>
            <h1 className="text-[17px] font-extrabold text-[#2DD4BF] tracking-tight -mt-1">Manager</h1>
          </div>"""

new_title = """          <div className="leading-tight">
            <h1 className="text-[17px] font-extrabold text-[#1E293B] tracking-tight">Attendance</h1>
            <h1 className="text-[17px] font-extrabold text-[#10B981] tracking-tight -mt-1">Manager</h1>
            <p className="text-[10px] font-bold text-gray-400 tracking-wider mt-0.5">Track • Manage • Grow</p>
          </div>"""

page = page.replace(old_title, new_title)

# The flash icon in mockup has a circle background and is dark. The settings icon is also dark.
# The mockup icons are:
# Lightning bolt (Flash)
# Refresh
# Settings (Gear)

old_icons = """        <div className="flex space-x-2">
          <button className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#64748B] hover:text-blue-600">
            <Zap size={20} className="fill-current" />
          </button>
          <button className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#64748B] hover:text-blue-600">
            <RefreshCw size={20} />
          </button>
          <button onClick={() => setActiveTab("settings")} className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#64748B] hover:text-blue-600">
            <Settings size={20} />
          </button>
        </div>"""

new_icons = """        <div className="flex space-x-2">
          <button className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#334155] hover:text-blue-600 transition-colors">
            <Zap size={18} className="fill-current" />
          </button>
          <button className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#334155] hover:text-blue-600 transition-colors">
            <RefreshCw size={18} />
          </button>
          <button onClick={() => setActiveTab("settings")} className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#334155] hover:text-blue-600 transition-colors">
            <Settings size={18} className="fill-current" />
          </button>
        </div>"""

page = page.replace(old_icons, new_icons)

with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(page)

print("Done")
