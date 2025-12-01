# FrontendRelease

Release-ready front-end bundles live here, separated from active development in `FrontendDeveloper/`.

## Run the static UI
1) From repo root:
```bash
cd FrontendRelease
python -m http.server 8501
```
2) Open http://127.0.0.1:8501

### Switch between release vs developer UI
- Default is static release UI.
- To launch developer (Streamlit) UI: `./scripts/StartAll.sh -d` or `FRONTEND_MODE=developer ./scripts/StartAll.sh`
- To force release explicitly:
```bash
./scripts/StartAll.sh -r
```

## Config
- API endpoints are centralized in `config.js` (`apiBaseUrl`, `endpoints`).
- Mock fallback is on by default when requests fail; set `mockResponses` to `true` in `config.js` for offline demos.

## Files
- `index.html` — layout & structure (no build step).
- `styles.css` — light SaaS/mental-health dashboard styling.
- `config.js` — API URLs and feature flags.
- `api.js` — fetch wrappers + mock fallback.
- `ui.js` — rendering helpers (messages, charts, toasts).
- `app.js` — entry point, state, bindings.
