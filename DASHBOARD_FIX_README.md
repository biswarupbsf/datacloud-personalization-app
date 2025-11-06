# Dashboard Loading Issue - Quick Fix

## Problem
The Data Cloud analytics cards show "Loading..." but never update with actual numbers.

## Diagnosis Steps

### 1. Check Browser Console
Press **F12** (or **Cmd+Option+I** on Mac) to open Developer Tools, then:

1. Go to the **Console** tab
2. Refresh the page
3. Look for any red errors
4. Check if you see these logs:
   - "Loading Data Cloud stats..."
   - "Data Cloud stats response: {...}"

### 2. Check Network Tab
1. Open **Network** tab in Developer Tools
2. Refresh the page
3. Look for request to `/api/analytics/datacloud`
4. Click on it and check:
   - **Status**: Should be 200
   - **Response**: Should have `total_records` object

### 3. Manual API Test
Open this URL in a new tab (while logged in):
```
http://localhost:5001/api/analytics/datacloud
```

You should see JSON like:
```json
{
  "total_records": {
    "email_engagements": 12789953,
    "message_engagements": 19851,
    "website_events": 339598,
    "orders": 312559
  }
}
```

If you see `"error": "Not logged in"`, that's the problem.

### 4. Check Debug Status
Visit:
```
http://localhost:5001/api/debug/status
```

Should show:
```json
{
  "session_connected": true,
  "sf_manager_connected": true,
  "session_keys": ["connected", "username", "password", ...],
  "sf_instance": "https://sftutor.my.salesforce.com"
}
```

## Common Issues

### Issue 1: JavaScript Not Executing
**Symptom**: No console logs appear
**Fix**: Browser cache issue - hard refresh with Cmd+Shift+R

### Issue 2: Session Lost
**Symptom**: API returns error "Not logged in"
**Fix**: Log out and log back in

### Issue 3: Connection Lost After Reload
**Symptom**: `sf_manager_connected: false` but `session_connected: true`
**Fix**: The auto-reconnect should handle this, but may need manual re-login

## Quick Fix Commands

Try these in your browser console:

```javascript
// Force reload stats
loadDataCloudStats();

// Check if function exists
typeof loadDataCloudStats;

// Manual API call
fetch('/api/analytics/datacloud').then(r => r.json()).then(console.log);
```

## If Nothing Works

Please share:
1. Any errors from Console tab
2. The response from `/api/analytics/datacloud`  
3. The response from `/api/debug/status`

This will help identify the exact issue!



