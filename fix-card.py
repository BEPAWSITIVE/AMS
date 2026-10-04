import sys

content = open('components/EmployeesTab.tsx', 'r').read()

helper_function = """
  function generateCardCanvas(qrCanvas: HTMLCanvasElement, employee: any): HTMLCanvasElement {
    const canvas = document.createElement("canvas");
    canvas.width = 600;
    canvas.height = 800;
    const ctx = canvas.getContext("2d")!;
    
    // Background
    ctx.fillStyle = "#F4F9FF";
    ctx.fillRect(0, 0, 600, 800);
    
    // Card Shadow
    ctx.shadowColor = "rgba(0, 0, 0, 0.08)";
    ctx.shadowBlur = 30;
    ctx.shadowOffsetY = 10;
    
    // Card Body
    ctx.fillStyle = "#FFFFFF";
    // Rounded rect
    const x = 40, y = 40, w = 520, h = 720, r = 32;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    ctx.fill();
    
    // Reset shadow for text/images
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
    ctx.shadowOffsetY = 0;
    
    ctx.textAlign = "center";
    
    // Header
    ctx.fillStyle = "#3B82F6";
    ctx.font = "bold 20px sans-serif";
    ctx.letterSpacing = "2px";
    ctx.fillText("ATTENDANCE PASS", 300, 120);
    
    // Name
    ctx.fillStyle = "#1E293B";
    ctx.font = "bold 46px sans-serif";
    ctx.fillText(employee.name, 300, 190);
    
    // Department & ID
    ctx.fillStyle = "#64748B";
    ctx.font = "24px sans-serif";
    ctx.fillText(`${employee.department} • ${employee.empId}`, 300, 240);
    
    // Draw QR
    // QR size is 320x320
    const qrSize = 340;
    ctx.drawImage(qrCanvas, 300 - qrSize/2, 290, qrSize, qrSize);
    
    // Footer
    ctx.fillStyle = "#94A3B8";
    ctx.font = "18px sans-serif";
    ctx.fillText("Scan this code at the entrance to mark attendance", 300, 700);
    
    // Logo text at very bottom
    ctx.fillStyle = "#CBD5E1";
    ctx.font = "bold 16px sans-serif";
    ctx.fillText("Attendance Manager", 300, 740);

    return canvas;
  }
"""

# Find where to inject the helper. Right before `async function handleAdd`
inject_marker = "  async function handleAdd(e: React.FormEvent) {"
content = content.replace(inject_marker, helper_function + "\n" + inject_marker)


# Now replace the sharing logic inside the button
old_share_logic = """              onClick={() => {
                const canvas = document.getElementById("qr-canvas") as HTMLCanvasElement;
                if (!canvas) return;
                
                canvas.toBlob(async (blob) => {
                  if (!blob) return;
                  const file = new File([blob], `${selectedEmployee.name.replace(/\s+/g, '_')}_QR.png`, { type: "image/png" });
                  
                  // Try Native Web Share API first
                  if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    try {
                      await navigator.share({
                        title: 'Attendance QR',
                        text: `Here is the Attendance QR Pass for ${selectedEmployee.name}.`,
                        files: [file]
                      });
                      return;
                    } catch (err) {
                      console.log("Share cancelled or failed", err);
                    }
                  } else {
                    // Fallback for desktop or unsupported browsers
                    const url = URL.createObjectURL(file);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = file.name;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    
                    let waUrl = "https://wa.me/";
                    if (selectedEmployee.phone) {
                      waUrl += selectedEmployee.phone.replace(/\D/g,'');
                    }
                    waUrl += "?text=" + encodeURIComponent(`Here is the Attendance QR Pass for ${selectedEmployee.name}.\\n\\nThe QR image has been downloaded to your device, please attach it to this message!`);
                    
                    if (confirm("The QR Image has been downloaded. Click OK to open WhatsApp now, and don't forget to attach the downloaded image!")) {
                      window.open(waUrl, "_blank");
                    }
                  }
                }, "image/png");
              }}"""

new_share_logic = """              onClick={() => {
                const qrCanvas = document.getElementById("qr-canvas") as HTMLCanvasElement;
                if (!qrCanvas) return;
                
                const cardCanvas = generateCardCanvas(qrCanvas, selectedEmployee);
                
                cardCanvas.toBlob(async (blob) => {
                  if (!blob) return;
                  const file = new File([blob], `${selectedEmployee.name.replace(/\\s+/g, '_')}_Pass.png`, { type: "image/png" });
                  
                  // Try Native Web Share API first
                  if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    try {
                      await navigator.share({
                        title: 'Attendance QR',
                        text: `Here is the Attendance QR Pass for ${selectedEmployee.name}.`,
                        files: [file]
                      });
                      return;
                    } catch (err) {
                      console.log("Share cancelled or failed", err);
                    }
                  } else {
                    // Fallback for desktop or unsupported browsers
                    const url = URL.createObjectURL(file);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = file.name;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    
                    let waUrl = "https://wa.me/";
                    if (selectedEmployee.phone) {
                      waUrl += selectedEmployee.phone.replace(/\\D/g,'');
                    }
                    waUrl += "?text=" + encodeURIComponent(`Here is the Attendance QR Pass for ${selectedEmployee.name}.\\n\\nThe pass image has been downloaded to your device, please attach it to this message!`);
                    
                    if (confirm("The QR Pass has been downloaded. Click OK to open WhatsApp now, and don't forget to attach the downloaded image!")) {
                      window.open(waUrl, "_blank");
                    }
                  }
                }, "image/png");
              }}"""

final_content = content.replace(old_share_logic, new_share_logic)
open('components/EmployeesTab.tsx', 'w').write(final_content)
print('Done')
