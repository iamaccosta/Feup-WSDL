## base
FROM python:3.12-alpine AS venv

USER nobody
WORKDIR /app

# Create virtual environment
RUN python -m venv .venv

COPY ./bin/with_venv.sh ./bin/
COPY ./requirements.txt ./

RUN ./bin/with_venv.sh pip install --no-cache-dir -r requirements.txt

## project
FROM python:3.12-alpine AS project

USER nobody
WORKDIR /app

COPY ./bin/ ./bin/
COPY ./app/ ./app/

COPY --from=venv /app/requirements.txt ./
COPY --from=venv /app/.venv/ ./.venv/

## runner-dev
FROM venv AS runner-dev

USER nobody
WORKDIR /app
EXPOSE 5000

VOLUME [ \
    "/data" \
    "/app/app", \
    "/app/.env" \
]

CMD [ "./bin/with_venv.sh", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--debug" ]

## runner-prod
FROM project AS runner-prod

USER nobody
WORKDIR /app
EXPOSE 5000

VOLUME [ "/data" ]

CMD [ "./bin/with_venv.sh", "flask", "--app", "app", "run", "--host", "0.0.0.0" ]

