import os

# 1. Update app/page.tsx
with open('app/page.tsx', 'r', encoding='utf-8') as f:
    page_code = f.read()

page_code = page_code.replace('{activeTab === "parcels" && <ParcelsTab />}', '{activeTab === "parcels" && <ParcelsTab role={role} />}')

with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(page_code)

# 2. Update components/ParcelsTab.tsx
with open('components/ParcelsTab.tsx', 'r', encoding='utf-8') as f:
    parcels_code = f.read()

# Change export
parcels_code = parcels_code.replace('export default function ParcelsTab() {', 'export default function ParcelsTab({ role = "guard" }: { role?: "admin" | "guard" }) {')

# Find the start of the Receive New Parcel form
receive_form_start = """      {/* New Parcel Form */}
      <div className="bg-white p-5 rounded-3xl shadow-lg border border-purple-100 mb-6 relative overflow-hidden">"""

receive_form_replacement = """      {/* New Parcel Form */}
      {role === 'guard' && (
      <div className="bg-white p-5 rounded-3xl shadow-lg border border-purple-100 mb-6 relative overflow-hidden">"""

parcels_code = parcels_code.replace(receive_form_start, receive_form_replacement)

# Now we need to close the conditional rendering block
# Let's find the end of the form by looking for the next section
list_start = """      {/* Parcel List */}
      <div>"""

list_replacement = """      </div>
      )}

      {/* Parcel List */}
      <div>"""

parcels_code = parcels_code.replace(list_start, list_replacement)


with open('components/ParcelsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(parcels_code)

print("Done")
