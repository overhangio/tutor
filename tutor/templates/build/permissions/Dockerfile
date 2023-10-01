ARG DOCKER_REGISTRY=docker.io
FROM ${DOCKER_REGISTRY}/alpine:3.13.6
LABEL maintainer="Overhang.io <contact@overhang.io>"

COPY ./setowner.sh /usr/local/bin/setowner
RUN chmod a+x /usr/local/bin/setowner

ENTRYPOINT ["setowner"]
