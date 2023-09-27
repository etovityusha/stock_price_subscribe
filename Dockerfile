FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.6.1
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install --no-install-recommends -y curl && \
    curl -sSL https://install.python-poetry.org | python - && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-interaction --no-ansi

COPY . /app