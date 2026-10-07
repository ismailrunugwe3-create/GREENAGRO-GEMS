# GEMS V1.1.0 Central Data Foundation
- Source forms remain unchanged.
- SQLite is the development persistent transactional database; WAL enables concurrent readers/writers.
- API: GET /api/health, GET/POST /api/records, PUT /api/records/{id}, GET /api/audit.
- Every record carries UUID, module/form source, version, timestamps, actor, project/site scope.
- Optimistic concurrency returns HTTP 409 when a stale user attempts to overwrite a newer version.
- Audit snapshots are append-only for CREATE/UPDATE events.
- Production deployment target: server-hosted PostgreSQL-compatible central database/API. Device-local DB is not authoritative in production.
- Enter Once / Use Everywhere will bind forms to canonical master entities and transactions in subsequent builds.
