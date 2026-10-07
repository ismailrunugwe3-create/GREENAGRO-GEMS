# GEMS V1.4.5 — Mobile + Desktop HTTPS Foundation

## Architecture
- One responsive GEMS frontend for mobile and desktop.
- 89 approved forms remain direct static routes; no srcdoc/blob/document.write renderer.
- Cloudflare Worker handles `/api/*`.
- Cloudflare D1 is the centralized persistent database foundation.
- Static forms and shell are served as Worker assets over HTTPS.
- Optimistic version checking is retained for shared form storage to prevent silent overwrites.
- Audit events are written centrally.

## Deployment sequence
1. Create a Cloudflare D1 database named `greenagro-gems`.
2. Put its database ID into `wrangler.jsonc`.
3. Apply `schema.sql` to D1.
4. Deploy the Worker/assets with Wrangler.
5. Open the resulting HTTPS URL on Android and desktop.
6. UAT all 89 forms and central save/sync before V1.5.0.

No PC localhost is required for normal production use after deployment.
