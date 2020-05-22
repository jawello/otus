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

## Третье домашнее задание
**tag**: v0.0.3

Добавить к развернутому приложению БД.
Сделать простейший RESTful CRUD по созданию, удалению, просмотру и 
обновлению пользователей.
Пример API - https://app.swaggerhub.com/apis/otus55/users/1.0.0

Добавить базу данных с persistent volume для приложения.
Docker-Image базы данных должен использоваться из официального 
докер-репозитория.
Под с БД должен запускаться StatefulSet-ом с количеством реплик - 1.
Конфигурация приложения должна хранится в Configmaps.
Доступы к БД должны храниться в Secrets.
Первоначальные миграции должны быть оформлены в качестве Pod-ы 
(или Job-ы).
Ingress-ы должны также вести на url arch.homework/otusapp/* 
(как и в прошлом занятии)

На выходе должны быть предоставлена
1) ссылка на директорию в github, где находится директория с манифестами
кубернетеса
2) команда kubectl apply -f, которая запускает в правильном порядке
манифесты кубернетеса.
3) Postman коллекция, в которой будут представлены примеры запросов к
сервису на создание, получение, изменение и удаление пользователя. 
Запросы из коллекции должны работать сразу после применения манифестов, 
без каких-то дополнительных подготовительных действий.

~~**tag**: v0.0.4~~ *WIP*

Задание со звездочкой (необязательное, но дает дополнительные баллы):
+3 балла за шаблонизацию приложения в helm 3 чартах
+2 балла за использование официального helm чарта для БД и подключение
его в чарт приложения в качестве зависимости.