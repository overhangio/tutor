FROM python:3.6-alpine

RUN apk add --no-cache curl
RUN pip install jinja2

RUN mkdir /openedx /openedx/config /openedx/templates
COPY ./bin/configurator /usr/local/bin
WORKDIR /openedx/

CMD configurator -c /openedx/config/config.json interactive && \
    configurator -c /openedx/config/config.json substitute /openedx/templates/ /openedx/output/
