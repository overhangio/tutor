FROM ubuntu:18.04

RUN apt update && \
  apt install -y python3 python3-pip
RUN pip3 install jinja2

RUN mkdir /openedx
VOLUME /openedx/config
COPY ./bin/configure.py /openedx/configure.py
COPY ./bin/docker-entrypoint.sh /openedx/docker-entrypoint.sh
WORKDIR /openedx

ENV SILENT=''
ENV ACTIVATE_HTTPS=''
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ./configure.py interactive ${SILENT:+--silent} && \
  ./configure.py substitute ./config/openedx/templates/lms.env.json.templ ./config/openedx/lms.env.json && \
  ./configure.py substitute ./config/openedx/templates/cms.env.json.templ ./config/openedx/cms.env.json && \
  ./configure.py substitute ./config/openedx/templates/lms.auth.json.templ ./config/openedx/lms.auth.json && \
  ./configure.py substitute ./config/openedx/templates/cms.auth.json.templ ./config/openedx/cms.auth.json && \
  ./configure.py substitute ./config/openedx/templates/provision.sh.templ ./config/openedx/provision.sh && \
  ./configure.py substitute ./config/xqueue/templates/universal.py.templ ./config/xqueue/universal.py && \
  ./configure.py substitute ./config/mysql/templates/auth.env.templ ./config/mysql/auth.env && \
  ./configure.py substitute ./config/nginx/templates/lms.conf.templ ./config/nginx/lms.conf && \
  ./configure.py substitute ./config/nginx/templates/cms.conf.templ ./config/nginx/cms.conf && \
  ./configure.py substitute ./config/android/templates/universal.yaml.templ ./config/android/universal.yaml && \
  ./configure.py substitute ./config/letsencrypt/templates/certonly.sh.templ ./config/letsencrypt/certonly.sh
