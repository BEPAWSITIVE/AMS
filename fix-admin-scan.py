import os

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update fetchRole to swap the active tab
old_fetchRole = """  const fetchRole = async (userId: string) => {
    const { data } = await supabase.from('user_roles').select('role').eq('user_id', userId).single();
    if (data && data.role) {
      setRole(data.role as "admin" | "guard");
    } else {
      setRole("guard");
    }
  };"""
new_fetchRole = """  const fetchRole = async (userId: string) => {
    const { data } = await supabase.from('user_roles').select('role').eq('user_id', userId).single();
    if (data && data.role === "admin") {
      setRole("admin");
      if (activeTab === "scanner") setActiveTab("reports");
    } else {
      setRole("guard");
    }
  };"""
code = code.replace(old_fetchRole, new_fetchRole)

# 2. Update rendering
old_main = """      <main className="h-[calc(100vh-140px)] overflow-y-auto relative z-10">
        {activeTab === "scanner" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab role={role} />}
        {activeTab === "logs" && role === "admin" && <LogsTab />}
        {activeTab === "reports" && role === "admin" && <ReportsTab />}
        {activeTab === "settings" && role === "admin" && <SettingsTab />}
        {activeTab === "parcels" && <ParcelsTab />}
      </main>"""
new_main = """      <main className="h-[calc(100vh-140px)] overflow-y-auto relative z-10">
        {activeTab === "scanner" && role === "guard" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab role={role} />}
        {activeTab === "logs" && role === "admin" && <LogsTab />}
        {activeTab === "reports" && role === "admin" && <ReportsTab />}
        {activeTab === "settings" && role === "admin" && <SettingsTab />}
        {activeTab === "parcels" && <ParcelsTab />}
      </main>"""
code = code.replace(old_main, new_main)

# 3. Update nav to hide Scanner from Admin
old_nav_button = """        <button onClick={() => setActiveTab("scanner")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "scanner" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <QrCode size={24} className={activeTab === "scanner" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Scan</span>
        </button>"""
new_nav_button = """        {role === 'guard' && (
          <button onClick={() => setActiveTab("scanner")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "scanner" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
            <QrCode size={24} className={activeTab === "scanner" ? "stroke-2" : "stroke-2"} />
            <span className="text-[10px] mt-1 font-semibold">Scan</span>
          </button>
        )}"""
code = code.replace(old_nav_button, new_nav_button)

# Also update the AuthStateChange hook to reset the active tab if they log out or switch to guard
old_auth_state = """      if (session) {
        fetchRole(session.user.id);
      } else {
        setRole("guard");
      }"""
new_auth_state = """      if (session) {
        fetchRole(session.user.id);
      } else {
        setRole("guard");
        setActiveTab("scanner");
      }"""
code = code.replace(old_auth_state, new_auth_state)

with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
