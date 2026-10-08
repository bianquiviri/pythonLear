FROM node:22-alpine AS build

WORKDIR /app
ENV NUXT_TELEMETRY_DISABLED=1

COPY package.json ./
RUN npm install --ignore-scripts

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/.output/public /usr/share/nginx/html

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD wget -q -O /dev/null http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
