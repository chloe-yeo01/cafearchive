# SECURITY.md — CafeArchive Sprint 1

## Threat Model

### T1: Malicious Image Upload
- **Risk:** Large files → OOM, crafted images → exploit parser
- **Mitigation:** 
  - FastAPI: Content-Type validation (image/* only) — already implemented
  - File size limit: 10MB max — implement in Sprint 2
  - Rate limiting: 10 req/min per IP — implement in Sprint 2

### T2: Unauthenticated API Access
- **Risk:** Anyone on LAN can call /api/analyze
- **Mitigation:** Local-only (127.0.0.1 binding) — acceptable for MVP, Sprint 4 add auth if needed

### T3: Image Metadata Leakage
- **Risk:** EXIF GPS data in uploaded photos exposes user location
- **Mitigation:** Strip EXIF before processing — Sprint 2

### T4: Dependency Supply Chain
- **Risk:** Malicious packages in pub.dev
- **Mitigation:** Use known packages (camera, http, provider all official Flutter packages)

## Current Status
- [x] Content-Type validation (T1 partial)
- [x] Localhost binding (T2)
- [ ] File size limit (T1)
- [ ] Rate limiting (T1)
- [ ] EXIF stripping (T3)

## Recommendations
- Sprint 2: Add file size limit + EXIF stripping to vision_service.py
- Sprint 3: Add API key authentication if backend goes beyond localhost
- Sprint 4: Review for network exposure (flutter_map makes external requests)