import os

with open('components/ParcelsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('setTargetPerson(initialAiData.recipient_name || "");', 'setRecipientName(initialAiData.recipient_name || "");')
code = code.replace('setCompanyName(initialAiData.company_name || "");', 'setCompanyName(initialAiData.company_name || "");\n      setBarcode(initialAiData.barcode || "");')

with open('components/ParcelsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
