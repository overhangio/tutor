# Changelog (nightly branch)

Note: Breaking changes between versions are indicated by "💥".

- [Bugfix] Fix running Caddy container in k8s, which should always be the case even if `ENABLE_WEB_PROXY` is false.
- 💥[Improvement] Run all services as unprivileged containers, for better security. This has multiple consequences:
  - The "openedx-dev" image is now built with `tutor dev dc build lms`.
  - The "smtp" service now runs the "devture/exim-relay" Docker image, which is unprivileged. Also, the default SMTP port is now 8025.
- 💥[Feature] Get rid of the nginx container and service, which is now replaced by Caddy. this has the following consequences:
    - Patches "nginx-cms", "nginx-lms", "nginx-extra", "local-docker-compose-nginx-aliases" are replaced by "caddyfile-cms", "caddyfile-lms", "caddyfile", " local-docker-compose-caddy-aliases".
    - Patches "k8s-deployments-nginx-volume-mounts", "k8s-deployments-nginx-volumes" were obsolete and are removed.
    - The `NGINX_HTTP_PORT` setting is renamed to `CADDY_HTTP_PORT`.
