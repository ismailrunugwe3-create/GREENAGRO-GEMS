GREENAGRO MODULE 07 — ORGANIZATION, DUTIES & ACCESS CONTROL — CUMULATIVE V1

Five controlled forms + one read-only governance engine.

Access architecture:
Organogram -> Department -> Position -> Duty Template -> Employee Assignment -> Project/Site -> Allowed Form -> Allowed Section/Action -> Approval Level.

Module 06 owns employee/employment facts.
Module 07 owns duties and access authorization.
Operational modules own their transactions.

Final GEMS must enforce permissions server-side, not only hide UI. It must use authenticated identities, default-deny logic, immutable audit logs, controlled access changes, row-level project/site scope, DENY precedence, SoD checks, approval thresholds and automatic access revocation on offboarding.
