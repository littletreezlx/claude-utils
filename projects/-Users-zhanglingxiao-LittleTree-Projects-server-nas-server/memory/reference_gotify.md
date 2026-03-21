---
name: gotify-notification-service
description: Self-hosted Gotify push notification service for NAS server alerts — URL, app name, and integration points
type: reference
---

Gotify push notification center for NAS Server critical alerts.

- **Internal URL**: http://192.168.0.100:50042
- **Public URL**: https://gotify.flametreehome.top:60443
- **App name on Gotify**: nas server
- **Env vars**: `GOTIFY_URL`, `GOTIFY_TOKEN` (in .env)

**Integration points**:
- Python utility: `pythonapi/internal/utils/gotify_notifier.py`
- Node.js utility: `nodejs-service/src/utils/gotify-notifier.ts`
- Hooked into: lifespan startup, error middleware, scheduler engine, auth notifier, Node.js index
