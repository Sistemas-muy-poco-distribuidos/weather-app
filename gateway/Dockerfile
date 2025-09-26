FROM node:20-alpine

WORKDIR /app
COPY protos /app/protos
COPY gateway/package.json /app/package.json
RUN npm install --omit=dev
COPY gateway/server.mjs /app/server.mjs

EXPOSE 8080
CMD ["node", "server.mjs"]