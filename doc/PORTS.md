## 📘 `PORTS.md` – Port Usage in Glyph Miner Deployment

This file documents the usage of ports in the local and container-based deployments of Glyph Miner to prevent conflicts and clarify configuration.

---

### 🔌 Port Assignments

| Port | Purpose | Used By | Notes |
|------|---------|---------|-------|
| **9090** | Public HTTP port | **nginx** | Accessible via `http://localhost:9090/`. Serves static files directly and proxies dynamic requests to uwsgi (see below). |
| **9091** | Internal UWSGI socket | **uwsgi** | Nginx connects to this via `uwsgi_pass 127.0.0.1:9091;`. Never exposed to the outside. |

---

### 📍 How they connect

```plaintext
Browser --> http://localhost:9090 --> nginx
                                       └──> uwsgi (127.0.0.1:9091) --> Python server (server.py)
	
