FROM node:11-slim
RUN mkdir /app
WORKDIR /app
COPY frontend/package.json frontend/yarn.lock frontend/package-lock.json ./
RUN npm install
COPY ./frontend /app
CMD ["npm", "start"]
