# Otus
Домашние задания по курсу [Архитектор ПО](https://otus.ru/lessons/arhitektor-po/?int_source=courses_catalog&int_term=operations)

## Первое домашнее задание
tag: v0.0.1 

Обернуть приложение в docker-образ и запушить его на Dockerhub
Создать минимальный сервис, который
1) отвечает на порту 8000
2) имеет http-метод
GET /health/
RESPONSE: {"status": "OK"}

Cобрать локально образ приложения в докер.
Запушить образ в dockerhub

На выходе необходимо предоставить
1) имя репозитория и тэг на Dockerhub
[jawello/otus:0.0.1](https://hub.docker.com/repository/docker/jawello/otus)
2) ссылку на github c Dockerfile, либо приложить Dockerfile в ДЗ

