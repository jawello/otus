FROM python:3.7-alpine
MAINTAINER jawello, jawello@gmail.com

RUN apk update \
  && apk add --virtual build-deps autoconf automake g++ make build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev

COPY data_generator/requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir /app
RUN mkdir /app/config

COPY ./data_generator/data_generator.py /app
COPY ./models /app/models
COPY routes.py /app
COPY db.py /app
COPY config.py /app

WORKDIR /app
VOLUME ["/app/config"]

ENTRYPOINT ["python", "data_generator.py", "-c", "/app/config/data_generator.yaml"]

