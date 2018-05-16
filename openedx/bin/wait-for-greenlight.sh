#!/bin/bash

echo "Checking system..."
until ./manage.py $SERVICE_VARIANT check
do
  printf "."
  sleep 1
done

echo -e "\nSystem is ready \\o/"
