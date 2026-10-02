/**
 * Attendance Manager - Offline-First QR Attendance Core Engine
 */

// ==========================================
// 1. STATE & DATABASE (IndexedDB)
// ==========================================
let db;
const DB_NAME = 'AttendanceManagerDB';
const DB_VERSION = 1;

let html5QrCodeScanner = null;
let currentCameraFacing = "environment"; // default to back camera
let isScannerActive = false;
let lastScanTimestamp = 0;
let lastScannedEmpId = null;

// Initialize IndexedDB
function initDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (e) => {
      const database = e.target.result;

      // Employee table
      if (!database.objectStoreNames.contains('employees')) {
        const empStore = database.createObjectStore('employees', { keyPath: 'empId' });
        empStore.createIndex('name', 'name', { unique: false });
        empStore.createIndex('department', 'department', { unique: false });
      }

      // Attendance records table (composite key: date_empId)
      if (!database.objectStoreNames.contains('attendance')) {
        const attStore = database.createObjectStore('attendance', { keyPath: 'recordId' });
        attStore.createIndex('date', 'date', { unique: false });
        attStore.createIndex('empId', 'empId', { unique: false });
        attStore.createIndex('isSynced', 'isSynced', { unique: false });
      }
    };

    request.onsuccess = (e) => {
      db = e.target.result;
      console.log('IndexedDB initialized successfully');
      resolve(db);
    };

    request.onerror = (e) => {
      console.error('IndexedDB error:', e);
      reject(e);
    };
  });
}

// Database Helper methods
const Storage = {
  // Employee methods
  addEmployee: (emp) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['employees'], 'readwrite');
      const store = tx.objectStore('employees');
      const req = store.put(emp);
      req.onsuccess = () => resolve(emp);
      req.onerror = (e) => reject(e);
    });
  },

  getAllEmployees: () => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['employees'], 'readonly');
      const store = tx.objectStore('employees');
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = (e) => reject(e);
    });
  },

  getEmployee: (empId) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['employees'], 'readonly');
      const store = tx.objectStore('employees');
      const req = store.get(empId);
      req.onsuccess = () => resolve(req.result);
      req.onerror = (e) => reject(e);
    });
  },

  deleteEmployee: (empId) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['employees'], 'readwrite');
      const store = tx.objectStore('employees');
      const req = store.delete(empId);
      req.onsuccess = () => resolve();
      req.onerror = (e) => reject(e);
    });
  },

  // Attendance methods
  saveAttendance: (record) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['attendance'], 'readwrite');
      const store = tx.objectStore('attendance');
      const req = store.put(record);
      req.onsuccess = () => resolve(record);
      req.onerror = (e) => reject(e);
    });
  },

  getAttendanceRecord: (recordId) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['attendance'], 'readonly');
      const store = tx.objectStore('attendance');
      const req = store.get(recordId);
      req.onsuccess = () => resolve(req.result);
      req.onerror = (e) => reject(e);
    });
  },

  getAttendanceByDate: (dateStr) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['attendance'], 'readonly');
      const store = tx.objectStore('attendance');
      const index = store.index('date');
      const req = index.getAll(dateStr);
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = (e) => reject(e);
    });
  },

  getAllAttendance: () => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['attendance'], 'readonly');
      const store = tx.objectStore('attendance');
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = (e) => reject(e);
    });
  },

  getUnsyncedAttendance: () => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['attendance'], 'readonly');
      const store = tx.objectStore('attendance');
      const index = store.index('isSynced');
      const req = index.getAll(0);
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = (e) => reject(e);
    });
  },

  markAsSynced: (recordIds) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['attendance'], 'readwrite');
      const store = tx.objectStore('attendance');
      recordIds.forEach(id => {
        const getReq = store.get(id);
        getReq.onsuccess = () => {
          if (getReq.result) {
            const updated = getReq.result;
            updated.isSynced = 1;
            store.put(updated);
          }
        };
      });
      tx.oncomplete = () => resolve();
      tx.onerror = (e) => reject(e);
    });
  },

  clearAllData: () => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['employees', 'attendance'], 'readwrite');
      tx.objectStore('employees').clear();
      tx.objectStore('attendance').clear();
      tx.oncomplete = () => resolve();
      tx.onerror = (e) => reject(e);
    });
  }
};

