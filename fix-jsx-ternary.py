import os

with open('components/EmployeesTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# The broken block starts here:
broken_block_start = "              ) : category !== 'Parcel' ? ("
broken_block_end = "              ) : null}"

# We need to find this exact ternary branch and wrap it in a fragment or div.
# But since I know exactly what it looks like, let's replace the whole ternary branch.

import re
pattern = r"\)\s*:\s*category !== 'Parcel'\s*\?\s*\(\s*(<div className=\"flex space-x-3\">[\s\S]*?\{category !== 'Parcel' && \([\s\S]*?<\/div>\s*\)\})\s*\)\s*:\s*null\}"

replacement = r") : category !== 'Parcel' ? (\n                <div className=\"space-y-2\">\n                  \1\n                </div>\n              ) : null}"

if re.search(pattern, code):
    code = re.sub(pattern, replacement, code)
    print("Fixed JSX ternary sibling issue!")
else:
    print("Pattern not found. Using fallback replace.")
    # Fallback: Just search for `<div className="flex space-x-3">` right after `? (`
    code = code.replace(
        ") : category !== 'Parcel' ? (\n                <div className=\"flex space-x-3\">",
        ") : category !== 'Parcel' ? (\n                <div className=\"space-y-2\">\n                  <div className=\"flex space-x-3\">"
    )
    code = code.replace(
        "                  )}\n              ) : null}",
        "                  )}\n                </div>\n              ) : null}"
    )
    print("Applied fallback replace.")

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
