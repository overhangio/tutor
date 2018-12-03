FROM ubuntu:18.04

RUN apt update && \
  apt install -y python3 python3-pip curl
RUN pip3 install jinja2

RUN mkdir /openedx /openedx/config /openedx/templates
COPY ./bin/configurator /usr/local/bin
COPY ./bin/docker-entrypoint.sh /usr/local/bin
WORKDIR /openedx/

ENTRYPOINT ["docker-entrypoint.sh"]
CMD configurator -c /openedx/config/config.json interactive && \
    configurator -c /openedx/config/config.json substitute /openedx/templates/ /openedx/output/
