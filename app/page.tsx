"use client";

import { useState, useEffect } from "react";
import { Users, QrCode, ClipboardList, Settings, Zap, RefreshCw } from "lucide-react";
import ScannerTab from '@/components/ScannerTab';
import EmployeesTab from '@/components/EmployeesTab';
import LogsTab from '@/components/LogsTab';
import SettingsTab from '@/components/SettingsTab';
import ParcelsTab from '@/components/ParcelsTab';
import { Package } from 'lucide-react';
import Image from 'next/image';

export default function Home() {
  const [activeTab, setActiveTab] = useState("scanner");

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
          <button className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#334155] hover:text-blue-600 transition-colors">
            <Zap size={18} className="fill-current" />
          </button>
          <button className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#334155] hover:text-blue-600 transition-colors">
            <RefreshCw size={18} />
          </button>
          <button onClick={() => setActiveTab("settings")} className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#334155] hover:text-blue-600 transition-colors">
            <Settings size={18} className="fill-current" />
          </button>
        </div>
      </header>

      <main className="h-[calc(100vh-140px)] overflow-y-auto relative z-10">
        {activeTab === "scanner" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab />}
        {activeTab === "logs" && <LogsTab />}
        {activeTab === "settings" && <SettingsTab />}
        {activeTab === "parcels" && <ParcelsTab />}
      </main>

      <nav className="fixed bottom-0 w-full max-w-md bg-white border-t border-gray-100 flex justify-around p-3 pb-safe shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.05)] z-20 rounded-t-3xl">
        <button onClick={() => setActiveTab("scanner")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "scanner" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <QrCode size={24} className={activeTab === "scanner" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Scan</span>
        </button>
        <button onClick={() => setActiveTab("employees")} className={`flex flex-col items-center justify-center w-[70px] h-[70px] rounded-[28px] transition-all ${activeTab === "employees" ? "bg-[#EAF3FF] text-[#3B82F6]" : "text-gray-400"}`}>
          <Users size={24} className={activeTab === "employees" ? "stroke-2" : "stroke-2"} />
          <span className="text-[10px] mt-1 font-semibold">Employees</span>
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
      </nav>
    </>
  );
}
