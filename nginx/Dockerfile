FROM nginx:1.13
VOLUME /openedx/data

# Install ced
RUN apt update
RUN apt install -y python-pip
RUN pip install ced

ARG lms_host=localhost
ARG cms_host=studio.$lms_host
ENV LMS_HOST=$lms_host CMS_HOST=$cms_host

COPY ./config/lms.conf.templ /etc/nginx/conf.d/lms.conf.templ
RUN ced -o /etc/nginx/conf.d/lms.conf -d £ /etc/nginx/conf.d/lms.conf.templ
COPY ./config/cms.conf.templ /etc/nginx/conf.d/cms.conf.templ
RUN ced -o /etc/nginx/conf.d/cms.conf -d £ /etc/nginx/conf.d/cms.conf.templ
