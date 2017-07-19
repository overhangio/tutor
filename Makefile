migrate:
	docker-compose run lms ./manage.py lms migrate --settings=production
assets:
	docker-compose run lms paver update_assets lms --settings=production
