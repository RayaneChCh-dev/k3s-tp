# ---- Build stage ----
FROM alpine:3.19 AS builder
WORKDIR /src
COPY index.html .

# ---- Runtime stage ----
FROM nginx:1.27-alpine
COPY --from=builder /src/index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1
