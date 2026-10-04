import os

emp = open('components/EmployeesTab.tsx', 'r', encoding='utf-8').read()

old_share_logic = """                  const useDirectWhatsApp = selectedEmployee.phone && selectedEmployee.phone.length > 5;
                  
                  if (useDirectWhatsApp) {
                    // Download the file first
                    const url = URL.createObjectURL(file);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = file.name;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    
                    const cleanPhone = (selectedEmployee.phone || '').replace(/\\D/g,'');
                    const waUrl = `https://wa.me/${cleanPhone}?text=` + encodeURIComponent(`Here is your Attendance QR Pass, ${selectedEmployee.name}.\\n\\n(Please see the attached image below)`);
                    
                    setTimeout(() => {
                      if (confirm("QR Card Downloaded! \\n\\nClick OK to open the chat directly with " + selectedEmployee.name + ". \\n\\n⚠️ IMPORTANT: You will need to tap the attachment/camera icon in WhatsApp to attach the downloaded pass!")) {
                        window.open(waUrl, "_blank");
                      }
                    }, 500);
                  } else if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    // Fallback to OS Share Sheet if no phone number is provided
                    try {
                      await navigator.share({
                        title: 'Attendance QR',
                        text: `Here is the Attendance QR Pass for ${selectedEmployee.name}.`,
                        files: [file]
                      });
                    } catch (err: any) {
                      console.log("Share cancelled or failed", err);
                    }
                  } else {
                    alert("Please add a phone number for this employee to share via WhatsApp.");
                  }"""
                  
new_share_logic = """                  const useDirectWhatsApp = selectedEmployee.phone && selectedEmployee.phone.length > 5;
                  
                  if (useDirectWhatsApp) {
                    if (!navigator.onLine) {
                      alert("You must be online to generate and upload the cloud link for this pass.");
                      return;
                    }
                    
                    try {
                      // Show uploading state (simple alert for now)
                      const fileName = `${selectedEmployee.empId}_${Date.now()}.png`;
                      
                      const { data, error } = await supabase
                        .storage
                        .from('qr-passes')
                        .upload(fileName, file, {
                          cacheControl: '3600',
                          upsert: false
                        });

                      if (error) {
                        console.error("Upload error", error);
                        alert("Failed to upload image. Did you create the 'qr-passes' public bucket in Supabase?");
                        return;
                      }

                      const { data: { publicUrl } } = supabase
                        .storage
                        .from('qr-passes')
                        .getPublicUrl(fileName);

                      const cleanPhone = (selectedEmployee.phone || '').replace(/\\D/g,'');
                      const msg = `Hello ${selectedEmployee.name}, here is your digital Attendance QR Pass!\\n\\nClick the secure link below to view and download your pass:\\n${publicUrl}`;
                      const waUrl = `https://wa.me/${cleanPhone}?text=` + encodeURIComponent(msg);
                      
                      window.open(waUrl, "_blank");
                      
                    } catch (err) {
                      alert("An error occurred while uploading the pass.");
                    }
                    
                  } else if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    try {
                      await navigator.share({
                        title: 'Attendance QR',
                        text: `Here is the Attendance QR Pass for ${selectedEmployee.name}.`,
                        files: [file]
                      });
                    } catch (err: any) {
                      console.log("Share cancelled or failed", err);
                    }
                  } else {
                    alert("Please add a phone number for this employee to share via WhatsApp.");
                  }"""
                  
emp = emp.replace(old_share_logic, new_share_logic)

with open('components/EmployeesTab.tsx', 'w', encoding='utf-8') as f:
    f.write(emp)
print("Done")
