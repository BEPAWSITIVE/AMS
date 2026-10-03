"use client";
import { useState } from "react";
import { useLiveQuery } from "dexie-react-hooks";
import { db } from "@/lib/db";
import { QRCodeSVG } from "qrcode.react";

export default function EmployeesTab() {
  const employees = useLiveQuery(() => db.employees.toArray());
  const [showForm, setShowForm] = useState(false);
  
  const [empId, setEmpId] = useState("");
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [phone, setPhone] = useState("");
  const [selectedQR, setSelectedQR] = useState<string | null>(null);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!empId || !name) return;
    
    await db.employees.put({
      empId, name, department, phone, createdAt: new Date().toISOString()
    });
    
    setShowForm(false);
    setEmpId(""); setName(""); setDepartment(""); setPhone("");
  }

  async function handleDelete(id: string) {
    if(confirm("Delete this employee?")) {
      await db.employees.delete(id);
    }
  }

  return (
    <div className="pb-20">
      {showForm ? (
        <div className="p-4 bg-white rounded-xl shadow-md border m-4">
          <h2 className="text-xl font-bold mb-4">Register Employee</h2>
          <form onSubmit={handleAdd} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-500 mb-1">Employee ID *</label>
              <input required value={empId} onChange={e=>setEmpId(e.target.value)} className="w-full border rounded p-2" />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Full Name *</label>
              <input required value={name} onChange={e=>setName(e.target.value)} className="w-full border rounded p-2" />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Department</label>
              <input value={department} onChange={e=>setDepartment(e.target.value)} className="w-full border rounded p-2" />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Phone</label>
              <input value={phone} onChange={e=>setPhone(e.target.value)} className="w-full border rounded p-2" />
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-500">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded shadow">Save</button>
            </div>
          </form>
        </div>
      ) : (
        <>
          <div className="p-4 flex justify-between items-center">
            <h2 className="text-lg font-bold text-gray-700">Staff List</h2>
            <button onClick={() => setShowForm(true)} className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm shadow">
              + Add Employee
            </button>
          </div>
          
          <div className="px-4 space-y-3">
            {employees?.length === 0 && (
              <p className="text-center text-gray-500 py-10">No employees found. Add one to generate a QR code.</p>
            )}
            {employees?.map(emp => (
              <div key={emp.empId} className="bg-white p-3 rounded-lg border shadow-sm flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-gray-800">{emp.name}</h3>
                  <p className="text-sm text-gray-500">{emp.empId} • {emp.department}</p>
                </div>
                <div className="flex space-x-2">
                  <button onClick={() => setSelectedQR(JSON.stringify({ empId: emp.empId, name: emp.name }))} className="bg-blue-50 text-blue-600 px-3 py-1.5 rounded text-sm font-medium">
                    Show QR
                  </button>
                  <button onClick={() => handleDelete(emp.empId)} className="text-red-400 p-1.5">
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {selectedQR && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white p-6 rounded-2xl w-full max-w-xs flex flex-col items-center relative">
            <button onClick={() => setSelectedQR(null)} className="absolute top-3 right-4 text-gray-400 text-xl font-bold">✕</button>
            <h3 className="font-bold text-blue-600 mb-4 tracking-widest text-sm">ATTENDANCE PASS</h3>
            <QRCodeSVG value={selectedQR} size={200} />
            <p className="mt-4 text-gray-400 text-xs">Scan this at the entrance</p>
          </div>
        </div>
      )}
    </div>
  );
}
