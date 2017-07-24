FROM nginx:1.13

VOLUME /openedx/data

COPY ./config/lms.conf /etc/nginx/conf.d/lms.conf
COPY ./config/cms.conf /etc/nginx/conf.d/cms.conf
