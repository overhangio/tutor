# [WIP] Docker-compose Open edX production stack

This is a work-in-progress.

The production stack is sufficient for a minimal production deployment of Open edX.

## Lauch a production stack

Prepare build:

    make directories

Build and run:

    docker-compose build # go get a coffee
    docker-compose up

The LMS will be reachable at [http://openedxdemo.overhang.io](http://openedxdemo.overhang.io).

The CMS will be reachable at [http://studio.openedxdemo.overhang.io](http://studio.openedxdemo.overhang.io).

For local development, you should point to http://localhost:8800.

On the first run you will need to migrate the database and collect static assets:

    make migrate
    make assets

To import the Open edX demo course, run:

    make import-demo-course

To daemonize:

    docker-compose up -d

## Development

Open a bash in the lms:

    docker-compose run lms bash

Open a python shell in the lms or the cms:

    make lms-shell
    make cms-shell

## TODO

- Make sure that secret keys are not shared with the entire world
- Don't duplicate args between containers
- Add arguments to set domain name, platform name, etc.
- Add documentation on host Nginx
- Better readme
