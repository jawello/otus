# Otus
Домашние задания по курсу [Архитектор ПО](https://otus.ru/lessons/arhitektor-po/?int_source=courses_catalog&int_term=operations)

## Первое домашнее задание
**tag**: v0.0.1 

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

## Второе домашнее задание
**tag**: v0.0.2

Развернуть приложение в minikube

**Цель:** Написать манифесты для деплоя в k8s для сервиса из прошлого ДЗ. 
Манифесты должны описывать сущности Deployment, Service, Ingress. 
В Deployment обязательно должны быть указаны Liveness, Readiness пробы. 
Количество реплик должно быть не меньше 2. Image контейнера должен быть 
указан с Dockerhub. В Ingress-е должно быть правило, которое форвардит 
все запросы с /otusapp/* на сервис с rewrite-ом пути. Хост в ингрессе 
должен быть arch.homework. В итоге после применения манифестов GET 
запрос на http://arch.homework/otusapp/health должен отдавать
`{“status”: “OK”}`. На выходе предоставить ссылку на github c манифестами. 
Манифесты должны лежать в одной директории, так чтобы можно было их все 
применить одной командой kubectl apply -f .