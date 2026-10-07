# GEMS V1.4.3 — Direct Form Integration

- Approved forms audited: 89
- Source files retained as application pages.
- Mobile standalone renderer decodes the complete approved source at runtime and assigns it directly to the workspace document via `iframe.srcdoc`.
- No Blob URL renderer is used.
- Post-load verification checks rendered controls/tables/body content.
- Full server build continues to route directly to the original form files.
