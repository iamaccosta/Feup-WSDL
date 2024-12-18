## base
FROM python:3.12-alpine AS base

RUN addgroup runner
RUN adduser -G runner -D runner

USER runner
WORKDIR /home/runner/backend

## venv
FROM base AS venv

# Create virtual environment
RUN python -m venv .venv

COPY ./backend/bin/with_venv.sh ./bin/
COPY ./backend/requirements.txt ./

RUN --mount=type=cache,target=/home/runner/.cache/pip \
    ./bin/with_venv.sh pip install -r requirements.txt

## project
FROM base AS project

COPY ./backend/bin/ ./bin/
COPY ./backend/app ./app

COPY ./backend/requirements.txt ./
COPY --from=venv /home/runner/backend/.venv/ ./.venv/


## runner-dev
FROM project AS runner-dev

EXPOSE 5000
VOLUME /data

CMD [ "./bin/with_venv.sh", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--debug" ]

## runner-prod
FROM project AS runner-prod

EXPOSE 5000
VOLUME /data

CMD [ "./bin/with_venv.sh", "flask", "--app", "app", "run", "--host", "0.0.0.0" ]

