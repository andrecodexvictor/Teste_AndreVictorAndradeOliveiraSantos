# =============================================================
# Dockerfile.frontend - Vue.js Dashboard
# =============================================================
# MULTI-STAGE BUILD: Node para build, Nginx para servir
# Imagem final ~25MB ao invés de ~1GB
#
# BUILD: docker build -f docker/frontend/Dockerfile -t frontend ./frontend
# =============================================================

# Stage 1: Build
FROM node:22-alpine as builder

WORKDIR /app

# Copia package files primeiro (cache de layers)
COPY frontend/package*.json ./

# Instala dependências
RUN npm ci --silent

# Copia código fonte
COPY frontend/ .

# Build para produção
RUN npm run build

# Stage 2: Nginx para servir arquivos estáticos
FROM nginx:alpine

# Copia build do Vue.js
COPY --from=builder /app/dist /usr/share/nginx/html

# Expõe porta
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
