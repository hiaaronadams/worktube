# Deploying Worktube to a VPS (Hostinger KVM, or any Ubuntu/Debian box)

The whole stack runs in Docker: **Postgres + FastAPI + Next.js**, behind a
**Caddy** reverse proxy that terminates TLS and serves everything on one origin
(`/` = dashboard, `/api/*` = API). One command brings it all up.

## 0. Prerequisites

- A Hostinger VPS (KVM 1 is plenty) running Ubuntu 22.04/24.04, with SSH access.
- (Optional but recommended) a domain or subdomain you can point at the VPS, for
  automatic HTTPS. Without one you can still run over plain HTTP via the IP.

## 1. Point a domain at the VPS (optional, enables HTTPS)

In your DNS provider, add an **A record** for e.g. `rfp.yourstudio.com` →
your VPS's IPv4 address. Skip this if you'll use the bare IP for now.

## 2. Install Docker on the VPS

```bash
ssh root@YOUR_VPS_IP
curl -fsSL https://get.docker.com | sh
docker compose version   # confirm the compose plugin is present
```

(Hostinger also offers a one-click "Ubuntu with Docker" VPS template, which
skips this step.)

## 3. Get the code

```bash
git clone https://github.com/hiaaronadams/worktube.git
cd worktube
git checkout claude/jolly-goodall-20k6t5
```

## 4. Configure secrets

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

Set:
- `DOMAIN` — `rfp.yourstudio.com` for HTTPS, or leave `:80` to serve over HTTP by IP.
- `POSTGRES_PASSWORD` — a long random string.
- `SAM_API_KEY` — your SAM.gov key (optional; needed for live US federal data).

## 5. Open the firewall

```bash
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable
```

## 6. Launch

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

First run builds both app images and pulls Postgres/Caddy (a few minutes).
Check status and logs:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

The backend auto-creates tables and seeds the default sources on startup
(idempotent). Visit:

- `https://rfp.yourstudio.com` (or `http://YOUR_VPS_IP`)

Caddy obtains a Let's Encrypt certificate automatically the first time a real
`DOMAIN` resolves to the server.

## 7. Pull in real opportunities

```bash
# Needs SAM_API_KEY set. SAM.gov first:
docker compose -f docker-compose.prod.yml exec backend python -m app.scripts.ingest --source sam
# Everything:
docker compose -f docker-compose.prod.yml exec backend python -m app.scripts.ingest --all
```

Automate it with a cron entry on the VPS (every 12h, per the spec):

```bash
0 */12 * * * cd /root/worktube && docker compose -f docker-compose.prod.yml exec -T backend python -m app.scripts.ingest --all >> /var/log/worktube-ingest.log 2>&1
```

## 8. Updating after new commits

```bash
cd worktube
git pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

## 9. Backups

The database lives in the `pgdata` Docker volume. Quick dump:

```bash
docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U worktube worktube > worktube-$(date +%F).sql
```

---

## ⚠️ Important: there is no login yet

The dashboard and API are currently **unauthenticated**. The moment this is on a
public domain/IP, anyone who finds the URL can read and edit your pipeline.
Before sharing it, add one of:

- **Caddy Basic Auth** (quickest — a username/password gate in the `Caddyfile`), or
- proper app-level auth.

Ask and I'll wire up Basic Auth (or a real login) — it's a small change to the
`Caddyfile` plus a note in the API client.
