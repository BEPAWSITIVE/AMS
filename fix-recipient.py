import os

parcels = open('components/ParcelsTab.tsx', 'r', encoding='utf-8').read()

# 1. Remove validation check
parcels = parcels.replace('if (!companyName || !recipientName) return;', 'if (!companyName) return;')

# 2. Update form input
old_input = """              <div className="w-1/2">
                <label className="block text-xs font-bold text-gray-500 mb-1">For Whom *</label>
                <input 
                  type="text" 
                  value={recipientName} 
                  onChange={e => setRecipientName(e.target.value)}
                  placeholder="Employee Name"
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>"""

new_input = """              <div className="w-1/2">
                <label className="block text-xs font-bold text-gray-500 mb-1">For Whom</label>
                <input 
                  type="text" 
                  value={recipientName} 
                  onChange={e => setRecipientName(e.target.value)}
                  placeholder="Optional"
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>"""
parcels = parcels.replace(old_input, new_input)

# 3. Update display to handle empty string
parcels = parcels.replace('<h4 className="font-bold text-gray-800 text-lg">{p.recipient_name}</h4>', '<h4 className="font-bold text-gray-800 text-lg">{p.recipient_name || "Unspecified"}</h4>')

parcels = parcels.replace('<h4 className="font-bold text-gray-700">{p.recipient_name}</h4>', '<h4 className="font-bold text-gray-700">{p.recipient_name || "Unspecified"}</h4>')

parcels = parcels.replace('<h3 className="text-xl font-bold">{pickupModal.recipient_name}</h3>', '<h3 className="text-xl font-bold">{pickupModal.recipient_name || "Unspecified"}</h3>')

with open('components/ParcelsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(parcels)

print("Done")
