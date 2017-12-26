#!/bin/bash

echo "Waiting for mysql database"
until echo "show tables;" | ./manage.py lms --settings=production dbshell
do
  printf "."
  sleep 1
done

echo -e "\nmysql database ready"
