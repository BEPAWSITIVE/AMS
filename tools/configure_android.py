import os
import re

def configure_android():
    print("Configuring Android for Attendance Manager...")

    # 1. Update minSdk = 21 in build.gradle / build.gradle.kts
    gradle_files = [
        os.path.join("android", "app", "build.gradle"),
        os.path.join("android", "app", "build.gradle.kts"),
    ]
    for gpath in gradle_files:
        if os.path.exists(gpath):
            with open(gpath, "r", encoding="utf-8") as f:
                content = f.read()
            # Replace minSdk
            content = re.sub(r'minSdk\s*=\s*flutter\.minSdkVersion', 'minSdk = 21', content)
            content = re.sub(r'minSdkVersion\s+flutter\.minSdkVersion', 'minSdkVersion 21', content)
            with open(gpath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated minSdk in {gpath}")

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
            # Insert right after <manifest ...>
            manifest = re.sub(r'(<manifest[^>]*>)', r'\1' + permissions, manifest, count=1)
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(manifest)
            print("Injected camera, network, and package install permissions into AndroidManifest.xml")
        else:
            print("Permissions already present in AndroidManifest.xml")

if __name__ == "__main__":
    configure_android()
