.PHONY: env volumes services deployments
.DEFAULT_GOAL := help

podname = kubectl get pods -n openedx --selector=app=$(1) -o name | head -1 | cut -d '/' -f 2
podexec = kubectl exec -n openedx -it $$($(call podname,$(1))) -- $(2)

all: configure deploy databases ## Provision a full platform from scratch

configure:
	@$(MAKE) -s -C ../.. --always-make config.json
	@$(MAKE) -s env

env:
	@$(MAKE) -s -C .. env
	@$(MAKE) -s -C ../.. substitute TEMPLATES=$(PWD)/templates OUTPUT=$(PWD)/env

namespace: ## Create the platform namespace
	kubectl create -f namespace.yml
configmaps: ## Create configmap objects
	kubectl create configmap nginx-config --from-file=../env/nginx --namespace=openedx
	kubectl create configmap mysql-config --from-env-file=../env/mysql/auth.env --namespace=openedx
	kubectl create configmap openedx-settings-lms --from-file=../env/openedx/settings/lms --namespace=openedx
	kubectl create configmap openedx-settings-cms --from-file=../env/openedx/settings/cms --namespace=openedx
	kubectl create configmap openedx-config --from-file=../env/openedx/config --namespace=openedx
	kubectl create configmap openedx-scripts --from-file=../env/openedx/scripts --namespace=openedx
volumes: ## Create volumes
	kubectl create -f volumes/ --recursive=true --namespace=openedx
services: ## Create services
	kubectl create -f services/ --recursive=true --namespace=openedx
deployments: ## Create deployments
	kubectl create -f deployments/ --recursive=true --namespace=openedx
ingress: ## Create ingress
	kubectl create -f env/ingress.yml --namespace=openedx
deploy: namespace volumes configmaps services deployments ingress ## Deploy a platform from scratch

upgrade: down ## Upgrade an already running platform
	@$(MAKE) -s namespace || true
	@$(MAKE) -s configmaps || true
	@$(MAKE) -s volumes || true
	@$(MAKE) -s services || true
	@$(MAKE) -s deployments || true
	@$(MAKE) -s ingress || true

down: ## Delete all non-persistent objects
	kubectl delete -f services/ --recursive=true --namespace=openedx || true
	kubectl delete -f deployments/ --recursive=true --namespace=openedx || true
	kubectl delete configmap --all --namespace openedx || true

delete: ## Delete EVERYTHING! (with no confirmation at all)
	# TODO ask question to make sure user reaaaaaaally want to do this
	kubectl delete namespace openedx


##################### Databases

databases: provision-databases migrate #provision-oauth2 ## Bootstrap databases
provision-databases: ## Create necessary databases and users
	$(call podexec,lms,bash /openedx/scripts/provision.sh)
provision-oauth2: ## Create users for SSO between services
	$(call podexec,lms,bash /openedx/scripts/oauth2.sh)
migrate: migrate-openedx migrate-forum ## Perform all database migrations
migrate-openedx: migrate-lms migrate-cms reindex-courses ## Perform database migrations on LMS/CMS
migrate-lms:
	$(call podexec,lms,bash -c 'dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py lms migrate')
migrate-cms:
	$(call podexec,cms,bash -c 'dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py cms migrate')
migrate-forum: ## Perform database migrations on discussion forums
	$(call podexec,forum,bash -c "bundle exec rake search:initialize && \
		bundle exec rake search:rebuild_index")
migrate-notes: ## Perform database migrations for the Notes service
	$(call podexec,notes,./manage.py migrate)
migrate-xqueue: ## Perform database migrations for the XQueue service
	$(call podexec,xqueue,./manage.py migrate)
reindex-courses: ## Refresh course index so they can be found in the LMS search engine
	$(call podexec,cms,./manage.py cms reindex_course --all --setup)

##################### Various Open edX commands

lms-shell: ## Launch a shell inside an lms pod
	$(call podexec,lms,bash)
lms-exec: ## Execute a command inside an lms pod: make lms-exec COMMAND="..."
	$(call podexec,lms,$(COMMAND))
pod-exec: ## Execute a command inside an arbitrary pod: make pod-exec APP=appname COMMAND="..."
	$(call podexec,$(APP),$(COMMAND))

# TODO replace these tasks with Job objects
import-demo-course: ## Import the demo course from edX
	$(call podexec,cms,/bin/bash -c "\
		git clone https://github.com/edx/edx-demo-course --branch open-release/hawthorn.2 --depth 1 ../edx-demo-course \
		&& python ./manage.py cms import ../data ../edx-demo-course")

create-staff-user: ## Create a user with admin rights: make create-staff-user USERNAME=... EMAIL=...
	$(call podexec,lms,/bin/bash -c "\
		./manage.py lms manage_user --superuser --staff ${USERNAME} ${EMAIL} \
		&& ./manage.py lms changepassword ${USERNAME}")

##################### Various minikube command

minikube-open:
	minikube service nginx --namespace=openedx

##################### Various k8s commands

k8s-proxy: ## Create a proxy to the Kubernetes API server
	kubectl proxy
k8s-dashboard: ## Create the dashboard
	kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/master/aio/deploy/recommended/kubernetes-dashboard.yaml
k8s-admin: ## Create an admin user for accessing the Kubernetes dashboard
	kubectl -f admin.yml
k8s-admin-token: ## Print the admin token required to log in the dashboard
	kubectl -n kube-system describe secret $$(kubectl -n kube-system get secret | grep admin-user | awk '{print $$1}') | grep token: | awk '{print $$2}'

##################### Information

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/\n               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
