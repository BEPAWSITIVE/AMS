import os

scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

# Replace the specific duplicate block
old_block = """  } | null>(null);
  const [parcelModal, setParcelModal] = useState<{ profile: Employee; lastRecord: AttendanceRecord } | null>(null);
  const [pickerName, setPickerName] = useState("");
  
  const [driverName, setDriverName] = useState("");"""

new_block = """  } | null>(null);
  
  const [driverName, setDriverName] = useState("");"""

scanner = scanner.replace(old_block, new_block)

with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scanner)

print("Done")
