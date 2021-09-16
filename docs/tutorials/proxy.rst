.. _web_proxy:

Running Open edX behind a web proxy
===================================

The containerized web server (`Caddy <https://caddyserver.com/>`__) needs to listen to ports 80 and 443 on the host. If there is already a webserver running on the host, such as Apache or Nginx, the caddy container will not be able to start. Tutor supports running behind a web proxy. To do so, add the following configuration::

       tutor config save --set RUN_CADDY=false --set NGINX_HTTP_PORT=81

In this example, the nginx container port would be mapped to 81 instead of 80. You must then configure the web proxy on the host. As of v11.0.0, configuration files are no longer provided for automatic configuration of your web proxy. Basically, you should setup a reverse proxy to `localhost:NGINX_HTTP_PORT` from the following hosts: LMS_HOST, PREVIEW_LMS_HOST, CMS_HOST, as well as any additional host exposed by your plugins.

.. warning::
    In this setup, the Nginx HTTP port will be exposed to the world. Make sure to configure your server firewall to block unwanted connections to your server's ``NGINX_HTTP_PORT``. Alternatively, you can configure the Nginx container to accept only local connections::

        tutor config save --set NGINX_HTTP_PORT=127.0.0.1:81