// ==========================================
// 2. AUDIO & HAPTIC FEEDBACK
// ==========================================
const Sound = {
  ctx: null,
  init: () => {
    if (!Sound.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) Sound.ctx = new AudioContext();
    }
  },
  playSuccess: () => {
    Sound.init();
    if (!Sound.ctx) return;
    try {
      const now = Sound.ctx.currentTime;
      const osc = Sound.ctx.createOscillator();
      const gain = Sound.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, now); // D5
      osc.frequency.setValueAtTime(880.00, now + 0.1); // A5
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(gain);
      gain.connect(Sound.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.35);
    } catch (e) {
      console.warn('Audio play error:', e);
    }
  },
  playCheckout: () => {
    Sound.init();
    if (!Sound.ctx) return;
    try {
      const now = Sound.ctx.currentTime;
      const osc = Sound.ctx.createOscillator();
      const gain = Sound.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(784.00, now); // G5
      osc.frequency.setValueAtTime(523.25, now + 0.12); // C5
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
      osc.connect(gain);
      gain.connect(Sound.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.4);
    } catch (e) {
      console.warn('Audio play error:', e);
    }
  },
  playWarning: () => {
    Sound.init();
    if (!Sound.ctx) return;
    try {
      const now = Sound.ctx.currentTime;
      const osc = Sound.ctx.createOscillator();
      const gain = Sound.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(350, now);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      osc.connect(gain);
      gain.connect(Sound.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.25);
    } catch (e) {}
  },
  vibrate: (pattern = [100, 50, 100]) => {
    if ('vibrate' in navigator) {
      try { navigator.vibrate(pattern); } catch (e) {}
    }
  }
};

