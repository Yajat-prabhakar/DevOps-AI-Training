# ---- Dependencies ----
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
RUN npm install

# ---- Development ----
FROM deps AS development
COPY . .
EXPOSE 5173
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:5173 || exit 1
CMD ["npm", "run", "dev"]

# ---- Build (used by production stage) ----
FROM deps AS build
COPY . .
RUN npm run build

# ---- Production ----
FROM nginx:1.27-alpine AS production
RUN apk add --no-cache curl
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/healthz || exit 1
CMD ["nginx", "-g", "daemon off;"]
