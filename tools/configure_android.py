import os
import re

def configure_android():
    print("Configuring Android for Attendance Manager...")

    # 1. Update minSdk to 21 everywhere in android/
    for root, dirs, files in os.walk("android"):
        for fname in files:
            if fname.startswith("build.gradle"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    orig = content
                    content = re.sub(r'minSdk\s*=\s*[a-zA-Z0-9_.]+', 'minSdk = 21', content)
                    content = re.sub(r'minSdkVersion\s+[a-zA-Z0-9_.]+', 'minSdkVersion 21', content)
                    if content != orig:
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"Updated minSdk to 21 in {fpath}")
                except Exception as e:
                    print(f"Warning: could not process {fpath}: {e}")

    # 2. Add permissions and hardware features to AndroidManifest.xml
    manifest_path = os.path.join("android", "app", "src", "main", "AndroidManifest.xml")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = f.read()

        permissions = """
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />
    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.camera.autofocus" android:required="false" />
    <uses-feature android:name="android.hardware.camera.flash" android:required="false" />
"""
        if "android.permission.CAMERA" not in manifest:
            manifest = re.sub(r'(<manifest[^>]*>)', r'\1' + permissions, manifest, count=1)
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(manifest)
            print("Injected camera, network, and package install permissions into AndroidManifest.xml")
        else:
            print("Permissions already present in AndroidManifest.xml")

if __name__ == "__main__":
    configure_android()