// ==========================================
// 3. CORE ATTENDANCE SCAN LOGIC
// ==========================================
async function processScannedEmployee(scannedData) {
  const now = new Date();
  const todayStr = getTodayDateString(now);
  const currentTimeStr = formatTimeAMPM(now);

  // Parse QR content (supports JSON format or raw Employee ID)
  let empId = scannedData.trim();
  let rawName = "";
  let rawDept = "";

  if (scannedData.startsWith('{') && scannedData.endsWith('}')) {
    try {
      const parsed = JSON.parse(scannedData);
      empId = parsed.empId || parsed.id || empId;
      rawName = parsed.name || "";
      rawDept = parsed.department || "";
    } catch (e) {
      console.warn('QR parse as JSON failed, using raw string');
    }
  } else if (scannedData.startsWith('EMP:')) {
    empId = scannedData.replace('EMP:', '').trim();
  }

  // Look up employee in local database
  let employee = await Storage.getEmployee(empId);
  if (!employee) {
    // If not pre-registered, auto-create a temp record so guards are not blocked!
    employee = {
      empId: empId,
      name: rawName || `Employee ${empId}`,
      department: rawDept || "General Staff",
      phone: "",
      createdAt: now.toISOString()
    };
    await Storage.addEmployee(employee);
    renderEmployeeList();
  }

  const recordId = `${todayStr}_${empId}`;
  let record = await Storage.getAttendanceRecord(recordId);

  const feedbackCard = document.getElementById('feedbackCard');
  const feedbackAvatar = document.getElementById('feedbackAvatar');
  const feedbackEmpName = document.getElementById('feedbackEmpName');
  const feedbackEmpDetails = document.getElementById('feedbackEmpDetails');
  const feedbackTitleText = document.getElementById('feedbackTitleText');
  const feedbackTimeChip = document.getElementById('feedbackTimeChip');
  const feedbackTimestamp = document.getElementById('feedbackTimestamp');

  feedbackAvatar.textContent = getInitials(employee.name);
  feedbackEmpName.textContent = employee.name;
  feedbackEmpDetails.textContent = `${employee.empId} • ${employee.department}`;
  feedbackTimestamp.textContent = currentTimeStr;

  feedbackCard.className = 'feedback-card'; // reset classes

  if (!record) {
    // CASE 1: FIRST SCAN OF THE DAY -> MARK CHECK-IN
    record = {
      recordId: recordId,
      empId: employee.empId,
      empName: employee.name,
      department: employee.department,
      date: todayStr,
      inTime: currentTimeStr,
      inTimestamp: now.getTime(),
      outTime: "",
      outTimestamp: null,
      totalHours: "",
      status: "Checked In",
      isSynced: 0,
      updatedAt: now.toISOString()
    };

    await Storage.saveAttendance(record);
    Sound.playSuccess();
    Sound.vibrate([120]);

    feedbackCard.classList.add('checkin');
    feedbackTitleText.textContent = 'CHECK-IN RECORDED (Arrival)';
    feedbackTimeChip.textContent = `In Time: ${currentTimeStr}`;
    feedbackCard.style.display = 'block';

  } else if (record.inTime && (!record.outTime || record.outTime === "")) {
    // CASE 2: SECOND SCAN OF THE DAY -> MARK CHECK-OUT
    const inTimeDate = new Date(record.inTimestamp || now.getTime());
    const durationMs = Math.max(0, now.getTime() - inTimeDate.getTime());
    const durationFormatted = formatDuration(durationMs);

    record.outTime = currentTimeStr;
    record.outTimestamp = now.getTime();
    record.totalHours = durationFormatted;
    record.status = "Completed";
    record.isSynced = 0; // Mark unsynced so updated outTime pushes to Google Sheets
    record.updatedAt = now.toISOString();

    await Storage.saveAttendance(record);
    Sound.playCheckout();
    Sound.vibrate([100, 80, 100]);

    feedbackCard.classList.add('checkout');
    feedbackTitleText.textContent = 'CHECK-OUT RECORDED (Departure)';
    feedbackTimeChip.textContent = `Out: ${currentTimeStr} • Duration: ${durationFormatted}`;
    feedbackCard.style.display = 'block';

  } else {
    // CASE 3: ALREADY CHECKED IN AND CHECKED OUT
    Sound.playWarning();
    Sound.vibrate([200]);

    feedbackCard.classList.add('already');
    feedbackTitleText.textContent = 'ALREADY LOGGED TODAY';
    feedbackTimeChip.textContent = `In: ${record.inTime} | Out: ${record.outTime} (${record.totalHours})`;
    feedbackCard.style.display = 'block';
  }

  // Update UI components
  updatePendingCounter();
  renderAttendanceStats();
  renderRecentScans();
  renderAttendanceLogs();

  // Auto-sync in background if internet is active
  if (navigator.onLine) {
    syncPendingRecords(true); // silent sync
  }
}

// ==========================================
// 4. CAMERA SCANNER HANDLERS
// ==========================================
function startCameraScanner() {
  const readerElement = document.getElementById("reader");
  if (!readerElement) return;

  const btnCameraText = document.getElementById("btnCameraText");
  const scannerStatusText = document.getElementById("scannerStatusText");

  if (!html5QrCodeScanner) {
    html5QrCodeScanner = new Html5Qrcode("reader");
  }

  const config = {
    fps: 15,
    qrbox: { width: 220, height: 220 },
    aspectRatio: 1.0
  };

  html5QrCodeScanner.start(
    { facingMode: currentCameraFacing },
    config,
    onQrScanSuccess,
    onQrScanError
  ).then(() => {
    isScannerActive = true;
    btnCameraText.textContent = "Stop Camera";
    scannerStatusText.textContent = "Scanning Active";
    scannerStatusText.style.color = "#4ade80";
    document.getElementById("scanLaserOverlay").style.display = "block";
  }).catch((err) => {
    console.error("Camera start error:", err);
    scannerStatusText.textContent = "Camera Error / No Permission";
    scannerStatusText.style.color = "#f87171";
    alert("Could not access camera. Please ensure camera permissions are allowed in Chrome or your Android settings.");
  });
}

