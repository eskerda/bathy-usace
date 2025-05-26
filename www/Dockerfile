FROM node:latest AS vite_build

WORKDIR /app

COPY package.json .

RUN npm install

COPY index.html .
COPY src ./src
COPY vite.config.mjs .

RUN npm run build

FROM nginx
COPY --from=vite_build /app/dist /usr/share/nginx/html
