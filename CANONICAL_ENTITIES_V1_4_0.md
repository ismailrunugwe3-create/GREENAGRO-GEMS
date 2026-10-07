# GEMS V1.4.0 — Canonical Entity Layer

Canonical kinds: employee, supplier, customer, item, site, project, subproject, flock_batch_cycle.

Rules:
- One entity = one stable UUID across all GEMS modules.
- `(kind, code)` is unique. Duplicate creation returns HTTP 409 and the existing canonical record must be reused.
- Entity updates use optimistic concurrency (`version`) to prevent silent overwrite.
- Cross-domain relationships use `entity_links`, so batches/cycles, projects, sites and other masters reference canonical IDs instead of repeated free text.
- Audit events are written for canonical entity CREATE and UPDATE operations.
- Approved module form source files remain unchanged.

API:
- GET/POST `/api/entities`
- GET `/api/entities?kind=customer`
- PUT `/api/entities/{uuid}`
- GET/POST `/api/entity-links`
