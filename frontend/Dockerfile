# ---- Build stage ----
FROM node:20-slim AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Base URL the BROWSER uses to reach the API. Baked in at build time because
# it is a NEXT_PUBLIC_ var. Default "/api" => same-origin via the Caddy proxy.
ARG NEXT_PUBLIC_API_BASE=/api
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE

RUN npm run build

# ---- Runtime stage ----
FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000

# Standalone output bundles only what's needed to run.
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
