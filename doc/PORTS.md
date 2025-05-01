# Port Usage in glyph-miner

This document summarizes the purpose and usage of ports in the glyph-miner project.

## Web Servers

### NGINX
- **Port 9090**  
  NGINX listens on port 9090 and acts as a reverse proxy.
  - Serves static frontend files from `/web`
  - Forwards `/api/` requests to uWSGI backend on port 9091

### Other services
- **Port 8080**  
  This port is reserved by the system for unrelated development purposes.  
  Avoid using 8080 in this project.

## uWSGI
- **Port 9091**  
  The uWSGI Python backend binds to port 9091 and processes `/api/` requests proxied by NGINX.

## Summary

| Port | Component | Purpose                         |
|------|-----------|---------------------------------|
| 9090 | NGINX     | Public-facing static + API proxy|
| 9091 | uWSGI     | Internal Python API backend     |
| 8080 | Reserved  | Do not use for glyph-miner      |
