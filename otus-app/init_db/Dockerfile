FROM python:3.7-alpine
MAINTAINER jawello, jawello@gmail.com

RUN apk update \
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  && pip install --no-cache-dir alembic psycopg2-binary \
  && apk del build-deps gcc

COPY . /migration

WORKDIR /migration


VOLUME ["/migration/alembic.ini"]

ENTRYPOINT ["alembic", "upgrade", "head"]