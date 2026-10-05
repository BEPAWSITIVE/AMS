import os

# 1. Update lib/supabase.ts
supa = open('lib/supabase.ts', 'r', encoding='utf-8').read()
supa = supa.replace('meter_in?: number;', 'meter_in?: number;\n  location?: string;')
with open('lib/supabase.ts', 'w', encoding='utf-8') as f:
    f.write(supa)

# 2. Update ScannerTab.tsx
scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

# Add visitedLocation state
scanner = scanner.replace('const [meterReading, setMeterReading] = useState("");', 'const [meterReading, setMeterReading] = useState("");\n  const [visitedLocation, setVisitedLocation] = useState("");')

# Add location to updatedRecord
old_update = """      const updatedRecord = {
        ...lastRecord,
        outTime: timeStr,
        outTimestamp: today.getTime(),
        meter_in: meterIn,
        totalHours: `${consumed} units consumed`,
        status: 'OUT',
        isSynced: navigator.onLine ? 1 : 0,
        updatedAt: today.toISOString()
      };"""
new_update = """      const updatedRecord = {
        ...lastRecord,
        outTime: timeStr,
        outTimestamp: today.getTime(),
        meter_in: meterIn,
        location: visitedLocation,
        totalHours: `${consumed} units consumed`,
        status: 'OUT',
        isSynced: navigator.onLine ? 1 : 0,
        updatedAt: today.toISOString()
      };"""
scanner = scanner.replace(old_update, new_update)

# Add reset to setVisitedLocation
scanner = scanner.replace('setMeterReading("");', 'setMeterReading("");\n    setVisitedLocation("");')

# Add field to Returning Vehicle modal
old_return_modal = """                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Return Meter Reading *</label>
                    <input 
                      type="number" 
                      step="any"
                      value={meterReading}
                      onChange={e => setMeterReading(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-emerald-500 font-mono"
                      required
                    />
                  </div>"""

new_return_modal = """                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Return Meter Reading *</label>
                    <input 
                      type="number" 
                      step="any"
                      value={meterReading}
                      onChange={e => setMeterReading(e.target.value)}
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-emerald-500 font-mono mb-3"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">Location Visited *</label>
                    <input 
                      type="text" 
                      value={visitedLocation}
                      onChange={e => setVisitedLocation(e.target.value)}
                      placeholder="e.g. City Hospital, Downtown"
                      className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-emerald-500"
                      required
                    />
                  </div>"""
scanner = scanner.replace(old_return_modal, new_return_modal)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scanner)

# 3. Update LogsTab.tsx to display Location
logs = open('components/LogsTab.tsx', 'r', encoding='utf-8').read()

old_log = """                  <div className="flex justify-between mb-1">
                    <span className="text-gray-500 font-bold text-xs">Driver:</span>
                    <span className="font-bold text-gray-800">{log.driver_name}</span>
                  </div>"""

new_log = """                  <div className="flex justify-between mb-1">
                    <span className="text-gray-500 font-bold text-xs">Driver:</span>
                    <span className="font-bold text-gray-800">{log.driver_name}</span>
                  </div>
                  {log.location && (
                    <div className="flex justify-between mb-2 pb-2 border-b border-amber-200/50">
                      <span className="text-gray-500 font-bold text-xs">Visited:</span>
                      <span className="font-bold text-gray-800 truncate pl-2 text-right">{log.location}</span>
                    </div>
                  )}"""

logs = logs.replace(old_log, new_log)

with open('components/LogsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(logs)

print("Done")
