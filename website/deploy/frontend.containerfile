## deps
FROM node:22-alpine AS deps

WORKDIR /usr/src

COPY \
    ./frontend/package.json \
    ./frontend/package-lock.json \
    ./

RUN --mount=type=cache,target=/root/.npm npm ci

## project
FROM node:22-alpine AS project

WORKDIR /usr/src

COPY \
    ./frontend/postcss.config.js \
    ./frontend/tailwind.config.ts \
    ./frontend/tsconfig.json \
    ./frontend/vite.config.ts \
    ./

COPY ./frontend/public/ ./public/
COPY ./frontend/app/ ./app/

COPY --from=deps /usr/src/package.json /usr/src/package-lock.json ./
COPY --from=deps /usr/src/node_modules ./node_modules

## runner-dev
FROM project AS runner-dev

WORKDIR /usr/src
EXPOSE 3000

CMD [ "npm", "run", "dev", "--", "--host", "--port", "3000" ]

## builder-prod
FROM project AS builder-prod

WORKDIR /usr/src

RUN npm run build

## runner-prod
FROM deps AS runner-prod

WORKDIR /usr/src
EXPOSE 3000

COPY --from=builder-prod /usr/src/build ./build

CMD [ "npm", "start" ]
