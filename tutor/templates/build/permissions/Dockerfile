FROM docker.io/alpine:3.13.6
LABEL maintainer="Overhang.io <contact@overhang.io>"

COPY ./setowner.sh /usr/local/bin/setowner
RUN chmod a+x /usr/local/bin/setowner

ENTRYPOINT ["setowner"]
