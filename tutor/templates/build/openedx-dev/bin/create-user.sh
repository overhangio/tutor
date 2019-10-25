#! /bin/sh -e
USERID=$1

if [ "$USERID" != "" ] && [ "$USERID" != "0" ]
then
  echo "Creating 'openedx' user with id $USERID"
  useradd --home-dir /openedx --uid $USERID openedx
  chown -R openedx:openedx /openedx
else
  echo "Running as root"
fi