import os
import re

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace `const [activeTab, setActiveTab] = useState("scanner");`
# with a lazy initializer that reads from sessionStorage
target = '  const [activeTab, setActiveTab] = useState("scanner");'
replacement = """  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = sessionStorage.getItem('ams_active_tab');
      if (saved) return saved;
    }
    return "scanner";
  });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('ams_active_tab', activeTab);
    }
  }, [activeTab]);"""

code = code.replace(target, replacement)

# Now, in fetchRole, we should only redirect to reports if there is no saved tab!
# Or we can just say: if we are admin and activeTab is "scanner", go to "reports". Since admin doesn't have scanner, this logic is fine as long as activeTab is correctly loaded from sessionStorage first!
# If activeTab was 'employees' (Registry), it will load 'employees' from sessionStorage, so activeTab won't be "scanner", and it won't redirect to "reports"!

with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
