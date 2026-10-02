function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "ok",
    message: "Attendance Manager API is running",
    timestamp: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(30000);
  
  try {
    var contents = e.postData.contents;
    var data = JSON.parse(contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("Attendance");
    
    if (!sheet) {
      sheet = ss.insertSheet("Attendance");
    }
    
    // Auto-create header row if sheet is empty
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["Date", "Employee ID", "Employee Name", "Department", "In Time", "Out Time", "Total Hours", "Status", "Last Synced"]);
      var headerRange = sheet.getRange(1, 1, 1, 9);
      headerRange.setFontWeight("bold");
      headerRange.setBackground("#1E3A8A");
      headerRange.setFontColor("#FFFFFF");
      sheet.setFrozenRows(1);
    }
    
    var records = data.records || [];
    var lastRow = sheet.getLastRow();
    var rows = lastRow > 1 ? sheet.getRange(2, 1, lastRow - 1, 9).getValues() : [];
    
    records.forEach(function(rec) {
      var dateStr = (rec.date || "").toString().trim();
      var empIdStr = (rec.empId || "").toString().trim();
      var foundRow = -1;
      
      for (var i = 0; i < rows.length; i++) {
        var rDate = rows[i][0];
        if (rDate instanceof Date) {
          var y = rDate.getFullYear();
          var m = ("0" + (rDate.getMonth() + 1)).slice(-2);
          var d = ("0" + rDate.getDate()).slice(-2);
          rDate = y + "-" + m + "-" + d;
        }
        rDate = (rDate || "").toString().trim();
        var rId = (rows[i][1] || "").toString().trim();
        
        if (rDate === dateStr && rId === empIdStr) {
          foundRow = i + 2;
          break;
        }
      }
      
      var nowStr = new Date().toLocaleString();
      var status = rec.outTime ? "Completed" : "Checked In";
      
      if (foundRow > 0) {
        // Update existing row (e.g. check-out on same day)
        var range = sheet.getRange(foundRow, 1, 1, 9);
        var cur = range.getValues()[0];
        var finalIn = rec.inTime || cur[4];
        var finalOut = rec.outTime || cur[5];
        var finalHours = rec.totalHours || cur[6];
        
        range.setValues([[
          dateStr,
          empIdStr,
          rec.empName || cur[2],
          rec.department || cur[3],
          finalIn,
          finalOut,
          finalHours,
          status,
          nowStr
        ]]);
      } else {
        // Append new attendance row
        sheet.appendRow([
          dateStr,
          empIdStr,
          rec.empName || "",
          rec.department || "",
          rec.inTime || "",
          rec.outTime || "",
          rec.totalHours || "",
          status,
          nowStr
        ]);
      }
    });
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      count: records.length,
      message: "Attendance records synced successfully"
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
