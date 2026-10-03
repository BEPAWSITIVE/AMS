import os
import re

def configure_android():
    print("Configuring Android for Attendance Manager...")

    # 1. Update minSdk to 21 and disable R8/minify in build.gradle
    for root, dirs, files in os.walk("android"):
        for fname in files:
            if fname.startswith("build.gradle"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    orig = content

                    # Set minSdk = 21
                    content = re.sub(r'minSdk\s*=\s*[a-zA-Z0-9_.]+', 'minSdk = 21', content)
                    content = re.sub(r'minSdkVersion\s+[a-zA-Z0-9_.]+', 'minSdkVersion 21', content)

                    # In app build.gradle, disable minification in release build to prevent R8 from stripping ML Kit & CameraX
                    if "com.android.application" in content or "android {" in content:
                        # Ensure minifyEnabled false and shrinkResources false
                        if "minifyEnabled" in content:
                            content = re.sub(r'minifyEnabled\s+true', 'minifyEnabled false', content)
                            content = re.sub(r'minifyEnabled\s*=\s*true', 'minifyEnabled = false', content)
                        else:
                            content = re.sub(
                                r'(buildTypes\s*\{[^{}]*release\s*\{)',
                                r'\1\n            minifyEnabled false\n            shrinkResources false',
                                content
                            )
                        if "shrinkResources" in content:
                            content = re.sub(r'shrinkResources\s+true', 'shrinkResources false', content)
                            content = re.sub(r'shrinkResources\s*=\s*true', 'shrinkResources = false', content)

                    if content != orig:
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"Configured minSdk & disabled minification in {fpath}")
                except Exception as e:
                    print(f"Warning: could not process {fpath}: {e}")

    # 2. Create comprehensive proguard-rules.pro
    proguard_dir = os.path.join("android", "app")
    if os.path.exists(proguard_dir):
        proguard_file = os.path.join(proguard_dir, "proguard-rules.pro")
        with open(proguard_file, "w", encoding="utf-8") as f:
            f.write("""
# Flutter wrapper keep rules
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.**  { *; }
-keep class io.flutter.plugins.**  { *; }

# Mobile Scanner & CameraX keep rules
-keep class dev.steenbakker.mobile_scanner.** { *; }
-keep class androidx.camera.** { *; }
-keep class androidx.camera.core.** { *; }
-keep class androidx.camera.lifecycle.** { *; }
-keep class androidx.camera.camera2.** { *; }
-keep class androidx.camera.view.** { *; }

# Google ML Kit Barcode Scanning
-keep class com.google.mlkit.** { *; }
-keep class com.google.android.gms.internal.mlkit_vision_barcode.** { *; }
-keep class com.google.android.gms.vision.** { *; }
-keep class com.google.android.gms.common.** { *; }

-dontwarn androidx.camera.**
-dontwarn com.google.mlkit.**
-dontwarn dev.steenbakker.mobile_scanner.**
""")
        print("Created android/app/proguard-rules.pro")

    # 3. Add permissions and ML Kit metadata to AndroidManifest.xml
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

        # Add ML Kit barcode dependency meta-data inside <application>
        mlkit_meta = '\n        <meta-data android:name="com.google.mlkit.vision.DEPENDENCIES" android:value="barcode" />'
        if "com.google.mlkit.vision.DEPENDENCIES" not in manifest:
            manifest = re.sub(r'(<application[^>]*>)', r'\1' + mlkit_meta, manifest, count=1)

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest)
        print("Injected camera permissions & ML Kit metadata into AndroidManifest.xml")

if __name__ == "__main__":
    configure_android()