function stopCameraScanner() {
  if (html5QrCodeScanner && isScannerActive) {
    html5QrCodeScanner.stop().then(() => {
      isScannerActive = false;
      document.getElementById("btnCameraText").textContent = "Start Camera";
      document.getElementById("scannerStatusText").textContent = "Stopped";
      document.getElementById("scannerStatusText").style.color = "#94a3b8";
      document.getElementById("scanLaserOverlay").style.display = "none";
    }).catch(err => console.warn(err));
  }
}

function toggleCameraScanner() {
  if (isScannerActive) {
    stopCameraScanner();
  } else {
    startCameraScanner();
  }
}

function switchCamera() {
  currentCameraFacing = currentCameraFacing === "environment" ? "user" : "environment";
  if (isScannerActive) {
    stopCameraScanner();
    setTimeout(() => startCameraScanner(), 300);
  }
}

function onQrScanSuccess(decodedText, decodedResult) {
  const now = Date.now();
  // Prevent duplicate scan triggering within 2.5 seconds
  if (decodedText === lastScannedEmpId && (now - lastScanTimestamp) < 2500) {
    return;
  }
  lastScanTimestamp = now;
  lastScannedEmpId = decodedText;

  console.log("QR Code Scanned:", decodedText);
  processScannedEmployee(decodedText);
}

function onQrScanError(errorMessage) {
  // Silent frame parse error (occurs when no QR code in frame)
}

// Prompt simulated test scan for testing without camera
async function promptSimulatedScan() {
  const employees = await Storage.getAllEmployees();
  if (employees.length === 0) {
    alert("No employees registered yet. Please add an employee or click 'Load Sample Employees' in Settings.");
    return;
  }

  const empOptions = employees.map((e, idx) => `${idx + 1}. [${e.empId}] ${e.name} (${e.department})`).join('\n');
  const selection = prompt(`SELECT EMPLOYEE TO TEST SCAN:\n\n${empOptions}\n\nEnter number (1-${employees.length}) or type an Employee ID:`);

  if (!selection) return;

  const num = parseInt(selection);
  if (!isNaN(num) && num >= 1 && num <= employees.length) {
    processScannedEmployee(employees[num - 1].empId);
  } else {
    processScannedEmployee(selection.trim());
  }
}

// ==========================================
// 5. GOOGLE SHEETS OFFLINE SYNC ENGINE
// ==========================================
async function syncPendingRecords(isSilent = false) {
  const scriptUrl = localStorage.getItem('googleScriptUrl') || '';
  if (!scriptUrl) {
    if (!isSilent) {
      alert("Please configure your Google Apps Script Web App URL in the 'Settings' tab first.");
      switchTab('settings', document.querySelectorAll('.nav-item')[3]);
    }
    return;
  }

  if (!navigator.onLine) {
    if (!isSilent) alert("Device is currently OFFLINE. Records are stored safely locally and will sync once internet is back.");
    return;
  }

  const unsynced = await Storage.getUnsyncedAttendance();
  if (unsynced.length === 0) {
    if (!isSilent) alert("All attendance records are already synced to your Google Sheet! No pending records.");
    return;
  }

  try {
    const payload = {
      action: "syncAttendance",
      records: unsynced.map(r => ({
        empId: r.empId,
        empName: r.empName,
        department: r.department,
        date: r.date,
        inTime: r.inTime || "",
        outTime: r.outTime || "",
        totalHours: r.totalHours || "",
        status: r.status || "",
        syncTime: new Date().toISOString()
      }))
    };

    // Google Apps Script requires text/plain or no-cors handling for cross-origin web apps
    const response = await fetch(scriptUrl, {
      method: "POST",
      body: JSON.stringify(payload),
      headers: { "Content-Type": "text/plain;charset=utf-8" }
    });

    const resultText = await response.text();
    console.log("Google Sheet sync response:", resultText);

    // Mark as synced locally
    const syncedIds = unsynced.map(r => r.recordId);
    await Storage.markAsSynced(syncedIds);

    updatePendingCounter();
    renderAttendanceLogs();

    if (!isSilent) {
      alert(`Success! ${unsynced.length} attendance record(s) synced to Google Sheet.`);
    }

  } catch (error) {
    console.error("Sync error:", error);
    if (!isSilent) {
      alert(`Sync failed: ${error.message}. Records remain stored safely on your device.`);
    }
  }
}

