import os

with open('components/ParcelsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. First, let's undo any messy changes I might have made in my previous script just in case
# Actually, the previous script probably didn't find the exact strings, so it did nothing.
# Let's check if the role prop is there.
if 'export default function ParcelsTab() {' in code:
    code = code.replace('export default function ParcelsTab() {', 'export default function ParcelsTab({ role = "guard" }: { role?: "admin" | "guard" }) {')

# 2. Hide the + Receive Parcel button
old_button = """          <button 
            onClick={() => setShowForm(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl text-sm font-bold shadow-md transition-colors"
          >
            + Receive Parcel
          </button>"""

new_button = """          {role === 'guard' && (
            <button 
              onClick={() => setShowForm(true)}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl text-sm font-bold shadow-md transition-colors"
            >
              + Receive Parcel
            </button>
          )}"""
code = code.replace(old_button, new_button)

with open('components/ParcelsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
