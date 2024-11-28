## base
FROM python:3.12-alpine AS base

WORKDIR /usr/src
RUN chown nobody:nobody /usr/src

## venv
FROM base AS venv

RUN mkdir -p /usr/cache/pip
RUN chown nobody:nobody /usr/cache/pip

USER nobody
WORKDIR /usr/src

# Create virtual environment
RUN python -m venv .venv

COPY ./backend/bin/with_venv.sh ./bin/
COPY ./backend/requirements.txt ./

RUN --mount=type=cache,target=/usr/cache/pip \
    ./bin/with_venv.sh pip install --cache-dir /usr/cache/pip -r requirements.txt

## project
FROM base AS project

USER nobody
WORKDIR /usr/src

COPY ./backend/bin/ ./bin/
COPY ./backend/app ./app

COPY --from=venv /usr/src/requirements.txt ./
COPY --from=venv /usr/src/.venv/ ./.venv/

## runner-dev
FROM project AS runner-dev

USER nobody
WORKDIR /usr/src
EXPOSE 5000

VOLUME /data

CMD [ "./bin/with_venv.sh", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--debug" ]

## runner-prod
FROM project AS runner-prod

USER nobody
WORKDIR /usr/src
EXPOSE 5000

VOLUME /data

CMD [ "./bin/with_venv.sh", "flask", "--app", "app", "run", "--host", "0.0.0.0" ]

