.PHONY: config volumes services deployments
.DEFAULT_GOAL := help

all: namespace config deploy assets

namespace: ## Create the platform namespace
	kubectl create -f namespace.yml

config: ## Create configmap objects
	kubectl create configmap nginx-config --from-file=../env/nginx --namespace=openedx
	kubectl create configmap mysql-config --from-env-file=../env/mysql/auth.env --namespace=openedx
	kubectl create configmap openedx-settings-lms --from-file=../env/openedx/settings/lms --namespace=openedx
	kubectl create configmap openedx-settings-cms --from-file=../env/openedx/settings/cms --namespace=openedx
	kubectl create configmap openedx-config --from-file=../env/openedx/config --namespace=openedx
	kubectl create configmap openedx-scripts --from-file=../env/openedx/scripts --namespace=openedx

volumes: ## Create volumes
	kubectl create -f volumes/ --recursive=true --namespace=openedx
deployments: ## Create deployments
	kubectl create -f deployments/ --recursive=true --namespace=openedx
services: ## Create services
	kubectl create -f services/ --recursive=true --namespace=openedx
deploy: volumes services deployments

upgrade: down deploy

down: ## Delete all non-persistent objects
	kubectl delete -f services/ --recursive=true --namespace=openedx
	kubectl delete -f deployments/ --recursive=true --namespace=openedx

delete:
	# TODO ask question to make sure user reaaaaaaally want to do this
	kubectl delete namespace openedx


##################### Databases

databases: provision-databases migrate #provision-oauth2 ## Bootstrap databases
provision-databases: ## Create necessary databases and users
	@$(MAKE) lms-exec COMMAND="bash /openedx/scripts/provision.sh"
provision-oauth2: ## Create users for SSO between services
	@$(MAKE) lms-exec COMMAND="bash /openedx/scripts/oauth2.sh"
migrate: migrate-openedx #migrate-forum $(extra_migrate_targets) ## Perform all database migrations
migrate-openedx: ## Perform database migrations on LMS/CMS
	@$(MAKE) lms-exec COMMAND="bash -c 'dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py lms --settings=tutor.production migrate'"
	#@$(MAKE) cms-exec COMMAND="bash -c 'dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py cms --settings=tutor.production migrate'"
	#$(MAKE) reindex-courses
#migrate-forum: ## Perform database migrations on discussion forums
	#$(DOCKER_COMPOSE_RUN) forum bash -c "bundle exec rake search:initialize && \
		#bundle exec rake search:rebuild_index"
#migrate-notes: ## Perform database migrations for the Notes service
	#$(DOCKER_COMPOSE_RUN) notes ./manage.py migrate
#migrate-xqueue: ## Perform database migrations for the XQueue service
	#$(DOCKER_COMPOSE_RUN) xqueue ./manage.py migrate
#reindex-courses: ## Refresh course index so they can be found in the LMS search engine
	#$(DOCKER_COMPOSE_RUN) cms ./manage.py cms reindex_course --all --setup

##################### Assets

assets:
	$(MAKE) pod-exec APP=nginx COMMAND="rm -rf /var/www/openedx/staticfiles"
	kubectl cp openedx/openedx:/openedx/staticfiles openedx/nginx:/var/www/openedx/staticfiles

##################### Various commands

lms-shell: ## Launch a shell inside an lms pod
	@$(MAKE) lms-exec COMMAND=bash
lms-exec: ## Execute a command inside an lms pod: make lms-exec COMMAND="..."
	@$(MAKE) pod-exec APP=lms COMMAND=$(COMMAND)
pod-exec: ## Execute a command inside an arbitrary pod: make pod-exec APP=appname COMMAND="..."
	kubectl exec -n openedx -it $$(kubectl get pods -n openedx --selector=app=$(APP) -o name | head -1 | cut -d '/' -f 2) -- $(COMMAND)

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'

