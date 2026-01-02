.. _web_proxy:

Running Open edX behind a web proxy
===================================

In a vanilla deployment of Open edX with Tutor, a web proxy is launched to process incoming web requests. This web proxy is an instance of `Caddy <https://caddyserver.com/>`__ running inside a Docker container. This Docker container listens to ports 80 and 443 on the host.

Quite often, there is already a web proxy running on the host, and this web proxy also listens to ports 80 and 443. In such a configuration, the Caddy container will not be able to start out of the box. So you should make small changes to the Tutor configuration by running::

    tutor config save --set ENABLE_WEB_PROXY=false --set CADDY_HTTP_PORT=81

With these changes, Tutor will no longer listen to ports 80 and 443 on the host. In this configuration, the Caddy container will only listen to port 81 on the host. Web requests will follow this path::

    Client → Web proxy (http(s)://yourhost) → Caddy (0.0.0.0:81) → Granian (LMS/CMS/...)

.. warning::
    In this setup, the Caddy HTTP port (81) will be exposed to the world. Make sure to configure your server firewall to block unwanted connections to the Caddy container. Alternatively, you can configure the Caddy container to accept only local connections::

        tutor config save --set ENABLE_WEB_PROXY=false --set CADDY_HTTP_PORT=127.0.0.1:81

It is then your responsibility to configure the web proxy on the host. There are too many use cases and proxy vendors, so Tutor does not provide configuration files that will work for everyone. You should configure your web proxy to:

- Capture traffic for the following hostnames: LMS_HOST, PREVIEW_LMS_HOST, CMS_HOST, as well as any additional host exposed by your plugins (MFE_HOST, CREDENTIALS_HOST, etc.). See each plugin documentation for more information.
- If SSL/TLS is enabled:
    - Perform SSL/TLS termination using your own certificates.
    - Forward http traffic to https.
- Set the following headers appropriately: ``X-Forwarded-Proto``, ``X-Forwarded-Port``.
- Forward all traffic to ``localhost:81`` (or whatever port indicated by CADDY_HTTP_PORT, see above).
- If possible, add support for `HTTP/3 <https://en.wikipedia.org/wiki/HTTP/3>`__, which considerably improves performance for Open edX (see `this comment <https://github.com/overhangio/tutor/issues/845#issuecomment-1566964289>`__).

.. note::
    If you want to run Open edX at ``https://...`` urls (as you probably do in production) it is *crucial* that the ``ENABLE_HTTPS`` flag is set to ``true``. If not, the web services will be configured to run at ``http://...`` URLs, and all sorts of trouble will happen. Therefore, make sure to continue answering ``y`` ("yes") to the quickstart dialogue question "Activate SSL/TLS certificates for HTTPS access?".
