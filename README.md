# [WIP] Docker-compose Open edX production stack

This is a work-in-progress.

The production stack is composed of Nginx, MySQL, MongoDB, Memcache and an LMS container.

## Install

Create necessary data folders:

    mkdir -p data/lms/course_static data/lms/data data/lms/logs data/lms/staticfiles data/lms/uploads
    mkdir -p data/mongodb data/mysql

## Lauch a production stack

    docker-compose up --build

The LMS will be reachable at the following url: [http://openedx.localhost](http://openedx.localhost).

## Development tips & tricks

Open a bash in the lms:

    docker-compose run lms bash

How to find the IP address of a running docker:

    docker container ls
    docker inspect a0fc4cc602f8

## TODO

- Add a CMS container
- Add rabbitmq and celery worker containers
- Make sure that secret keys are not shared with the entire world
- Fix TODOs
