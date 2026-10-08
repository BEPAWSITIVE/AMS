import os

with open('components/ParcelsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

target = "async function fetchParcels() {"

effect_code = """
  useEffect(() => {
    if (initialAiData) {
      setCompanyName(initialAiData.company_name || "");
      setTargetPerson(initialAiData.recipient_name || "");
      setShowForm(true);
      if (onAiDataConsumed) onAiDataConsumed();
    }
  }, [initialAiData]);
"""

code = code.replace(target, effect_code + '\n  ' + target)

with open('components/ParcelsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
