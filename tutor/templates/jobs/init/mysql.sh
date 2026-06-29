echo "Initialising MySQL..."
mysql_connection_max_attempts=10
mysql_connection_attempt=0
until mysql -u {{ MYSQL_ROOT_USERNAME }} --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" --port {{ MYSQL_PORT }} -e 'exit'
do
    mysql_connection_attempt=$(expr $mysql_connection_attempt + 1)
    echo "    [$mysql_connection_attempt/$mysql_connection_max_attempts] Waiting for MySQL service (this may take a while)..."
    if [ $mysql_connection_attempt -eq $mysql_connection_max_attempts ]
    then
      echo "MySQL initialisation error" 1>&2
      exit 1
    fi
    sleep 10
done
echo "MySQL is up and running"

# edx-platform database
mysql -u {{ MYSQL_ROOT_USERNAME }} --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" --port {{ MYSQL_PORT }} -e "CREATE DATABASE IF NOT EXISTS {{ OPENEDX_MYSQL_DATABASE }};"
# This command may fail if the specified user has created a custom view, such
# as is done in the enterprise app.
#
# Yes, even 'if not exists' does not prevent this. :/
# https://bugs.mysql.com/bug.php?id=107139
#
# When our minimum version of MySQL is 8.4, we should be able to drop this
# || true workaround, as the SET_USER_ID privilege has been removed.
mysql -u {{ MYSQL_ROOT_USERNAME }} --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" --port {{ MYSQL_PORT }} -e "CREATE USER IF NOT EXISTS '{{ OPENEDX_MYSQL_USERNAME }}';" || true
# If the user truly doesn't exist, we'll get an error here.
mysql -u {{ MYSQL_ROOT_USERNAME }} --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" --port {{ MYSQL_PORT }} -e "ALTER USER '{{ OPENEDX_MYSQL_USERNAME }}'@'%' IDENTIFIED BY '{{ OPENEDX_MYSQL_PASSWORD }}';"
mysql -u {{ MYSQL_ROOT_USERNAME }} --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" --port {{ MYSQL_PORT }} -e "GRANT ALL ON {{ OPENEDX_MYSQL_DATABASE }}.* TO '{{ OPENEDX_MYSQL_USERNAME }}'@'%';"
