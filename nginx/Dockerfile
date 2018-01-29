FROM nginx:1.13
VOLUME /openedx/data/lms
VOLUME /openedx/data/cms

COPY ./config/lms.conf /etc/nginx/conf.d/lms.conf
COPY ./config/cms.conf /etc/nginx/conf.d/cms.conf
