# Build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm ci || npm install

COPY . .

RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# SPA routing config
RUN echo 'server { \
  listen 80; \
  location / { \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    try_files $uri $uri/ /index.html; \
  } \
  location /api { \
    proxy_pass http://backend:8000; \
  } \
  location /health { \
    proxy_pass http://backend:8000; \
  } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
