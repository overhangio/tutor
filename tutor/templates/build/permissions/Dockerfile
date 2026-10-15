FROM docker.io/alpine:3.13.6
LABEL maintainer="Overhang.io <contact@overhang.io>"

COPY ./setowner.sh /usr/local/bin/setowner
RUN chmod a+x /usr/local/bin/setowner

# Grants busybox the ability to chown files it doesn't own, without running as
# root. Kubernetes does not propagate added capabilities into a non-root
# container's effective set (no ambient capability support, see
# kubernetes/kubernetes#56374), so capabilities.add in a pod's securityContext
# alone would be silently dropped at execve. A file capability baked into the
# image is unaffected by that gap and survives allowPrivilegeEscalation: false
# (verified empirically against a real cluster). Used by the k8s
# fix-volume-permissions init containers, which run as the service's own
# non-root uid with capabilities: {add: [CHOWN], drop: [ALL]}.
RUN apk add --no-cache libcap && setcap cap_chown=ep /bin/busybox

ENTRYPOINT ["setowner"]
