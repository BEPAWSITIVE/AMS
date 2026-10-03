"use client";

import { useState } from "react";
import { Users, QrCode, ClipboardList, Settings } from "lucide-react";
import ScannerTab from '@/components/ScannerTab';
import EmployeesTab from '@/components/EmployeesTab';
import LogsTab from '@/components/LogsTab';
import SettingsTab from '@/components/SettingsTab';

export default function Home() {
  const [activeTab, setActiveTab] = useState("scanner");

  return (
    <>
      <header className="bg-blue-600 text-white p-4 shadow-md flex justify-between items-center z-10 relative">
        <h1 className="text-xl font-bold">Attendance Manager</h1>
      </header>

      <main className="h-[calc(100vh-130px)] overflow-y-auto">
        {activeTab === "scanner" && <ScannerTab />}
        {activeTab === "employees" && <EmployeesTab />}
        {activeTab === "logs" && <LogsTab />}
        {activeTab === "settings" && <SettingsTab />}
      </main>

      <nav className="fixed bottom-0 w-full max-w-md bg-white border-t border-gray-200 flex justify-around p-3 pb-safe shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-10">
        <button onClick={() => setActiveTab("scanner")} className={`flex flex-col items-center ${activeTab === "scanner" ? "text-blue-600" : "text-gray-400"}`}>
          <QrCode size={24} />
          <span className="text-xs mt-1">Scan</span>
        </button>
        <button onClick={() => setActiveTab("employees")} className={`flex flex-col items-center ${activeTab === "employees" ? "text-blue-600" : "text-gray-400"}`}>
          <Users size={24} />
          <span className="text-xs mt-1">Staff</span>
        </button>
        <button onClick={() => setActiveTab("logs")} className={`flex flex-col items-center ${activeTab === "logs" ? "text-blue-600" : "text-gray-400"}`}>
          <ClipboardList size={24} />
          <span className="text-xs mt-1">Logs</span>
        </button>
        <button onClick={() => setActiveTab("settings")} className={`flex flex-col items-center ${activeTab === "settings" ? "text-blue-600" : "text-gray-400"}`}>
          <Settings size={24} />
          <span className="text-xs mt-1">Settings</span>
        </button>
      </nav>
    </>
  );
}
