FROM python:3.7-alpine as builder
COPY requirements.txt .
RUN pip install --upgrade pip
RUN apk update \
  && apk add --virtual build-deps autoconf automake g++ gcc make python3-dev musl-dev \
  && apk add postgresql-dev
RUN pip install --user -r requirements.txt
RUN pip install --prefix=/install -r /requirements.txt

FROM python:3.7-alpine as builder_multidict
COPY requirements.txt .
RUN pip install --upgrade pip
RUN apk update \
  && apk add --virtual build-deps autoconf automake g++ gcc make python3-dev musl-dev
RUN pip wheel --wheel-dir=/root/wheels multidict

FROM python:3.7-alpine
COPY --from=builder /root/.local /root/.local
COPY --from=builder_multidict /root/wheels /root/wheels
RUN pip install \
      --no-index \
      --find-links=/root/wheels \
      multidict
COPY . /app
RUN apk --no-cache add libpq
WORKDIR /app
VOLUME ["/app/config"]
ENTRYPOINT ["python", "main.py", "-c", "/app/config/otus.yaml", "-cm", "/app/config/alembic.ini"]