async function testSheetConnection() {
  const scriptUrl = localStorage.getItem('googleScriptUrl') || '';
  if (!scriptUrl) {
    alert("Please enter a Google Apps Script URL first.");
    return;
  }

  try {
    const res = await fetch(scriptUrl);
    const data = await res.json();
    if (data.status === "ok") {
      alert("Connection Successful! Google Apps Script is active and responding.");
    } else {
      alert("Received unexpected response: " + JSON.stringify(data));
    }
  } catch (err) {
    alert("Failed to connect to Google Apps Script. Please verify the URL and ensure access is set to 'Anyone'. Error: " + err.message);
  }
}

// ==========================================
// 6. EMPLOYEE MANAGEMENT & QR GENERATION
// ==========================================
async function handleEmployeeSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('empName').value.trim();
  const empId = document.getElementById('empId').value.trim().toUpperCase();
  const department = document.getElementById('empDept').value.trim();
  const phone = document.getElementById('empPhone').value.trim();

  if (!name || !empId) {
    alert("Name and Employee ID are required.");
    return;
  }

  const employee = {
    empId: empId,
    name: name,
    department: department || "General",
    phone: phone || "",
    createdAt: new Date().toISOString()
  };

  await Storage.addEmployee(employee);
  closeAddEmployeeModal();
  renderEmployeeList();
  openQrModal(empId);
}

