import sys

content = open('components/ScannerTab.tsx', 'r').read()

new_content = """  useEffect(() => {
    let html5QrCode: any;

    const timer = setTimeout(() => {
      import("html5-qrcode").then(({ Html5Qrcode }) => {
        html5QrCode = new Html5Qrcode("reader");
        
        html5QrCode.start(
          { facingMode: "environment" },
          { 
            fps: 10, 
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0 
          },
          onScanSuccess,
          onScanFailure
        ).then(() => {
          scannerRef.current = html5QrCode;
        }).catch(err => {
          console.error("Camera start failed automatically", err);
        });
      });
    }, 100);

    return () => {
      clearTimeout(timer);
      if (scannerRef.current) {
        try {
          if (scannerRef.current.isScanning) {
            scannerRef.current.stop().then(() => {
              scannerRef.current?.clear();
              scannerRef.current = null;
            }).catch((e: any) => console.error("Failed to stop scanner", e));
          } else {
            scannerRef.current.clear();
            scannerRef.current = null;
          }
        } catch(e) {}
      } else if (html5QrCode) {
        try { html5QrCode.clear(); } catch(e) {}
      }
    };
  }, []);"""

old_content = """  useEffect(() => {
    if (!scannerRef.current) {
      scannerRef.current = new Html5QrcodeScanner(
        "reader",
        { 
          fps: 10, 
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0,
          showTorchButtonIfSupported: true,
          supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA],
        },
        false
      );
      
      scannerRef.current.render(onScanSuccess, onScanFailure);
    }

    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(e => console.error("Failed to clear scanner", e));
        scannerRef.current = null;
      }
    };
  }, []);"""

final_content = content.replace(old_content, new_content)
open('components/ScannerTab.tsx', 'w').write(final_content)
print('Done')
