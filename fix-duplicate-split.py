import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# I will find all instances of 'const [batchDrafts, setBatchDrafts]'
parts = code.split('const [batchDrafts, setBatchDrafts] = useState<any[]>([]);')

if len(parts) == 3:
    # the second instance starts parts[2]. We need to remove from parts[2] until the closing brace of handleBatchAiScan
    # The end of the block we want to remove in parts[2] is after `    }\n  };\n`
    
    match = re.search(r'    \}\n  \};\n', parts[2])
    if match:
        rest_of_code = parts[2][match.end():]
        # Reconstruct without the second instance
        final_code = parts[0] + 'const [batchDrafts, setBatchDrafts] = useState<any[]>([]);' + parts[1] + rest_of_code
        
        with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
            f.write(final_code)
        print("Success! Duplicate removed.")
    else:
        print("Could not find end of handleBatchAiScan")
else:
    print(f"Found {len(parts)-1} instances, expected 2.")
