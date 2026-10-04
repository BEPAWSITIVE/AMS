import os

content = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

# Replace the import
content = content.replace(
    'import { MessageCircle, X } from "lucide-react";',
    'import { MessageCircle, X, Download } from "lucide-react";'
)

# Fix the WhatsApp text message string
old_msg_code = "const msg = `Hello ${selectedEmployee.name}, here is your digital Attendance QR Pass!\\n\\nClick the secure link below to view and download your pass:\\n${publicUrl}`;"
new_msg_code = "const msg = `Hello ${selectedEmployee.name},\\n\\nOpen the link to view your QR pass and download it:\\n${publicUrl}`;"
content = content.replace(old_msg_code, new_msg_code)

# I will find the whole button chunk by using index
# It starts at: <button \n              onClick={() => {
# and ends at: <MessageCircle size={18} className="mr-2" /> Share to WhatsApp\n            </button>
# Let's write a targeted replace for the button layout.

# I'll define handleDownload logic to reuse the canvas. 
# But wait, we can just replace the whole button with a div containing two buttons.

old_button_start = """            <button 
              onClick={() => {"""
old_button_end = """              <MessageCircle size={18} className="mr-2" /> Share to WhatsApp
            </button>"""

idx_start = content.find(old_button_start)
idx_end = content.find(old_button_end) + len(old_button_end)

if idx_start != -1 and idx_end != -1:
    button_block = content[idx_start:idx_end]
    
    # We will replace this block with two buttons inside a div.
    new_buttons = """            <div className="w-full flex space-x-2 mt-1">
              <button 
                onClick={() => {
                  const qrCanvas = document.getElementById("qr-canvas") as HTMLCanvasElement;
                  if (!qrCanvas) return;
                  const cardCanvas = generateCardCanvas(qrCanvas, selectedEmployee);
                  const url = cardCanvas.toDataURL("image/png");
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `${selectedEmployee.name.replace(/\\s+/g, '_')}_Pass.png`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                }}
                className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-3 rounded-xl flex items-center justify-center font-bold shadow-sm transition-colors text-sm"
              >
                <Download size={18} className="mr-1" /> Download
              </button>
""" + button_block.replace('className="w-full bg-[#25D366]', 'className="flex-1 bg-[#25D366]').replace('<MessageCircle size={18} className="mr-2" /> Share to WhatsApp', '<MessageCircle size={18} className="mr-1" /> WhatsApp') + """
            </div>"""
            
    content = content[:idx_start] + new_buttons + content[idx_end:]

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
