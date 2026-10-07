# GEMS V1.2.0 — Master Data Foundation

This release adds canonical shared master-data services without modifying approved module forms.

Canonical domains seeded: company, farms, depots, projects, poultry sub-projects, and the seven official departments.

API: GET /api/master-data, GET /api/master-data?kind=farm, POST /api/master-data.

Principle: one canonical identifier is reused across modules so later form adapters can implement Enter Once → Use Everywhere without duplicate masters.
