## deps
FROM node:22-alpineASdeps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

## project
FROM node:22-alpineASproject

WORKDIR /app

COPY ./postcss.config.js \
     ./tailwind.config.ts \
     ./tsconfig.json \
     ./vite.config.ts ./

COPY ./public/ ./public/
COPY ./app/ ./app/

COPY --from=deps ./package.json ./package-lock.json ./
COPY --from=deps /app/node_modules ./node_modules

## runner-dev
FROM depsASrunner-dev

WORKDIR /app
EXPOSE 3000

VOLUME [ \
    "/app/app", \
    "/app/public", \
    "/app/.env" \
    "/app/postcss.config.js", \
    "/app/tailwind.config.ts", \
    "/app/tsconfig.json", \
    "/app/vite.config.ts" \
]

CMD [ "npm", "run", "dev", "--", "--host", "--port", "3000" ]

## builder-prod
FROM projectASbuilder-prod

WORKDIR /app

RUN npm run build

## runner-prod
FROM depsASrunner-prod

WORKDIR /app
EXPOSE 3000

COPY --from=builder-prod /app/build ./build

CMD [ "npm", "start" ]
