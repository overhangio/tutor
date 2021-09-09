FROM {{ DOCKER_IMAGE_OPENEDX }} as base
MAINTAINER Overhang.io <contact@overhang.io>

# Install useful system requirements
RUN apt update && \
    apt install -y vim iputils-ping dnsutils telnet \
    && rm -rf /var/lib/apt/lists/*

# Install dev python requirements
RUN pip install -r requirements/edx/development.txt
RUN pip install ipdb==0.13.4 ipython==7.27.0

{{ patch("openedx-dev-dockerfile-post-python-requirements") }}

# Recompile static assets: in development mode all static assets are stored in edx-platform,
# and the location of these files is stored in webpack-stats.json. If we don't recompile
# static assets, then production assets will be served instead.
RUN rm -r /openedx/staticfiles && \
    mkdir /openedx/staticfiles && \
    openedx-assets webpack --env=dev

# Copy new entrypoint (to take care of permission issues at runtime)
COPY ./bin /openedx/bin
RUN chmod a+x /openedx/bin/*

# Configure new user
ARG USERID=1000
RUN create-user.sh $USERID

######## Development image
FROM base as dev

# Default django settings
ENV SETTINGS tutor.development
