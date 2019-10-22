FROM {{ DOCKER_REGISTRY }}{{ DOCKER_IMAGE_OPENEDX }}
MAINTAINER Overhang.io <contact@overhang.io>

# Install useful system requirements
RUN apt update && \
    apt install -y vim telnet \
    && rm -rf /var/lib/apt/lists/*

# Install dev python requirements
RUN pip install -r requirements/edx/development.txt
RUN pip install ipdb==0.12.2 ipython==5.8.0

# Configure new user
ARG USERID=1000
RUN useradd --home-dir /openedx --uid $USERID openedx
RUN chown -R openedx:openedx /openedx

# Copy new entrypoint (to take care of permission issues at runtime)
COPY ./bin /openedx/bin
RUN chmod a+x /openedx/bin/*

# Default django settings
ENV SETTINGS tutor.development

# TODO recompile static assets and point to edx-platform