import os

scan = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

old_code = """    try {
      const data = JSON.parse(decodedText);
      const empId = data.empId;
      if (!empId) throw new Error("Invalid format");

      let empData = null;"""

new_code = """    try {
      const data = JSON.parse(decodedText);
      const empId = data.empId;
      if (!empId) throw new Error("Invalid format");

      const today = new Date();
      const dateStr = today.toISOString().split("T")[0];
      const timeStr = today.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      let empData = null;"""

scan = scan.replace(old_code, new_code)

old_date_code = """        if (!empData) {
          setScanResult({ success: false, msg: `Employee ${empId} not found.` });
        } else {
          const emp = empData;
          const today = new Date();
          const dateStr = today.toISOString().split("T")[0];
          const timeStr = today.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });"""
          
new_date_code = """        if (!empData) {
          setScanResult({ success: false, msg: `Employee ${empId} not found.` });
        } else {
          const emp = empData;"""

scan = scan.replace(old_date_code, new_date_code)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scan)
print("Done")
