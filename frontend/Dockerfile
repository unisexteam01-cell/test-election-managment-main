FROM node:20-slim

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --network-concurrency 1

COPY . /app

EXPOSE 19006

CMD ["yarn", "start", "--web"]
