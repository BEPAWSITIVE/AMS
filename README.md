# Attendance Manager 📱
> **Offline-First QR Attendance Android App with Automatic Check-In/Check-Out & Google Sheets Sync**

---

## 📌 System Overview

**Attendance Manager** is a complete, offline-first attendance solution designed for security guards and workplace administrators:

1. **Employee Registration**: Register all employees in the app with their Name, ID, Department, and Phone.
2. **Unique QR Code Generation**: Instantly generates an individual QR code pass for each employee that can be downloaded or printed as a physical badge.
3. **Smart Gate Scanning (Guard Mode)**:
   - **Arrival**: Guard scans the employee's QR code. The app automatically detects this is their first scan of the day and marks **CHECK-IN** with the exact entry timestamp.
   - **Departure**: Guard scans the same employee's QR code when leaving. The app detects they are already inside and automatically marks **CHECK-OUT**, recording departure time and calculating total working hours (e.g., `8h 45m`).
   - **Feedback**: Plays sound chimes and triggers physical vibration with a large visual card showing the employee's photo avatar, name, and timestamp.
4. **100% Offline Capability**:
   - Guard can scan all day without any internet or Wi-Fi.
   - All records are saved locally in the device database (SQLite / IndexedDB) with a `pending sync` status.
5. **Google Sheets Sync**:
   - As soon as mobile data or Wi-Fi reconnects (or when the guard taps **"Sync Pending Records"**), the app automatically pushes the attendance data to your **Google Sheet**.

---

## 📂 Project Structure

```
attendance-manager/
├── google_apps_script/
│   └── Code.gs                  # Google Sheets Webhook Script (doPost & doGet)
├── pwa/                         # Instant-install Android Web APK / PWA (Offline & Camera ready)
│   ├── index.html               # Main mobile interface (Scanner, Staff, Logs, Settings)
│   ├── style.css               # Clean, high-contrast dark theme
│   ├── app.js                   # IndexedDB offline engine, QR scanner, audio & sync
│   ├── sw.js                    # Service Worker caching for offline usage
│   ├── manifest.json            # Android Standalone App manifest
│   ├── icon-192.png             # Android launcher icon (192x192)
│   └── icon-512.png             # Android launcher icon (512x512)
├── flutter_app/                 # Native Android Flutter Codebase
│   ├── lib/
│   │   ├── main.dart            # Flutter app entry point
│   │   ├── models/              # Employee & AttendanceRecord models
│   │   ├── database/            # SQLite DBHelper (sqflite)
│   │   ├── services/            # SyncService (Google Sheets HTTP push)
│   │   └── screens/             # Scanner, Employees, Logs, Settings screens
│   ├── android/app/src/main/
│   │   └── AndroidManifest.xml  # Camera, Internet, Vibrate permissions
│   └── pubspec.yaml             # Flutter dependencies
├── .github/workflows/
│   └── build_apk.yml            # 1-Click Automated Cloud APK Builder (GitHub Actions)
└── README.md                    # Setup and deployment documentation
```

---

## 🚀 Step 1: Set Up Google Sheet (Takes 2 Minutes)

1. Open **[Google Sheets](https://sheets.google.com)** and create a **Blank Spreadsheet**.
2. Name the spreadsheet: **`Attendance Manager Records`**.
3. In the top menu bar, click **Extensions** > **Apps Script**.
4. Clear any existing code in the editor, open `google_apps_script/Code.gs` from this project, and copy-paste the entire code.
5. Click the **Save** icon (floppy disk).
6. Click the blue **Deploy** button (top right) > **New deployment**.
7. Click the gear icon next to "Select type" and select **Web app**.
8. Fill in:
   - **Description**: `Attendance Manager Webhook`
   - **Execute as**: `Me`
   - **Who has access**: `Anyone` *(Crucial: This enables the mobile app to sync records seamlessly)*
9. Click **Deploy** and grant permissions if prompted.
10. Copy the generated **Web app URL** (starts with `https://script.google.com/macros/s/.../exec`).

---

## 📲 Step 2: Running & Installing on Android

You have **two deployment options**:

### Option A: Instant 0-Install Android App (Recommended)
You can run and test the app immediately without downloading Android Studio or SDKs:

1. **Host or open the `pwa/` folder**:
   - You can host the `pwa` folder on free static hosting (Vercel, Netlify, GitHub Pages, Firebase Hosting) or test locally on your network.
   - Run a local server:
     ```powershell
     cd C:\Users\Deepak\.gemini\antigravity\scratch\attendance-manager\pwa
     python -m http.server 8080
     ```
2. Open Chrome on the Guard's Android phone and navigate to the URL.
3. Tap the **3 dots menu** in Chrome > select **"Install app"** or **"Add to Home screen"**.
4. The app will install with its official icon onto the Android home screen just like an APK, opens in full screen (no browser address bar), caches all files for offline access, and has direct hardware camera QR scanning access!

### Option B: Build Native Android APK (`.apk` file)

#### Method 1: 1-Click Cloud APK Build (Zero Installation)
We have included a GitHub Actions workflow in `.github/workflows/build_apk.yml`:
1. Push this folder to a GitHub repository.
2. In your GitHub repository, click on the **Actions** tab.
3. Select **"Build Android APK"** and click **Run workflow**.
4. In under 3 minutes, GitHub compiles the release APK and provides a downloadable **`app-release.apk`** artifact!
5. Transfer `app-release.apk` to any Android phone and install.

#### Method 2: Build Locally with Flutter CLI
If Flutter is installed on your workstation:
```bash
cd flutter_app
flutter pub get
flutter build apk --release
```
The compiled APK will be located at:
`flutter_app/build/app/outputs/flutter-apk/app-release.apk`

---

## 🛠️ Step 3: Using the App

1. **Configure Webhook**:
   - Go to the **Settings** tab.
   - Paste your **Google Apps Script Webhook URL** and tap **Save URL**.
   - Tap **"Load 5 Sample Employees"** to instantly test with demo staff.
2. **Guard Mode (Scanning)**:
   - Go to the **Scan** tab.
   - Tap **Start Camera** (or use **"Test Scan"** to simulate scans).
   - Point the camera at any employee's QR badge.
   - 🟢 **First scan**: Marks **Check-In** (Arrival time recorded, green alert).
   - 🔵 **Second scan**: Marks **Check-Out** (Leaving time + total hours worked recorded, blue alert).
   - 🟡 **Repeat scan**: Alerts guard that today's attendance has already been logged.
3. **Offline Sync**:
   - If the guard has no internet, all records remain safely stored on the device.
   - An amber badge shows pending count (e.g. `3 unsynced`).
   - When internet is restored, the app auto-syncs or the guard can tap **"Push Pending Records Now"**.
4. **Google Sheet Output**:
   - Columns automatically populated:
     `Date | Employee ID | Employee Name | Department | In Time | Out Time | Total Hours | Status | Last Synced At`
