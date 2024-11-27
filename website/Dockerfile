## base
FROM python:3.12-alpine AS venv

USER nobody

WORKDIR /app

# Create virtual environment
RUN python -m venv .venv

COPY bin/with_venv.sh ./bin/with_venv.sh
COPY requirements.txt ./requirements.txt

RUN ./bin/with_venv.sh pip install --no-cache-dir -r requirements.txt

## app
FROM python:3.12-alpine AS app

USER nobody

WORKDIR /app

COPY . .
COPY --from=venv /app/.venv .venv

ARG APP_PORT=5000
EXPOSE ${APP_PORT}
ENV APP_PORT=${APP_PORT}

WORKDIR /app

CMD [ "./bin/with_venv.sh", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "${APP_PORT}", "--debug" ]

