"use client";

import { useState, useEffect } from "react";
import { Users, QrCode, ClipboardList, Settings, Zap, RefreshCw } from "lucide-react";
import ScannerTab from '@/components/ScannerTab';
import EmployeesTab from '@/components/EmployeesTab';
import LogsTab from '@/components/LogsTab';
import SettingsTab from '@/components/SettingsTab';
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
          {/* We'll use a placeholder icon for the logo if we don't have the exact image */}
          <div className="w-10 h-10 bg-white rounded-lg shadow-sm border border-gray-100 flex items-center justify-center relative">
             <ClipboardList className="text-blue-900" size={24} />
             <div className="absolute -bottom-1 -right-1 bg-green-500 rounded-full w-4 h-4 flex items-center justify-center border-2 border-white">
                <span className="text-white text-[8px] font-bold">✓</span>
             </div>
          </div>
          <div className="leading-tight">
            <h1 className="text-[17px] font-extrabold text-[#1E293B] tracking-tight">Attendance</h1>
            <h1 className="text-[17px] font-extrabold text-[#2DD4BF] tracking-tight -mt-1">Manager</h1>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <button className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#64748B] hover:text-blue-600">
            <Zap size={20} className="fill-current" />
          </button>
          <button className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#64748B] hover:text-blue-600">
            <RefreshCw size={20} />
          </button>
          <button onClick={() => setActiveTab("settings")} className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center text-[#64748B] hover:text-blue-600">
            <Settings size={20} />
          </button>
        </div>
      </header>

      <main className="h-[calc(100vh-140px)] overflow-y-auto relative z-10">
        {activeTab === "scanner" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab />}
        {activeTab === "logs" && <LogsTab />}
        {activeTab === "settings" && <SettingsTab />}
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
