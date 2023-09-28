.. _backup_tutorial:

Making backups and migrating data
---------------------------------

With Tutor, all data are stored in a single folder. This means that it's extremely easy to migrate an existing platform to a different server. For instance, it's possible to configure a platform locally on a laptop, and then move this platform to a production server.

1. Make sure `tutor` is installed on both servers with the same version.
2. Stop any running platform on server 1::

    tutor local stop

3. Transfer the configuration, environment, and platform data from server 1 to server 2::

    sudo rsync -avr "$(tutor config printroot)/" username@server2:/tmp/tutor/

4. On server 2, move the data to the right location::

    mv /tmp/tutor "$(tutor config printroot)"

5. Start the instance with::

    tutor local start -d

Making database dumps
---------------------

To dump all data from the MySQL and Mongodb databases used on the platform, run the following commands::

    tutor local exec \
        -e USERNAME="$(tutor config printvalue MYSQL_ROOT_USERNAME)" \
        -e PASSWORD="$(tutor config printvalue MYSQL_ROOT_PASSWORD)" \
        mysql sh -c 'mysqldump --all-databases --user=$USERNAME --password=$PASSWORD > /var/lib/mysql/dump.sql'
    tutor local exec mongodb mongodump --out=/data/db/dump.mongodb

The ``dump.sql`` and ``dump.mongodb`` files will be located in ``$(tutor config printroot)/data/mysql`` and ``$(tutor config printroot)/data/mongodb``.
