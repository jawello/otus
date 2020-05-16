FROM python:3.7-alpine as builder
COPY otus-app/requirements.txt .
RUN apk update \
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  && pip install --no-cache-dir alembic psycopg2-binary \
  && apk del build-deps gcc
RUN pip install --upgrade pip
RUN pip install --user -r requirements.txt

FROM python:3.7-alpine
COPY --from=builder /root/.local /root/.local
COPY otus-app/main.py /app/main.py
COPY otus-app/models /app/models
WORKDIR /app
EXPOSE 8000
ENTRYPOINT ["python", "main.py"]

