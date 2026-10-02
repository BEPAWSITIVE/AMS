import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../database/db_helper.dart';

class SyncService {
  static final SyncService instance = SyncService._init();
  SyncService._init();

  static const String PREF_SHEET_URL = 'google_sheet_url';

  Future<String?> getGoogleSheetUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(PREF_SHEET_URL);
  }

  Future<void> saveGoogleSheetUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(PREF_SHEET_URL, url.trim());
  }

  Future<bool> isConnected() async {
    final connectivityResult = await Connectivity().checkConnectivity();
    return !connectivityResult.contains(ConnectivityResult.none);
  }

  Future<Map<String, dynamic>> syncPendingAttendance() async {
    final bool online = await isConnected();
    if (!online) {
      return {'success': false, 'message': 'Device is offline. Records remain saved locally.'};
    }

    final scriptUrl = await getGoogleSheetUrl();
    if (scriptUrl == null || scriptUrl.isEmpty) {
      return {'success': false, 'message': 'Google Sheet Web App URL is not configured in Settings.'};
    }

    final unsynced = await DBHelper.instance.getUnsyncedAttendance();
    if (unsynced.isEmpty) {
      return {'success': true, 'message': 'All records are already synced.', 'count': 0};
    }

    try {
      final payload = {
        'action': 'syncAttendance',
        'records': unsynced.map((r) => {
          'empId': r.empId,
          'empName': r.empName,
          'department': r.department,
          'date': r.date,
          'inTime': r.inTime,
          'outTime': r.outTime ?? '',
          'totalHours': r.totalHours ?? '',
          'status': r.status,
          'syncTime': DateTime.now().toIso8601String(),
        }).toList(),
      };

      final response = await http.post(
        Uri.parse(scriptUrl),
        body: jsonEncode(payload),
        headers: {'Content-Type': 'text/plain;charset=utf-8'},
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200 || response.statusCode == 302) {
        final List<String> syncedIds = unsynced.map((r) => r.recordId).toList();
        await DBHelper.instance.markRecordsAsSynced(syncedIds);
        return {
          'success': true,
          'message': 'Successfully synced ${unsynced.length} record(s) to Google Sheets.',
          'count': unsynced.length
        };
      } else {
        return {
          'success': false,
          'message': 'Server responded with status code ${response.statusCode}'
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Sync error: $e'
      };
    }
  }
}
