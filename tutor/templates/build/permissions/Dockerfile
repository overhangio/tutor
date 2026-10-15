FROM docker.io/alpine:3.13.6
LABEL maintainer="Overhang.io <contact@overhang.io>"

COPY ./setowner.sh /usr/local/bin/setowner
RUN chmod a+x /usr/local/bin/setowner

# Grants busybox the ability to chown files it doesn't own, without running as
# root. Kubernetes does not propagate added capabilities into a non-root
# container's effective set (no ambient capability support, see
# kubernetes/kubernetes#56374), so capabilities.add in a pod's securityContext
# alone is silently dropped at execve.
#
# This must be set on /bin/busybox itself, not a dedicated copy used only for
# the chown step: with allowPrivilegeEscalation: false, a file capability can
# only elevate a process up to what it already had in ITS OWN pre-exec
# permitted set - and that's empty for anything except the container's single
# direct entrypoint exec (confirmed empirically: capabilities.add populates
# the bounding set correctly, but not permitted/effective/inheritable, for a
# non-root process). fix-volume-permissions.sh runs as a shell script, so
# `sh` is that one direct exec, and chown is a later, separate exec from
# inside it - scoping the capability to a different file than the one `sh`
# itself runs as means that later exec can't be granted anything. Setting it
# on busybox directly means `sh`, `timeout` and `chown` are all the same
# already-capable file, so the capability carries through the whole chain
# (verified on an actual cluster, both ways).
RUN apk add --no-cache libcap && setcap cap_chown=ep /bin/busybox

ENTRYPOINT ["setowner"]
