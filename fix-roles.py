import os

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Imports
code = code.replace("import AuthScreen from '@/components/AuthScreen';", "import AuthScreen from '@/components/AuthScreen';\nimport ReportsTab from '@/components/ReportsTab';\nimport { FileBarChart2 } from 'lucide-react';")

# 2. Add role state and fetch logic
old_states = """  const [activeTab, setActiveTab] = useState("scanner");
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);"""

new_states = """  const [activeTab, setActiveTab] = useState("scanner");
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState<"admin" | "guard">("guard");

  const fetchRole = async (userId: string) => {
    const { data } = await supabase.from('user_roles').select('role').eq('user_id', userId).single();
    if (data && data.role) {
      setRole(data.role as "admin" | "guard");
    } else {
      setRole("guard");
    }
  };

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) fetchRole(session.user.id);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) {
        fetchRole(session.user.id);
      } else {
        setRole("guard");
      }
    });

    return () => subscription.unsubscribe();
  }, []);"""
code = code.replace(old_states, new_states)

# 3. Main render logic
old_main = """      <main className="h-[calc(100vh-140px)] overflow-y-auto relative z-10">
        {activeTab === "scanner" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab />}
        {activeTab === "logs" && <LogsTab />}
        {activeTab === "settings" && <SettingsTab />}
        {activeTab === "parcels" && <ParcelsTab />}
      </main>"""
new_main = """      <main className="h-[calc(100vh-140px)] overflow-y-auto relative z-10">
        {activeTab === "scanner" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab role={role} />}
        {activeTab === "logs" && role === "admin" && <LogsTab />}
        {activeTab === "reports" && role === "admin" && <ReportsTab />}
        {activeTab === "settings" && role === "admin" && <SettingsTab />}
        {activeTab === "parcels" && <ParcelsTab />}
      </main>"""
code = code.replace(old_main, new_main)

# 4. Nav rendering
old_nav = """      <nav className="fixed bottom-0 w-full max-w-md bg-white border-t border-gray-100 flex justify-around p-3 pb-safe shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.05)] z-20 rounded-t-3xl">
        <button onClick={() => setActiveTab("scanner")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "scanner" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <QrCode size={24} className={activeTab === "scanner" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Scan</span>
        </button>
        <button onClick={() => setActiveTab("employees")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "employees" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Users size={24} className={activeTab === "employees" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Registry</span>
        </button>
        <button onClick={() => setActiveTab("parcels")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "parcels" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Package size={24} className={activeTab === "parcels" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Parcels</span>
        </button>
        <button onClick={() => setActiveTab("logs")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "logs" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <ClipboardList size={24} className={activeTab === "logs" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Logs</span>
        </button>
        <button onClick={() => setActiveTab("settings")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "settings" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Settings size={24} className={activeTab === "settings" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Settings</span>
        </button>
      </nav>"""

new_nav = """      <nav className="fixed bottom-0 w-full max-w-md bg-white border-t border-gray-100 flex justify-around p-3 pb-safe shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.05)] z-20 rounded-t-3xl">
        <button onClick={() => setActiveTab("scanner")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "scanner" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <QrCode size={24} className={activeTab === "scanner" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Scan</span>
        </button>
        
        <button onClick={() => setActiveTab("employees")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "employees" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Users size={24} className={activeTab === "employees" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">{role === 'admin' ? 'Registry' : 'Visitors'}</span>
        </button>
        
        <button onClick={() => setActiveTab("parcels")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "parcels" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Package size={24} className={activeTab === "parcels" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Parcels</span>
        </button>
        
        {role === 'admin' && (
          <button onClick={() => setActiveTab("reports")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "reports" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
            <FileBarChart2 size={24} className={activeTab === "reports" ? "stroke-2" : "stroke-2"} />
            <span className="text-[10px] mt-1 font-semibold">Reports</span>
          </button>
        )}
      </nav>"""
code = code.replace(old_nav, new_nav)

# Hide settings and logs from top header for guards
old_header_btn = """          <button onClick={() => setActiveTab("settings")} className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#334155] hover:text-blue-600 transition-colors">
            <Settings size={18} className="fill-current" />
          </button>"""
new_header_btn = """          {role === 'admin' && (
            <button onClick={() => setActiveTab("settings")} className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#334155] hover:text-blue-600 transition-colors">
              <Settings size={18} className="fill-current" />
            </button>
          )}"""
code = code.replace(old_header_btn, new_header_btn)


with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