async function renderEmployeeList() {
  const container = document.getElementById('employeesListContainer');
  if (!container) return;

  const searchQuery = (document.getElementById('employeeSearchInput')?.value || '').toLowerCase();
  const employees = await Storage.getAllEmployees();

  const filtered = employees.filter(emp => {
    return emp.name.toLowerCase().includes(searchQuery) ||
           emp.empId.toLowerCase().includes(searchQuery) ||
           emp.department.toLowerCase().includes(searchQuery);
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 30px; color: var(--text-muted);">
        <i data-lucide="users" style="width: 42px; height: 42px; margin-bottom: 8px; opacity: 0.5;"></i>
        <p>No employees found.</p>
        <p style="font-size: 0.78rem; margin-top: 4px;">Click "Add Employee" to create one.</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  container.innerHTML = filtered.map(emp => `
    <div class="emp-item">
      <div class="emp-info">
        <div class="emp-avatar">${getInitials(emp.name)}</div>
        <div>
          <h4>${escapeHtml(emp.name)}</h4>
          <p><b style="color: #60a5fa;">${escapeHtml(emp.empId)}</b> &bull; ${escapeHtml(emp.department)}</p>
          ${emp.phone ? `<p style="font-size: 0.72rem;">📞 ${escapeHtml(emp.phone)}</p>` : ''}
        </div>
      </div>
      <div class="emp-actions">
        <button class="btn btn-primary btn-sm" onclick="openQrModal('${escapeHtml(emp.empId)}')">
          <i data-lucide="qr-code"></i> QR Card
        </button>
        <button class="btn btn-secondary btn-sm" onclick="confirmDeleteEmployee('${escapeHtml(emp.empId)}')">
          <i data-lucide="trash-2" style="color: #f87171;"></i>
        </button>
      </div>
    </div>
  `).join('');

  lucide.createIcons();
}

async function confirmDeleteEmployee(empId) {
  if (confirm(`Are you sure you want to delete employee ${empId}?`)) {
    await Storage.deleteEmployee(empId);
    renderEmployeeList();
  }
}

// QR Modal & Generation
let currentQrCodeInstance = null;

async function openQrModal(empId) {
  const employee = await Storage.getEmployee(empId);
  if (!employee) return;

  document.getElementById('badgeEmpName').textContent = employee.name;
  document.getElementById('badgeEmpId').textContent = employee.empId;
  document.getElementById('badgeEmpDept').textContent = employee.department;
  document.getElementById('badgeEmpPhone').textContent = employee.phone ? `Phone: ${employee.phone}` : '';

  const qrContainer = document.getElementById('qrCodeContainer');
  qrContainer.innerHTML = '';

  // QR Code payload: JSON containing empId and name
  const qrPayload = JSON.stringify({
    type: "ATTENDANCE_EMP",
    empId: employee.empId,
    name: employee.name,
    department: employee.department
  });

  currentQrCodeInstance = new QRCode(qrContainer, {
    text: qrPayload,
    width: 180,
    height: 180,
    colorDark: "#0f172a",
    colorLight: "#ffffff",
    correctLevel: QRCode.CorrectLevel.H
  });

  document.getElementById('qrModal').classList.add('open');
  lucide.createIcons();
}

function closeQrModal() {
  document.getElementById('qrModal').classList.remove('open');
}

function downloadQrBadgeImage() {
  const qrCanvas = document.querySelector('#qrCodeContainer canvas');
  const empId = document.getElementById('badgeEmpId').textContent || 'EMP';
  if (qrCanvas) {
    const link = document.createElement('a');
    link.download = `QR_${empId}.png`;
    link.href = qrCanvas.toDataURL('image/png');
    link.click();
  }
}

function openAddEmployeeModal() {
  document.getElementById('empName').value = '';
  document.getElementById('empId').value = 'EMP' + Math.floor(100 + Math.random() * 900);
  document.getElementById('empDept').value = '';
  document.getElementById('empPhone').value = '';
  document.getElementById('addEmployeeModal').classList.add('open');
  lucide.createIcons();
}

function closeAddEmployeeModal() {
  document.getElementById('addEmployeeModal').classList.remove('open');
}

// ==========================================
// 7. ATTENDANCE LOGS & STATS UI
// ==========================================
async function renderAttendanceLogs() {
  const container = document.getElementById('attendanceLogsContainer');
  if (!container) return;

  const dateFilterInput = document.getElementById('logDateFilter');
  const targetDate = dateFilterInput.value || getTodayDateString(new Date());

  const records = await Storage.getAttendanceByDate(targetDate);

  if (records.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <i data-lucide="calendar-x" style="width: 40px; height: 40px; margin-bottom: 8px; opacity: 0.5;"></i>
        <p>No attendance records for ${targetDate}.</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  container.innerHTML = records.map(r => `
    <div class="card" style="margin-bottom: 10px; padding: 12px 14px;">
      <div class="card-header-flex" style="margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <div class="emp-avatar" style="width: 36px; height: 36px; font-size: 0.9rem;">
            ${getInitials(r.empName)}
          </div>
          <div>
            <h4 style="font-size: 0.95rem;">${escapeHtml(r.empName)}</h4>
            <p style="font-size: 0.74rem; color: var(--text-muted);">${escapeHtml(r.empId)} &bull; ${escapeHtml(r.department)}</p>
          </div>
        </div>
        <div>
          ${r.isSynced === 1 
            ? `<span class="badge" style="background: rgba(34, 197, 94, 0.15); color: #4ade80;"><i data-lucide="check-check"></i> Synced</span>`
            : `<span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24;"><i data-lucide="clock"></i> Pending</span>`}
        </div>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; background: #0f172a; padding: 8px 12px; border-radius: 8px;">
        <div>
          <span style="color: var(--text-muted);">In:</span> 
          <b style="color: #4ade80;">${r.inTime || '--:--'}</b>
        </div>
        <div>
          <span style="color: var(--text-muted);">Out:</span> 
          <b style="color: #60a5fa;">${r.outTime || 'Pending'}</b>
        </div>
        <div>
          <span style="color: var(--text-muted);">Duration:</span> 
          <b>${r.totalHours || '--'}</b>
        </div>
      </div>
    </div>
  `).join('');

  lucide.createIcons();
}

async function renderAttendanceStats() {
  const todayStr = getTodayDateString(new Date());
  const records = await Storage.getAttendanceByDate(todayStr);

  const presentCount = records.length;
  const departedCount = records.filter(r => r.outTime && r.outTime !== '').length;
  const insideCount = presentCount - departedCount;

  const statPresent = document.getElementById('statPresentCount');
  const statInside = document.getElementById('statInsideCount');
  const statDeparted = document.getElementById('statDepartedCount');

  if (statPresent) statPresent.textContent = presentCount;
  if (statInside) statInside.textContent = insideCount;
  if (statDeparted) statDeparted.textContent = departedCount;
}

async function renderRecentScans() {
  const recentContainer = document.getElementById('recentScansList');
  if (!recentContainer) return;

  const todayStr = getTodayDateString(new Date());
  const records = await Storage.getAttendanceByDate(todayStr);

  if (records.length === 0) {
    recentContainer.innerHTML = `<p style="font-size: 0.82rem; color: var(--text-muted); text-align: center; padding: 12px;">No scans recorded yet today.</p>`;
    return;
  }

  // Sort descending by updated timestamp
  const sorted = records.sort((a, b) => (b.outTimestamp || b.inTimestamp || 0) - (a.outTimestamp || a.inTimestamp || 0)).slice(0, 4);

  recentContainer.innerHTML = sorted.map(r => `
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--surface-border);">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="width: 8px; height: 8px; border-radius: 50%; background: ${r.outTime ? '#3b82f6' : '#22c55e'};"></span>
        <span style="font-size: 0.88rem; font-weight: 600;">${escapeHtml(r.empName)}</span>
      </div>
      <div style="font-size: 0.78rem; color: var(--text-muted);">
        ${r.outTime ? `Left at ${r.outTime}` : `Entered at ${r.inTime}`}
      </div>
    </div>
  `).join('');
}

async function updatePendingCounter() {
  const unsynced = await Storage.getUnsyncedAttendance();
  const count = unsynced.length;

  const syncBadge = document.getElementById('syncBadge');
  const pendingCountSpan = document.getElementById('pendingCount');
  const pendingRecordsText = document.getElementById('pendingRecordsText');

  if (pendingCountSpan) pendingCountSpan.textContent = `${count} unsynced`;
  if (pendingRecordsText) pendingRecordsText.textContent = `${count} records`;

  if (syncBadge) {
    syncBadge.style.display = count > 0 ? 'inline-flex' : 'none';
  }
}

// ==========================================
// 8. DATA EXPORT & DEMO DATA
// ==========================================
async function exportAttendanceCSV() {
  const records = await Storage.getAllAttendance();
  if (records.length === 0) {
    alert("No attendance records to export.");
    return;
  }

  const headers = ["Date", "Employee ID", "Employee Name", "Department", "In Time", "Out Time", "Total Hours", "Status", "Synced"];
  const rows = records.map(r => [
    r.date,
    r.empId,
    `"${r.empName}"`,
    `"${r.department}"`,
    r.inTime || "",
    r.outTime || "",
    r.totalHours || "",
    r.status || "",
    r.isSynced === 1 ? "Yes" : "No"
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `attendance_export_${getTodayDateString(new Date())}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function loadSampleEmployees() {
  const samples = [
    { empId: "EMP101", name: "Rahul Sharma", department: "Operations", phone: "+91 98765 43210" },
    { empId: "EMP102", name: "Priya Patel", department: "HR & Admin", phone: "+91 98765 43211" },
    { empId: "EMP103", name: "Amit Verma", department: "Security", phone: "+91 98765 43212" },
    { empId: "EMP104", name: "Sneha Reddy", department: "IT Support", phone: "+91 98765 43213" },
    { empId: "EMP105", name: "Vikas Singh", department: "Logistics", phone: "+91 98765 43214" }
  ];

  for (const emp of samples) {
    await Storage.addEmployee({
      ...emp,
      createdAt: new Date().toISOString()
    });
  }

  alert("5 sample employees loaded successfully! Check the Employees tab to generate their QR codes.");
  renderEmployeeList();
}

async function clearAllData() {
  if (confirm("Are you sure you want to reset all local data? This will clear all employees and attendance logs stored on this device.")) {
    await Storage.clearAllData();
    location.reload();
  }
}

// ==========================================
// 9. SETTINGS & APP LIFECYCLE
// ==========================================
function saveSettings() {
  const url = document.getElementById('scriptUrlInput').value.trim();
  localStorage.setItem('googleScriptUrl', url);
  alert("Settings saved successfully!");
  updatePendingCounter();
}

function switchTab(tabId, el) {
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));

  const targetPane = document.getElementById(`tab-${tabId}`);
  if (targetPane) targetPane.classList.add('active');
  if (el) el.classList.add('active');

  // Stop camera if navigating away from scanner tab to preserve battery
  if (tabId !== 'scanner' && isScannerActive) {
    stopCameraScanner();
  }

  // Refresh tab contents
  if (tabId === 'employees') renderEmployeeList();
  if (tabId === 'logs') renderAttendanceLogs();
  if (tabId === 'scanner') {
    renderAttendanceStats();
    renderRecentScans();
  }
}

// Network status listeners
function handleNetworkChange() {
  const networkBadge = document.getElementById('networkBadge');
  const networkText = document.getElementById('networkText');

  if (navigator.onLine) {
    networkBadge.className = 'badge badge-online';
    networkText.textContent = 'Online';
    // When back online, attempt sync immediately
    syncPendingRecords(true);
  } else {
    networkBadge.className = 'badge badge-offline';
    networkText.textContent = 'Offline';
  }
}

window.addEventListener('online', handleNetworkChange);
window.addEventListener('offline', handleNetworkChange);

// Utility functions
function getTodayDateString(d) {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatTimeAMPM(date) {
  let hours = date.getHours();
  let minutes = date.getMinutes();
  let seconds = date.getSeconds();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // 0 hour is 12
  minutes = minutes < 10 ? '0' + minutes : minutes;
  seconds = seconds < 10 ? '0' + seconds : seconds;
  return `${hours}:${minutes}:${seconds} ${ampm}`;
}

function formatDuration(ms) {
  const totalMinutes = Math.floor(ms / (1000 * 60));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours === 0) return `${minutes}m`;
  return `${hours}h ${minutes}m`;
}

function getInitials(name) {
  if (!name) return "EM";
  const parts = name.trim().split(" ");
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// ==========================================
// 10. APP BOOTSTRAP
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
  try {
    await initDatabase();
    handleNetworkChange();

    // Set today's date in log filter
    const logDateFilter = document.getElementById('logDateFilter');
    if (logDateFilter) logDateFilter.value = getTodayDateString(new Date());

    const todayDateLabel = document.getElementById('todayDateLabel');
    if (todayDateLabel) todayDateLabel.textContent = new Date().toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });

    // Load saved settings
    const savedUrl = localStorage.getItem('googleScriptUrl');
    if (savedUrl) {
      document.getElementById('scriptUrlInput').value = savedUrl;
    }

    renderEmployeeList();
    renderAttendanceStats();
    renderRecentScans();
    renderAttendanceLogs();
    updatePendingCounter();

  } catch (err) {
    console.error("App init error:", err);
  }
});
