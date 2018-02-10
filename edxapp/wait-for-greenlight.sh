#!/bin/bash

echo "Checking system..."
until ./manage.py lms --settings=production check
do
  printf "."
  sleep 1
done

echo -e "\nSystem is ready \\o/"
