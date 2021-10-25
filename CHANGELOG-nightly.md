# Changelog (nightly branch)

Note: Breaking changes between versions are indicated by "💥".

- 💥[Feature] Get rid of the nginx container and service, which is now replaced by Caddy. this has the following consequences:
    - Patches "nginx-cms", "nginx-lms", "nginx-extra", "local-docker-compose-nginx-aliases" are replaced by "caddyfile-cms", "caddyfile-lms", "caddyfile", " local-docker-compose-caddy-aliases".
    - Patches "k8s-deployments-nginx-volume-mounts", "k8s-deployments-nginx-volumes" were obsolete and are removed.
    - The `NGINX_HTTP_PORT` setting is renamed to `CADDY_HTTP_PORT`.