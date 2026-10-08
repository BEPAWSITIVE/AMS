"use client";

import { useState, useEffect } from "react";
import { Users, QrCode, ClipboardList, Settings, Zap, RefreshCw, LogOut } from "lucide-react";
import ScannerTab from '@/components/ScannerTab';
import EmployeesTab from '@/components/EmployeesTab';
import LogsTab from '@/components/LogsTab';
import SettingsTab from '@/components/SettingsTab';
import ParcelsTab from '@/components/ParcelsTab';
import AuthScreen from '@/components/AuthScreen';
import ReportsTab from '@/components/ReportsTab';
import { FileBarChart2 } from 'lucide-react';
import { Package } from 'lucide-react';
import Image from 'next/image';
import { supabase } from "@/lib/supabase";

export default function Home() {
  const [activeTab, setActiveTab] = useState("scanner");
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState<"admin" | "guard">("guard");

  const fetchRole = async (userId: string) => {
    const { data } = await supabase.from('user_roles').select('role').eq('user_id', userId).single();
    if (data && data.role === "admin") {
      setRole("admin");
      if (activeTab === "scanner") setActiveTab("reports");
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
        setActiveTab("scanner");
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center bg-[#F4F9FF]"><div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div></div>;
  }

  if (!session) {
    return <AuthScreen />;
  }

  return (
    <>
      {/* Decorative Background Blobs */}
      <div className="fixed top-20 -left-10 w-48 h-48 -left-20 bg-blue-100 rounded-full opacity-50 z-0"></div>
      <div className="fixed top-40 -right-10 w-56 h-56 -right-28 bg-green-100 rounded-full opacity-50 z-0"></div>

      <header className="bg-[#F4F9FF] p-4 flex justify-between items-center z-10 relative">
        <div className="flex items-center space-x-2">

          <div className="w-10 h-10 rounded-lg shadow-sm border border-gray-100 overflow-hidden">
             <Image src="/logo.jpg" alt="Logo" width={40} height={40} className="object-cover" priority />
          </div>
          <div className="leading-tight">
            <h1 className="text-[17px] font-extrabold text-[#1E293B] tracking-tight">Attendance</h1>
            <h1 className="text-[17px] font-extrabold text-[#10B981] tracking-tight -mt-1">Manager</h1>
            <p className="text-[10px] font-bold text-gray-400 tracking-wider mt-0.5">Track • Manage • Grow</p>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <button onClick={handleLogout} className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-red-500 hover:text-red-600 transition-colors" title="Sign Out">
            <LogOut size={18} className="ml-0.5" />
          </button>

        </div>
      </header>

      <main className="h-[calc(100vh-140px)] overflow-y-auto relative z-10">
        {activeTab === "scanner" && role === "guard" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab role={role} />}
        {activeTab === "logs" && role === "admin" && <LogsTab />}
        {activeTab === "reports" && role === "admin" && <ReportsTab />}
        {activeTab === "settings" && <SettingsTab />}
        {activeTab === "parcels" && role === "guard" && <ParcelsTab role={role} />}
      </main>

      <nav className="fixed bottom-0 w-full max-w-md bg-white border-t border-gray-100 flex justify-around p-3 pb-safe shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.05)] z-20 rounded-t-3xl">
        {role === 'guard' && (
          <button onClick={() => setActiveTab("scanner")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "scanner" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
            <QrCode size={24} className={activeTab === "scanner" ? "stroke-2" : "stroke-2"} />
            <span className="text-[10px] mt-1 font-semibold">Scan</span>
          </button>
        )}
        
        <button onClick={() => setActiveTab("employees")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "employees" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Users size={24} className={activeTab === "employees" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">{role === 'admin' ? 'Registry' : 'Visitors'}</span>
        </button>
        
        {role === 'guard' && (
          <button onClick={() => setActiveTab("parcels")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "parcels" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
            <Package size={24} className={activeTab === "parcels" ? "stroke-2" : "stroke-2"} />
            <span className="text-[10px] mt-1 font-semibold">Parcels</span>
          </button>
        )}
        
        {role === 'admin' && (
          <button onClick={() => setActiveTab("reports")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "reports" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
            <FileBarChart2 size={24} className={activeTab === "reports" ? "stroke-2" : "stroke-2"} />
            <span className="text-[10px] mt-1 font-semibold">Reports</span>
          </button>
        )}
        
        <button onClick={() => setActiveTab("settings")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "settings" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Settings size={24} className={activeTab === "settings" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Settings</span>
        </button>
      </nav>
    </>
  );
}
