import os

logs = open('components/LogsTab.tsx', 'r', encoding='utf-8').read()

old_block = """    const merged = [...queue, ...allLogs].reduce((acc, curr) => {
      if (!acc.find(item => item.recordId === curr.recordId)) {
        acc.push(curr);
      } else {
        const idx = acc.findIndex(item => item.recordId === curr.recordId);
        if (queue.find(q => q.recordId === curr.recordId)) {
          acc[idx] = curr;
        }
      }
      return acc;
    }, [] as AttendanceRecord[]);
    
    merged.sort((a, b) => b.inTimestamp - a.inTimestamp);"""

new_block = """    const merged = [...queue, ...allLogs].reduce((acc: AttendanceRecord[], curr: any) => {
      const current = curr as AttendanceRecord;
      if (!acc.find((item: AttendanceRecord) => item.recordId === current.recordId)) {
        acc.push(current);
      } else {
        const idx = acc.findIndex((item: AttendanceRecord) => item.recordId === current.recordId);
        if (queue.find((q: any) => (q as AttendanceRecord).recordId === current.recordId)) {
          acc[idx] = current;
        }
      }
      return acc;
    }, [] as AttendanceRecord[]);
    
    merged.sort((a: AttendanceRecord, b: AttendanceRecord) => b.inTimestamp - a.inTimestamp);"""

logs = logs.replace(old_block, new_block)

with open('components/LogsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(logs)

print("Done")
