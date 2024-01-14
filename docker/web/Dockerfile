FROM python:3.12-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /src

ARG POETRY_HOME=/opt/poetry
ARG POETRY_VERSION=1.7.1

RUN apt-get -y update && apt-get -y install curl

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:${POETRY_HOME}/bin"

WORKDIR /src
COPY poetry.lock pyproject.toml /src/

RUN poetry install --no-interaction --no-ansi --no-root --without test

COPY . .

CMD [ "poetry", "run", "python3", "web/main.py" ]