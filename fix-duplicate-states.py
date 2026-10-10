import os
import re

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'  const \[batchDrafts, setBatchDrafts\] = useState<any\[\]>\(\[\]\);\s*const \[aiLoading, setAiLoading\] = useState\(false\);\s*const fileInputRef = useRef<HTMLInputElement>\(null\);\s*const compressImage = \(file: File\): Promise<string> => \{[\s\S]*?const handleBatchAiScan = async \(e: React\.ChangeEvent<HTMLInputElement>\) => \{[\s\S]*?setAiLoading\(false\);\s*\}\s*\};\s*'

# Only remove the SECOND occurrence if there are two
matches = list(re.finditer(pattern, code))
if len(matches) > 1:
    second_match = matches[1]
    # Remove it
    code = code[:second_match.start()] + code[second_match.end():]
    with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully removed second occurrence")
else:
    print(f"Found {len(matches)} occurrences. Did not remove.")
