FROM nginx:1.13

RUN mkdir /openedx
RUN mkdir /openedx/course_static
RUN mkdir /openedx/static_files
RUN mkdir /openedx/uploads

VOLUME /openedx/course_static
VOLUME /openedx/staticfiles
VOLUME /openedx/uploads

# Wait until LMS becomes available
# TODO we shouldn't have to wait
RUN sleep 10
COPY lms.conf /etc/nginx/conf.d/lms.conf
