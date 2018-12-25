# Open edX 1-click install for everyone
![Build status](https://img.shields.io/travis/regisb/openedx-docker.svg)
![GitHub issues](https://img.shields.io/github/issues/regisb/openedx-docker.svg)
![GitHub closed issues](https://img.shields.io/github/issues-closed/regisb/openedx-docker.svg?colorB=brightgreen)

This is a one-click install of [Open edX](https://openedx.org), both for production and local development, inside docker containers. As a bonus, this also builds a mobile Android app for your platform.

[![asciicast](https://asciinema.org/a/6DowVk4iJf3AJ2m8xlXDWJKh3.png)](https://asciinema.org/a/6DowVk4iJf3AJ2m8xlXDWJKh3)

## Getting started

    git clone https://github.com/regisb/openedx-docker
    cd openedx-docker/
    make all

## That's it?

Yes :) When running `make all`, you will be asked some questions about the configuration of your Open edX platform. Then, all the components for a functional Open edX platform will be downloaded and assembled to and you will have both an LMS and a CMS running behind a web server on port 80, ready for production. You should be able to access your platform at the address you gave during the configuration phase.

All of this without touching your host environment! You don't even need root access.

To be honest, I really don't like 1-click installs :-p They tend to hide much of the important details. So I strongly recommend you read the more detailed instructions below to understand what is going on exactly and to troubleshoot potential issues. Also, instructions are given to setup a local development environment.

This might seem too simple to be true, but there's no magic -- just good packaging of already existing Open edX code. The code for building the Docker images is 100% available and fits in less than 1000 lines of code, in this repository.

## Optional features

Some optional features may be activated or deactivated during the interactive configuration step. These features change configuration files (during the `configure` step) as well as make targets.

### SSL/TLS certificates for HTTPS access

By activating this feature, a free SSL/TLS certificate from the [Let's Encrypt](https://letsencrypt.org/) certificate authority will be created for your platform. With this feature, **your platform will no longer be accessible in HTTP**. Calls to http urls will be redirected to https url.

The following DNS records must exist and point to your server:

    LMS_HOST (e.g: myopenedx.com)
    preview.LMS_HOST (e.g: preview.myopenedx.com)
    CMS_HOST (e.g: studio.myopenedx.com)

Thus, **this feature will (probably) not work in development** because the DNS records will (probably) not point to your development machine.

To download the certificate manually, run:

    make https-certificate

To renew the certificate, run this command once per month:

    make https-certificate-renew

### Student notes

With [notes](https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-hawthorn.master/exercises_tools/notes.html?highlight=notes), students can annotate portions of the courseware. 

![Notes in action](https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-hawthorn.master/_images/SFD_SN_bodyexample.png)

You should beware that the `notes.<LMS_HOST>` domain name should be activated and point to your server. For instance, if your LMS is hosted at [myopenedx.com](), the notes service should be found at [notes.myopenedx.com](). Student browsers will access this domain name to fetch their notes.

### Xqueue

[Xqueue](https://github.com/edx/xqueue) is for grading problems with external services. If you don't know what it is, you probably don't need it.

Note: in previous releases of openedx-docker, xqueue was run for all platforms. It is now an optional feature.

### Docker container web UI with [Portainer](https://portainer.io/)

Portainer is a web UI for managing docker containers. It lets you view your entire Open edX platform at a glace. Try it! It's really cool.

![Portainer demo](https://portainer.io/images/screenshots/portainer.gif)

After launching your platfom, the web UI will be available at [http://portainer.localhost](http://portainer.localhost) and http://portainer.YOUR_LMS_HOST. You will be asked to define a password for the admin user. Then, select a "Local environment" to work on and hit "Connect". You're done! Select the "local" group to view all running containers. Amon many other things, you'll be able to view the logs for each container, which is really useful.

### Android app (beta)

The Android app for your platform can be easily built in just one command:

    make android

If all goes well, the debuggable APK for your platform should then be available in ./data/android. To obtain a release APK, you will need to obtain credentials from the app store and add them to `config/android/gradle.properties`. Then run:

    make android-release

Building the Android app for an Open edX platform is currently labeled as a **beta feature** because it was not fully tested yet. In particular, there is no easy mechanism for overriding the edX assets in the mobile app. This is still a work-in-progress.

### Stats

By default, the install script will collect some information about your install and send it to a private server. The only transmitted information are the LMS domain name and the ID of the install. To disable stats collection, define the following environment variable:

    export DISABLE_STATS=1

If you decide to disable stats, please send me a message to tell me about your platform! 

## Requirements

The only prerequisite for running this is a working docker install. You will need both docker and docker-compose. Follow the instructions from the official documentation:

- [Docker](https://docs.docker.com/engine/installation/)
- [Docker compose](https://docs.docker.com/compose/install/)

Note that the production web server container will bind to port 80, so if you already have a web server running (Apache or Nginx, for instance), you should stop it.

You should be able to run Open edX on any platform that supports Docker and Python, including Mac OS and Windows. For now, only Ubuntu 16.04 was tested but we have no reason to believe the install would not work on a different OS.

At a minimum, the server running the containers should have 4 Gb of RAM; otherwise, the deployment procedure will crash during migrations (see the [troubleshooting](#troubleshooting) section).

Also, the host running the containers should be a 64 bit platform. (images are not built for i386 systems)

## Step-by-step install

### Configure

    make configure

This is the only non-automatic step in the install process. You will be asked various questions about your Open edX platform and appropriate configuration files will be generated. If you would like to automate this step then you should run `make configure` interactively once. After that, you will have a `config.json` file at the root of the repository. Just upload it to wherever you want to run Open edX and then run `make configure SILENT=1` instead of `make configure`. All values from `config.json` will be automatically loaded.

### Download

    make update

You will need to download the docker images from [Docker Hub](https://hub.docker.com/r/regis/openedx/). Depending on your bandwidth, this might take a long time. Minor image updates will be incremental, and thus much faster.

### Database creation, migrations and collection of static assets

    make databases
    make assets

These commands should be run just once. They will create the required databases tables, apply database migrations and make sure that static assets, such as images, stylesheets and Javascript dependencies, can be served by the nginx container.

If migrations are stopped with a `Killed` message, this certainly means the docker containers don't have enough RAM. See the [troubleshooting](#troubleshooting) section.

### Running Open edX

    make run

This will launch the various docker containers required for your Open edX platform. The LMS and the Studio will then be reachable at the domain name you specified during the configuration step. You can also access them at [http://localhost](http://localhost) and [http://studio.localhost](http://studio.localhost).

## Additional commands

All available commands can be listed by running:

    make help

### Creating a new user with staff and admin rights

You will most certainly need to create a user to administer the platform. Just run:

    make create-staff-user USERNAME=yourusername EMAIL=user@email.com

You will asked to set the user password interactively.

### Importing the demo course

On a fresh install, your platform will not have a single course. To import the [Open edX demo course](https://github.com/edx/edx-demo-course ), run:

    make import-demo-course

### Daemonizing

In production, you will probably want to daemonize the services. Instead of `make run`, run:

    make daemonize

And then, to stop all services:

    make stop

### Updating the course search index

The course search index can be updated with:

    make reindex-courses

Run this command periodically to ensure that course search results are always up-to-date.

### Logging

To view the logs from all containers use the [`docker-compose logs`](https://docs.docker.com/compose/reference/logs/) command:

    docker-compose logs -f

To view the logs from just one container, for instance the web server:

    docker-compose logs -f nginx

The last commands produce the logs since the creation of the containers, which can be a lot. Similar to a `tail -f`, you can run:

    docker-compose logs --tail=0 -f

### Debugging

Open a bash shell in the lms or the cms:

    make lms
    make cms

Open a python shell in the lms or the cms:

    make lms-python
    make cms-python

## For developers

In addition to running Open edX in production, you can use the docker containers for local development. This means you can hack on Open edX without setting up a Virtual Machine. Essentially, this replaces the devstack provided by edX.

(Note: containers are built on the Hawthorn release. If you are working on a different version of Open edX, you will have to rebuild the images with a different `EDX_PLATFORM_VERSION` argument. You may also want to change the `EDX_PLATFORM_REPOSITORY` argument to point to your own fork of edx-platform.)

### Standard devstack

Define development settings (on the host):

    export EDX_PLATFORM_SETTINGS=universal.development

Then open an LMS shell:

    make lms

You can then run a local web server, as usual:

    paver update_assets lms --settings=universal.development

Note that assets collection is made more difficult by the fact that development settings are [incorrectly loaded in hawthorn](https://github.com/edx/edx-platform/pull/18430/files). This should be fixed in the next release. Meanwhile, do not run `paver update_assets` while in development mode. Instead, run on the host:

    make assets-development

### Custom devstack

If you have one, you can point to a local version of [edx-platform](https://github.com/edx/edx-platform/) on your host machine:

    export EDX_PLATFORM_PATH=/path/to/your/edx-platform

Note that you should use an absolute path here, not a relative path (e.g: `/path/to/edx-platform` and not `../edx-platform`).

Point to your settings file:

    export EDX_PLATFORM_SETTINGS=mysettings.py

In this example, you should have a `mysettings.py` file in `edx-platform/lms/envs` and `edx-platform/cms/envs`. Development settings file for docker are a bit different from stock devstack settings. For valid development settings files, check [`config/openedx/universal/lms/development.py`](https://github.com/regisb/openedx-docker/blob/master/config/openedx/universal/lms/development.py) and [`config/openedx/universal/cms/development.py`](https://github.com/regisb/openedx-docker/blob/master/config/openedx/universal/cms/development.py)

You are ready to go! Run:

    make lms

Or:

    make cms

This will open a shell in the LMS (or CMS) container. You can then run just any command you are used to. For example, install node requirements, collect assets and run a local server:

    npm install
    paver update_assets lms --settings=mysettings
    ./manage.py lms runserver 0.0.0.0:8000

## Maintainers

The images are built, tagged and uploaded to Docker Hub in one command:

    make dockerhub

## Customising the `openedx` docker image

The LMS and the CMS all run from the `openedx` docker image. The base image is downloaded from [Docker Hub](https://hub.docker.com/r/regis/openedx/) when we run `make update` (or `make all`). But you can also customise and build the image yourself. The base image is built with:

    make build-openedx

The following sections describe how to modify various aspects of the docker image. After you have built your own image, you can run it as usual:

    make run

### Custom themes

Comprehensive theming is enabled by default. Put your themes in `openedx/themes`:

    openedx/themes/
        mycustomtheme1/
            cms/
                ...
            lms/
                ...
        mycustomtheme2/
            ...

Then you must rebuild the openedx Docker image:

    make build-openedx

Make sure the assets can be served by the web server:

    make assets

Finally, follow the [Open edX documentation to enable your themes](https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/configuration/changing_appearance/theming/enable_themes.html#apply-a-theme-to-a-site).

### Extra xblocks and requirements

Additional requirements can be added to the `openedx/requirements/private.txt` file. For instance:

    echo "git+https://github.com/open-craft/xblock-poll.git" >> openedx/requirements/private.txt

Then, the `openedx` docker image must be rebuilt:

    make build-openedx

To install xblocks from a private repository that requires authentication, you must first clone the repository inside the `openedx/requirements` folder on the host:

    git clone git@github.com:me/myprivaterepo.git ./openedx/requirements/myprivaterepo

Then, declare your extra requirements with the `-e` flag in `openedx/requirements/private.txt` :

    echo "-e ./myprivaterepo" >> openedx/requirements/private.txt

### Forked version of edx-platform

You may want to run your own flavor of edx-platform instead of the [official version](https://github.com/edx/edx-platform/). To do so, you will have to re-build the openedx image with the proper environment variables pointing to your repository and version:

    EDX_PLATFORM_REPOSITORY=https://mygitrepo/edx-platform.git EDX_PLATFORM_VERSION=my-tag-or-branch make build-openedx

You can then restart the services which will now be running your forked version of edx-platform:

    make restart-openedx

Note that your release must be a fork of Hawthorn in order to work. Otherwise, you may have important compatibility issues with other services.

### Running a different Docker image instead of [regis/openedx](https://hub.docker.com/r/regis/openedx/)

This is for people who have an account on [hub.docker.com](https://hub.docker.com) or a private image registry. You can build your image and push it to your repo. Then add the following content to the `.env` file:

    OPENEDX_DOCKER_IMAGE=myusername/myimage:mytag

Your own image will be used next time you run `make run`.

Note that the `make build` and `make push` command will no longer work as you expect and that you are responsible for building and pushing the image yourself.

## Help/Troubleshooting

### "Cannot start service nginx: driver failed programming external connectivity"

The containerized Nginx needs to listen to ports 80 and 443 on the host. If there is already a webserver, such as Apache or Nginx, running on the host, the nginx container will not be able to start. There are two solutions:

1. Stop Apache or Nginx on the host:

       sudo systemctl stop apache2
       sudo systemctl stop nginx

However, you might now want to do that if you need a webserver for running non-Open edX related applications. In such cases...

2. Run the nginx container on different ports: you can create a `.env` file in the `openedx-docker` directory in which you indicate different ports. For instance:

       cat .env
       NGINX_HTTP_PORT=81
       NGINX_HTTPS_PORT=444

In this example, the nginx container ports would be mapped to 81 and 444, instead of 80 and 443.

You should note that with the latter solution, it is your responsibility to configure the webserver on the host as a proxy to the nginx container. See [this](https://github.com/regisb/openedx-docker/issues/69#issuecomment-425916825) for http, and [this](https://github.com/regisb/openedx-docker/issues/90#issuecomment-437687294) for https.

### Help! The Docker containers are eating all my RAM/CPU/CHEESE

You can identify which containers are consuming most resources by running:

    docker stats

### "Running migrations... Killed!"

The LMS and CMS containers require at least 4 GB RAM, in particular to run the Open edX SQL migrations. On Docker for Mac, by default, containers are allocated at most 2 GB of RAM. On Mac OS, if the `make all` command dies after displaying "Running migrations", you most probably need to increase the allocated RAM. [Follow these instructions from the official Docker documentation](https://docs.docker.com/docker-for-mac/#advanced). 


### `Build failed running pavelib.servers.lms: Subprocess return code: 1`

    python manage.py lms --settings=development print_setting STATIC_ROOT 2>/dev/null
    ...
    Build failed running pavelib.servers.lms: Subprocess return code: 1`"

This might occur when you run a `paver` command. `/dev/null` eats the actual error, so you will have to run the command manually. Run `make lms` (or `make cms`) to open a bash session and then:

    python manage.py lms --settings=development print_setting STATIC_ROOT

Of course, you should replace `development` with your own settings. The error produced should help you better understand what is happening.

### `ValueError: Unable to configure handler 'local'`

    ValueError: Unable to configure handler 'local': [Errno 2] No such file or directory

This will occur if you try to run a development environment without patching the LOGGING configuration, as indicated in the [development](#for-developers) section above. Maybe you correctly patched the development settings, but they are not taken into account? For instance, you might have correctly defined the `EDX_PLATFORM_SETTINGS` environment variable, but `paver` uses the `devstack` settings (which does not patch the LOGGING variable). This is because calling `paver lms --settings=development` or `paver cms --settings=development` ignores the `--settings` argument. Yes, it might be considered an edx-platform bug... Instead, you should run the `update_assets` and `runserver` commands, as explained above.

### "`TypeError: get_logger_config() got an unexpected keyword argument 'debug'`"

This might occur when you try to run the latest version of `edx-platform`, and not a version close to `gingko.master`. It is no longer necessary to patch the `LOGGING` configuration in the latest `edx-platform` releases, as indicated in the [development](#for-developers) section above, so you should remove the call to `get_logger_config` altogether from your development settings.

### The chosen default language does not display properly

By default, Open edX comes with a [very limited set](https://github.com/edx/edx-platform/blob/master/conf/locale/config.yaml) of translation/localization files. To complement these languages, we add locales from the [openedx-i18n project](https://github.com/regisb/openedx-i18n/blob/master/edx-platform/locale/config-extra.yaml). But not all supported locales are downloaded. In some cases, the chosen default language will not display properly because if was not packaged in either edx-platform or openedx-i18n. If you feel like your language should be packaged, please [open an issue on the openedx-i18n project](https://github.com/regisb/openedx-i18n/issues).

## Disclaimers & Warnings

This project is the follow-up of my work on an [install from scratch of Open edX](https://github.com/regisb/openedx-install). It does not rely on any hack or complex deployment script. In particular, we do not use the Open edX [Ansible deployment playbooks](https://github.com/edx/configuration/). That means that the folks at edX.org are *not* responsible for troubleshooting issues of this project. Please don't bother Ned ;-)

Do you have a problem?

1. Carefully read the README, and in particular the [troubleshooting](#troubleshooting) section
2. Search for your problem among [open and closed Github issues](https://github.com/regisb/openedx-docker/issues?utf8=%E2%9C%93&q=is%3Aissue)
3. If necessary, open an [issue on Github](https://github.com/regisb/openedx-docker/issues/new).


## Known missing features: [discovery service](https://github.com/edx/course-discovery/), [ecommerce](https://github.com/edx/ecommerce), [analytics](https://github.com/edx/edx-analytics-pipeline)

Those extra services were considered low priority while developing this project. However, most of them should not be too hard to add to a standard install. If you need one or more of these services, feel free to let me know by opening an issue.

## Contributing

Pull requests will be happily examined! However, we should be careful to keep the project lean and simple: both to use and to modify. Optional features should not make the user experience more complex. Instead, documentation on how to add the feature is preferred.

## License

This work is licensed under the terms of the [MIT License](https://github.com/regisb/openedx-docker/blob/master/LICENSE.txt).
