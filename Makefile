.PHONY: all configure build migrate assets up daemon

all: configure build migrate assets daemon

##################### Bootstrapping commands

configure:
	./configure

build:
	docker-compose build

migrate:
	docker-compose run --rm lms bash -c "./wait-for-mysql.sh && ./manage.py lms migrate --settings=production"
	docker-compose run --rm cms bash -c "./wait-for-mysql.sh && ./manage.py cms migrate --settings=production"

assets:
	docker-compose run --rm lms paver update_assets lms --settings=production
	docker-compose run --rm cms paver update_assets cms --settings=production

##################### Running commands

up:
	docker-compose up

daemon:
	docker-compose up -d && \
	echo "Daemon is up and running"

stop:
	docker-compose stop

##################### Additional commands

lms-shell:
	docker-compose run --rm lms ./manage.py lms shell --settings=production
cms-shell:
	docker-compose run --rm lms ./manage.py cms shell --settings=production

import-demo-course:
	docker-compose run --rm cms /bin/bash -c "git clone https://github.com/edx/edx-demo-course ../edx-demo-course && git -C ../edx-demo-course checkout open-release/ginkgo.master && python ./manage.py cms --settings=production import ../data ../edx-demo-course"
