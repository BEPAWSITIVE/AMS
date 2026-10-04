import os

logs = open('components/LogsTab.tsx', 'r', encoding='utf-8').read()
if "localdb.syncQueue" not in logs:
    logs = logs.replace('import { supabase, AttendanceRecord } from "@/lib/supabase";', 'import { supabase, AttendanceRecord } from "@/lib/supabase";\nimport { localdb } from "@/lib/localdb";')
    
    old_fetch = """  async function fetchLogs() {
    const { data, error } = await supabase.from('attendance').select('*').order('inTimestamp', { ascending: false });
    if (!error && data) {
      setLogs(data);
    }
    setLoading(false);
  }"""
    new_fetch = """  async function fetchLogs() {
    let allLogs: AttendanceRecord[] = [];
    
    if (navigator.onLine) {
      const { data, error } = await supabase.from('attendance').select('*').order('inTimestamp', { ascending: false });
      if (!error && data) {
        allLogs = data;
        localStorage.setItem('cached_logs', JSON.stringify(data));
      }
    } else {
      const cached = localStorage.getItem('cached_logs');
      if (cached) allLogs = JSON.parse(cached);
    }

    // Add local pending records
    const queue = await localdb.syncQueue.toArray();
    
    // Merge without duplicates (using recordId), prioritizing queue over cached
    const merged = [...queue, ...allLogs].reduce((acc, curr) => {
      if (!acc.find(item => item.recordId === curr.recordId)) {
        acc.push(curr);
      } else {
        // If it exists, update it if the queue version is newer (queue version is always newer)
        const idx = acc.findIndex(item => item.recordId === curr.recordId);
        if (queue.find(q => q.recordId === curr.recordId)) {
          acc[idx] = curr;
        }
      }
      return acc;
    }, [] as AttendanceRecord[]);

    merged.sort((a, b) => b.inTimestamp - a.inTimestamp);
    setLogs(merged);
    setLoading(false);
  }"""
    logs = logs.replace(old_fetch, new_fetch)
    with open('components/LogsTab.tsx', 'w', encoding='utf-8') as f:
        f.write(logs)

print("Done")
