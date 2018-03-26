# Open edX quick install (in Docker containers)

This is a **one-click production install of [Open edX](https://openedx.org)**.

The deployment of a full-featured Open edX platform is a highly technical and complex project... but we can remove most of the complexity by relying on pre-configured Docker containers and by using only a subset of all possible features. We made this so that non-technical people could still install Open edX by themselves: knowing how to launch a server and ssh into it should be enough. But we also made sure that every step of the deploy process could be customized if you have the technical skills.

## Quickstart

All you have to do is [download the content of this repository](https://codeload.github.com/regisb/openedx-docker/zip/master), decompress and run:

    make all

There is no step #2. You will be asked some questions about the configuration of your Open edX platform. The build step will take some time, but then you will have both an LMS and a CMS running behind a web server on port 80. You should be able to access your platform at the address you gave during the configuration phase.

To be honest, I really don't like 1-click installs :-p They tend to hide much of the important details. So I strongly recommend you read the more detailed instructions below to understand what is going on exactly and to troubleshoot potential issues.

## Requirements

The only prerequisite for running this is Python and a working docker install. You will need both docker and docker-compose. Follow the instructions from the official documentation:

- [Python](https://www.python.org/downloads/): all versions >= 2.7 are supported.
- [Docker install](https://docs.docker.com/engine/installation/)
- [Docker compose install](https://docs.docker.com/compose/install/)

Note that the web server container will bind to port 80, so if you already have a web server running (Apache or Nginx, for instance), you should stop it.

You should be able to run Open edX on any platform that supports Docker and Python, including Mac OS and Windows. For now, only Ubuntu 16.04 was tested but we have no reason to believe the install would not work on a different OS.

At a minimum, the server running the containers should have 4 Gb of RAM.

## Step-by-step install

### Configure

    make configure

This is the only non-automatic step in the install process. You will be asked various questions about your Open edX platform and appropriate configuration files will be generated. If you would like to automate this step then you should run `make configure` interactively once. After that, you will have a `config.json` file at the root of the repository. Just upload it to wherever you want to run Open edX and then run `./configure --silent` instead of `make configure`. All values from `config.json` will be automatically loaded.

### Build

    make build # go get a coffee

Building the images may require a long time, depending on your bandwidth, as you will have to checkout the `edx-platform` repository (> 1 Gb) as well as the python dependencies. Once the images have been built, this step can be repeated very quickly.

### Migrations and assets

    make migrate
    make assets

These commands should be run just once. They will create the database tables and generate static assets, such as images, stylesheets and Javascript dependencies.

### Running Open edX

    make up

This will launch the various docker containers required for your Open edX platform. The LMS and the Studio will then be reachable at the domain name you specified during the configuration step.

## Additional commands

### Creating a new user with staff and admin rights

You will most certainly need to create a user to administer the platform. Just run:

    USERNAME=yourusername EMAIL=user@email.com make create-staff-user

You will asked to set the user password interactively.

### Importing the demo course

On a fresh install, your platform will not have a single course. To import the [Open edX demo course](https://github.com/edx/edx-demo-course ), run:

    make import-demo-course

### Daemonizing

Note that in production, you will probably want to daemonize the services. Instead of `make up`, run:

    make daemon

And then, to stop all services:

    make stop

### Logging

To view the logs from all containers:

    docker-compose logs -f

To view the logs from just one container, for instance the web server:

    docker-compose logs -f

### Development

Open a bash in the lms:

    docker-compose run lms bash

Open a python shell in the lms or the cms:

    make lms-shell
    make cms-shell

## Disclaimers & Warnings

This project is the follow-up of my work on an [install from scratch of Open edX](https://github.com/regisb/openedx-install). It does not rely on any hack or complex deployment script. In particular, we do not use the Open edX [Ansible deployment playbooks](https://github.com/edx/configuration/). That means that the folks at edX.org are *not* responsible for troubleshooting issues of this project. Please don't bother Ned ;-)

## Troubleshooting

### "Running migrations... Killed!"

The LMS and CMS containers require at least 4 GB RAM, in particular to run the Open edX SQL migrations. On Docker for Mac, by default, containers are allocated at most 2 GB of RAM. On Mac OS, if the `make all` command dies after displaying "Running migrations", you most probably need to increase the allocated RAM. [Follow these instructions from the official Docker documentation](https://docs.docker.com/docker-for-mac/#advanced). 

## Missing features

### Forums

Forums are not installed in this proposed install of Open edX. They require a specific ruby install and settings. Unfortunately, there is no section dedicated specifically to the forums in the [Open edX documentation](http://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/open-release-ginkgo.master/).

### SSL certificates

We have decided not to include the installation of SSL certificates in this project for running an Open edX platform on HTTPS. This is because there are too many different ways to generate SSL certificates. In particular, we should not assume that everyone uses [Let's Encrypt](http://letsencrypt.org/) certificates. If you decide to run your Open edX platform behind HTTPS, you will have to modify:

* the generated nginx configuration files 
* the `lms.env.json` and `cms.env.json` files: look for the `LMS_ROOT_URL` and `CMS_ROOT_URL` variables and replace "http" by "https".

## Contributing

If you have a problem, feel free to open a [Github issue](https://github.com/regisb/openedx-docker/issues) that describes:
- the problem you are facing: this includes the exact error message, or a screenshot of the error.
- what action triggered the error: which command line instruction, which url you tried to access, etc.
- any error logs that you may find: you may want to take a look at the files in `data/lms/logs`, for instance.

Pull requests will be happily examined, too! However, we should be careful to keep the project lean and simple: both to use and to modify. Optional features should not make the user experience more complex. Instead, documentation on how to add the feature is preferred.
