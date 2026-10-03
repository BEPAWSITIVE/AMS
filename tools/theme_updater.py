import os
import re

def update_theme():
    files = [
        'flutter_app/lib/screens/settings_screen.dart',
        'flutter_app/lib/screens/scanner_screen.dart',
        'flutter_app/lib/screens/employee_screen.dart',
        'flutter_app/lib/screens/logs_screen.dart'
    ]
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update hardcoded backgrounds
        content = content.replace('Color(0xFF0F172A)', 'Color(0xFFF8FAFC)')
        content = content.replace('Color(0xFF1E293B)', 'Color(0xFFFFFFFF)')
        
        # Replace specific hardcoded Colors.white in standard text and icons to Colors.black
        # We will change it to black, but later fix the ones in buttons.
        content = re.sub(r'Colors\.white70', 'Colors.black54', content)
        content = re.sub(r'Colors\.white60', 'Colors.black54', content)
        content = re.sub(r'Colors\.white54', 'Colors.black54', content)
        content = re.sub(r'Colors\.white30', 'Colors.black38', content)
        content = re.sub(r'Colors\.white', 'Colors.black87', content)

        # Fix button text/icons which are on blue background and should remain white.
        # Buttons usually have ElevatedButton.styleFrom(..., foregroundColor: Colors.black87)
        content = content.replace('foregroundColor: Colors.black87', 'foregroundColor: Colors.white')
        content = content.replace('color: Colors.black87))', 'color: Colors.white))') # inside CircularProgressIndicator
        content = content.replace('Icon(Icons.save, color: Colors.black87)', 'Icon(Icons.save, color: Colors.white)')
        content = content.replace('Icon(Icons.cloud_upload, color: Colors.black87)', 'Icon(Icons.cloud_upload, color: Colors.white)')
        content = content.replace('Text("Save URL", style: TextStyle(color: Colors.black87))', 'Text("Save URL", style: TextStyle(color: Colors.white))')
        content = content.replace('style: const TextStyle(color: Colors.black87, fontWeight: FontWeight.bold)', 'style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)') # Sync button
        
        # In scanner overlay, text on black overlay should be white
        content = content.replace(
            'Point camera at employee QR badge",\n                              style: TextStyle(color: Colors.black87, fontSize: 13',
            'Point camera at employee QR badge",\n                              style: TextStyle(color: Colors.white, fontSize: 13'
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    update_theme()
