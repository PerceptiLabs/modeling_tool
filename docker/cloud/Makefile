DEPLOYMENT_NAME         ?= perceptilabs
NAMESPACE_PREFIX        ?= a

# Shortcut for setting the namespace in an env var. Deduces the namespace from the namespace prefix
NAMESPACE               ?= $(shell oc get namespaces --no-headers --output='custom-columns=NAME:.metadata.name' | grep "^${NAMESPACE_PREFIX}" | head -n 1 | grep ".*" || echo "${NAMESPACE_PREFIX}1")

# For finding source directories when building docker images
ROOT_DIR                = $(shell git rev-parse --show-toplevel)

# For auto-generating sequential namespaces
NAMESPACE_SEQUENCE      = $(shell echo "${NAMESPACE}" | sed 's/^${NAMESPACE_PREFIX}//g')
NEXT_NAMESPACE_SEQUENCE = $(shell echo $$((${NAMESPACE_SEQUENCE}+1)))
NEXT_NAMESPACE          = ${NAMESPACE_PREFIX}${NEXT_NAMESPACE_SEQUENCE}

# For automatically deducing the latest docker build
REMOTE                  ?= $(shell git remote -v | grep "git@ssh.dev.azure.com:.*/PerceptiLabs/PerceptiLabs/PerceptiLabs (fetch)$$" | cut -d $$'\t' -f 1)
DOCKER_TAG_PATTERN      = ^docker_\\d\\+$$
LATEST_BUILD            ?= $(shell git fetch ${REMOTE} > /dev/null && git tag | grep ${DOCKER_TAG_PATTERN} | cut -d _ -f 2 | sort | tail -n 1)
BUILD_NUMBER            ?= ${LATEST_BUILD}

APP_VERSION 						?= $(shell cat ${ROOT_DIR}/VERSION)

# Requires a build id to append to the package
package: require-BUILD_ID
	helm package ./pl-saas --app-version ${APP_VERSION} --version ${APP_VERSION}-${BUILD_ID}

login:
	 $(if $(shell oc whoami ),,$(error You must run `oc login` first))

os8_cluster_setup: ## set up cluster-wide stuff for os8 (e.g. machine scalers, clusterautoscaler)
	helm upgrade --install cluster --debug ./os8

undeploy: login ## remove the helm chart
	helm uninstall --namespace=${NAMESPACE} ${DEPLOYMENT_NAME}

deploy: login require-BUILD_NUMBER require-NAMESPACE require-PERCEPTILABS_DOCKER_PULL_SECRET #secret ## deploy the helm chart
	@echo "Installing tag ${BUILD_NUMBER}"
	helm upgrade --install --namespace=${NAMESPACE} --create-namespace ${DEPLOYMENT_NAME} --set imageCredentials.password=${PERCEPTILABS_DOCKER_PULL_SECRET} --set pl_docker_tag=${BUILD_NUMBER} --debug ./pl-saas

remove_namespace: login  ## delete the namespace completely
	[ -n "${NAMESPACE}" ] && oc delete namespace ${NAMESPACE} --ignore-not-found &

redeploy: remove_namespace deploy  ## delete the namespace and redeploy everything

deploy_next: login remove_namespace require-PERCEPTILABS_DOCKER_PULL_SECRET ## delete the current ns and redeploys to the next ns in the sequence
	echo Installing tag ${BUILD_NUMBER} to namespace ${NEXT_NAMESPACE}
	helm install --namespace=${NEXT_NAMESPACE} --create-namespace ${DEPLOYMENT_NAME} --set imageCredentials.password=${PERCEPTILABS_DOCKER_PULL_SECRET} --set pl_docker_tag=${BUILD_NUMBER} ./pl-saas --debug
	echo "Deployed to namespace ${NEXT_NAMESPACE}"

list_deployments:
	helm list --all --all-namespaces

open:
	open "http://$(shell oc get routes --namespace=${NAMESPACE} --output=jsonpath='{.items[0].spec.host}')"

rygg_shell: login ## Get logs from the rygg api pod
	oc exec -it $(shell oc get pods --selector=app=rygg-api --namespace=${NAMESPACE} --no-headers --output=custom-columns=NAME:.metadata.name) --namespace=${NAMESPACE} -- bash

rygg_api_log: login ## Get logs from the rygg api pod
	oc logs $(shell oc get pods --selector=app=rygg-api --namespace=${NAMESPACE} --no-headers --output=custom-columns=NAME:.metadata.name) --namespace=${NAMESPACE} --follow

