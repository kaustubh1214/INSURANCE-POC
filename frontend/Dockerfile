# ============================================================
# InsureBridge Frontend — Dockerfile
# Multi-stage: builder (Vite build) + nginx runtime
# ============================================================

# ---------- Stage 1: Builder ----------
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (layer caching)
COPY package*.json ./
RUN npm ci --silent

# Copy source
COPY . .

# Build for production
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build


# ---------- Stage 2: nginx Runtime ----------
FROM nginx:alpine AS runtime

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx config: handle React Router (SPA fallback)
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://backend:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
