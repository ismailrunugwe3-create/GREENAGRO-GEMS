GREENAGRO ENTERPRISE MANAGEMENT SYSTEM (GEMS)
NEW ACTIVE APP V1.1.0 — CENTRAL DATA FOUNDATION

Windows: double-click START_GEMS.bat then open http://127.0.0.1:8765
Other OS: run python server.py and open the same address.

This build preserves all source forms unchanged and adds a persistent transactional API/database foundation, audit trail and concurrency protection.
IMPORTANT: V1.1.0 is still a development build. Its SQLite database travels with the ZIP/folder for single-host testing. True multi-device simultaneous use requires deploying the server/API to a shared company host; production will use a server-hosted database rather than device-local authoritative storage.