rygg_worker_log: login ## Get logs from a rygg worker pod
	oc logs $(shell oc get pods --selector=app=rygg-worker --namespace=${NAMESPACE} --no-headers --output=custom-columns=NAME:.metadata.name) --namespace=${NAMESPACE} --follow

monitor_log: login ## Get logs from a monitor pod
	oc logs $(shell oc get pods --selector=app=monitor --namespace=${NAMESPACE} --no-headers --output=custom-columns=NAME:.metadata.name) --namespace=${NAMESPACE} --follow

training_log: login ## Get logs from a training worker pod
	oc logs $(shell oc get pods --selector=app=training-worker --namespace=${NAMESPACE} --no-headers --output=custom-columns=NAME:.metadata.name) --namespace=${NAMESPACE} --follow

render_log: login ## Get logs from the render api pod
	oc logs $(shell oc get pods --selector=app=render --namespace=${NAMESPACE} --no-headers --output=custom-columns=NAME:.metadata.name) --namespace=${NAMESPACE} --follow

build_debug_rygg: ## build rygg and push to quay
	# Assemble for the dockerfile
	cd ${ROOT_DIR}/scripts && \
	source .venv/bin/activate && \
	./build.py docker rygg

	# build the image
	cd ${ROOT_DIR}/build/docker/rygg && \
	docker build . --tag=dev/rygg:latest

	# push the image to quay
	docker tag dev/rygg:latest quay.io/perceptilabs/rygg-dev
	docker push quay.io/perceptilabs/rygg-dev

build_debug_monitor: ## build monitor and push to quay
	# Assemble for the dockerfile
	cd ${ROOT_DIR}/scripts && \
	source .venv/bin/activate && \
	./build.py docker monitor

	# push the image to quay
	docker tag dev/monitor:latest quay.io/perceptilabs/monitor-dev
	docker push quay.io/perceptilabs/monitor-dev

build_debug_kernel: ## build kernel and push to quay
	# Assemble for the dockerfile
	cd ${ROOT_DIR}/scripts && \
	source .venv/bin/activate && \
	./build.py docker kernel

	# build the image
	cd ${ROOT_DIR}/build/docker/kernel && \
	docker build . --tag=dev/kernel:latest

	# push the image to quay
	docker tag dev/kernel:latest quay.io/perceptilabs/kernel-dev
	docker push quay.io/perceptilabs/kernel-dev

build_debug_frontend: ## build frontend and push to quay
	# Assemble for the dockerfile
	cd ${ROOT_DIR}/scripts && \
	source .venv/bin/activate && \
	./build.py docker frontend

	# build the image
	cd ${ROOT_DIR}/build/docker/frontend && \
	docker build . --tag=dev/frontend:latest

	# push the image to quay
	docker tag dev/frontend:latest quay.io/perceptilabs/frontend-dev
	docker push quay.io/perceptilabs/frontend-dev

bounce_rygg: login ## Bounce the rygg services to trigger a pull from quay and a restart
	@oc scale --replicas=0 deployments/rygg-api --namespace=${NAMESPACE}
	@oc scale --replicas=0 deployments/rygg-worker --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/rygg-api --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/rygg-worker --namespace=${NAMESPACE}

bounce_monitor: login ## Bounce the kernel services to trigger a pull from quay and a restart
	@oc scale --replicas=0 deployments/monitor --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/monitor --namespace=${NAMESPACE}

bounce_kernel: login ## Bounce the kernel services to trigger a pull from quay and a restart
	@oc scale --replicas=0 deployments/render --namespace=${NAMESPACE}
	@oc scale --replicas=0 deployments/training-worker --namespace=${NAMESPACE}
	@oc scale --replicas=0 deployments/misc-worker --namespace=${NAMESPACE}
	@oc scale --replicas=0 deployments/flower --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/render --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/training-worker --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/misc-worker --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/flower --namespace=${NAMESPACE}

bounce_frontend: login ## Bounce the kernel services to trigger a pull from quay and a restart
	@oc scale --replicas=0 deployments/frontend --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/frontend --namespace=${NAMESPACE}

#######################################################
# Plumbing

require-%:
	@: $(if ${${*}},,$(error You must pass the $* environment variable))


# script-kiddied from https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# .PHONY:

