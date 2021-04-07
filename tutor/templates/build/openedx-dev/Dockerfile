FROM {{ DOCKER_IMAGE_OPENEDX }} as base
MAINTAINER Overhang.io <contact@overhang.io>

# Install useful system requirements
RUN apt update && \
    apt install -y vim iputils-ping dnsutils telnet \
    && rm -rf /var/lib/apt/lists/*

# Install dev python requirements
RUN pip install -r requirements/edx/development.txt
# We install ipython from source to avoid too many deprecation warnings
# https://github.com/ipython/ipython/issues/12206
# We might be able to avoid this once they make a release later than 7.19.0.
RUN pip install ipdb==0.13.4 git+https://github.com/ipython/ipython.git@d0649a54a8936a8019d54549779dc92bcbde4e68#egg=ipython

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

######## Test image
FROM base as test

# Run all tests by default
ENTRYPOINT ["docker-entrypoint-test.sh"]
CMD pytest

######## Development image
FROM base as dev

# Default django settings
ENV SETTINGS tutor.development
