import os

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add states for AI prefill
old_states = """  const [role, setRole] = useState<"admin" | "guard">("guard");"""
new_states = """  const [role, setRole] = useState<"admin" | "guard">("guard");
  const [aiVisitorData, setAiVisitorData] = useState<any>(null);
  const [aiParcelData, setAiParcelData] = useState<any>(null);"""
code = code.replace(old_states, new_states)

# Add event listener in useEffect
old_effect = """    return () => subscription.unsubscribe();
  }, []);"""

new_effect = """    const handleAiScan = (e: any) => {
      const data = e.detail;
      if (data.type === 'visitor') {
        setAiVisitorData(data);
        setActiveTab('employees');
      } else if (data.type === 'parcel') {
        setAiParcelData(data);
        setActiveTab('parcels');
      }
    };
    
    window.addEventListener('ai_scan_result', handleAiScan);

    return () => {
      subscription.unsubscribe();
      window.removeEventListener('ai_scan_result', handleAiScan);
    };
  }, []);"""
code = code.replace(old_effect, new_effect)

# Pass data down
old_main = """        {activeTab === "scanner" && role === "guard" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab role={role} />}
        {activeTab === "logs" && role === "admin" && <LogsTab />}
        {activeTab === "reports" && role === "admin" && <ReportsTab />}
        {activeTab === "settings" && <SettingsTab />}
        {activeTab === "parcels" && role === "guard" && <ParcelsTab role={role} />}"""

new_main = """        {activeTab === "scanner" && role === "guard" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab role={role} initialAiData={aiVisitorData} onAiDataConsumed={() => setAiVisitorData(null)} />}
        {activeTab === "logs" && role === "admin" && <LogsTab />}
        {activeTab === "reports" && role === "admin" && <ReportsTab />}
        {activeTab === "settings" && <SettingsTab />}
        {activeTab === "parcels" && role === "guard" && <ParcelsTab role={role} initialAiData={aiParcelData} onAiDataConsumed={() => setAiParcelData(null)} />}"""
code = code.replace(old_main, new_main)

with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
