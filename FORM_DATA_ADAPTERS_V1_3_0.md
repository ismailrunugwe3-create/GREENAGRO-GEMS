# GEMS V1.3.0 — Central Form Data Adapters

- Approved form source files remain unchanged.
- 74 data-writing forms were automatically mapped to their existing storage namespaces.
- Before a form opens, its authoritative dataset is pulled from the central GEMS database into a compatibility cache.
- Existing form Save logic is intercepted at the App shell boundary and synchronized to `/api/storage`.
- Server-side version numbers reject stale concurrent writes with HTTP 409.
- Every central synchronization creates an audit event.
- Browser localStorage is compatibility/cache only; it is not the authoritative company database.

Next production step: replace development profiles with employee/position/duty assignments and field-level canonical entity adapters (employees, suppliers, customers, items, flocks/batches, sites).
