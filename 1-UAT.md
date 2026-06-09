# 1-UAT.md — CafeArchive Sprint 1

## Test Session: 2026-06-10

### Test 1: Flutter Analyze
- **Command:** `flutter analyze`
- **Result:** PASS — No issues found
- **Details:** 0 errors, 0 warnings after fixing test file reference

### Test 2: Android APK Build
- **Command:** `flutter build apk --debug`
- **Result:** PASS — 150MB APK generated
- **File:** `build/app/outputs/flutter-apk/app-debug.apk`

### Test 3: FastAPI Health
- **Command:** `curl -s http://127.0.0.1:8000/health`
- **Result:** PASS — `{"status":"ok","service":"CafeArchive Vision API"}`
- **Details:** Server running, API responsive

### Test 4: Image Upload Validation
- **Command:** `curl -s -X POST -F "file=@/dev/null" http://127.0.0.1:8000/api/analyze`
- **Result:** PASS — `{"detail":"Only image files accepted"}`
- **Details:** Content-Type validation works

### Test 5: Android Device Connection
- **Attempt:** `adb devices` → daemon started, no devices found
- **Status:** BLOCKED — USB not connected, wireless debugging requires initial USB pairing
- **Fix:** Connect phone via USB once, then enable wireless debugging for subsequent sessions

### Test 6: APK Installation on Device
- **Attempt:** `adb install .../app-debug.apk`
- **Status:** BLOCKED — no device connected, cannot install APK
- **Fix:** Same as Test 5 — USB connection needed first

## Summary
- **Passed:** 4/6 tests
- **Blocked:** 2/6 (device not connected — needs USB)
- **Overall:** PASS with limitations (code compiles, APK builds, backend runs; device testing blocked by USB connection)

## Next
- [ ] Connect Android phone via USB → enable wireless debugging
- [ ] Install APK on device → verify camera + result flow
- [ ] iOS: build and run on simulator (Xcode available but not tested)
- [ ] Sprint 2: OCR integration in FastAPI backend