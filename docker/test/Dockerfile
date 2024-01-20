FROM python:3.12-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /src
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

ARG POETRY_HOME=/opt/poetry
ARG POETRY_VERSION=1.7.1

RUN groupadd -g 10001 test && \
  useradd -u 10000 -g test test

RUN apt-get -y update && apt-get -y install curl gcc g++

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:${POETRY_HOME}/bin"

WORKDIR /src
COPY poetry.lock pyproject.toml /src/

RUN poetry install --no-interaction --no-ansi --no-root --without web

COPY --chown=test:test judger judger
COPY --chown=test:test docker/test/entrypoint.sh entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]