ROOT_DIR                = $(shell git rev-parse --show-toplevel)
TEMPLATE_CMD            = @sed 's+REPLACE_NAMESPACE+${NAMESPACE}+g'#; s+REPLACE_GPU_COUNT+${GPU_COUNT}+g; s+REPLACE_SUBSCRIPTION_NAME+${APP_REPOSITORY}+g'
DEPLOYMENT_NAME         = perceptilabs
NAMESPACE_PREFIX        = a
NAMESPACE               = $(shell oc get namespaces --no-headers --output='custom-columns=NAME:.metadata.name' | grep "^${NAMESPACE_PREFIX}" | head -n 1 | grep ".*" || echo "${NAMESPACE_PREFIX}1")
NAMESPACE_SEQUENCE      = $(shell echo "${NAMESPACE}" | sed 's/^${NAMESPACE_PREFIX}//g')
NEXT_NAMESPACE_SEQUENCE = $(shell echo $$((${NAMESPACE_SEQUENCE}+1)))
NEXT_NAMESPACE          = ${NAMESPACE_PREFIX}${NEXT_NAMESPACE_SEQUENCE}
REMOTE                  ?= $(shell git remote -v | grep "git@ssh.dev.azure.com:.*/PerceptiLabs/PerceptiLabs/PerceptiLabs (fetch)$$" | cut -d $$'\t' -f 1)
DOCKER_TAG_PATTERN      = ^docker_\\d\\+$$
LATEST_BUILD            ?= $(shell git fetch ${REMOTE} > /dev/null && git tag | grep ${DOCKER_TAG_PATTERN} | cut -d _ -f 2 | sort | tail -n 1)
BUILD_NUMBER            ?= ${LATEST_BUILD}


undeploy: ## remove the helm chart
	helm uninstall --namespace=${NAMESPACE} ${DEPLOYMENT_NAME}

deploy: require-BUILD_NUMBER require-NAMESPACE require-PERCEPTILABS_AZURECR_PWD #secret ## deploy the helm chart
	echo "Installing tag ${BUILD_NUMBER}"
	helm install --namespace=${NAMESPACE} --create-namespace ${DEPLOYMENT_NAME} --set imageCredentials.password=${PERCEPTILABS_AZURECR_PWD} --set pl_docker_tag=${BUILD_NUMBER} --debug ./chart

remove_namespace:  ## delete the namespace completely
	[ -n "${NAMESPACE}" ] && oc delete namespace ${NAMESPACE} --ignore-not-found &

redeploy: remove_namespace deploy  ## delete the namespace and redeploy everything

deploy_next: remove_namespace ## delete the current ns and redeploys to the next ns in the sequence
	echo Installing tag ${BUILD_NUMBER} to namespace ${NEXT_NAMESPACE}
	helm install --namespace=${NEXT_NAMESPACE} --create-namespace ${DEPLOYMENT_NAME} --set imageCredentials.password=${PERCEPTILABS_AZURECR_PWD} --set pl_docker_tag=${BUILD_NUMBER} ./chart --debug
	echo "Deployed to namespace ${NEXT_NAMESPACE}"

open:
	open "http://$(shell oc get routes --namespace=${NAMESPACE} --output=jsonpath='{.items[0].spec.host}')"

rygg_api_log:
	oc logs $(shell oc get pods --selector=app=rygg-api --namespace=${NAMESPACE} --no-headers --output=custom-columns=NAME:.metadata.name) --namespace=${NAMESPACE} --follow

rygg_worker_log:
	oc logs $(shell oc get pods --selector=app=rygg-worker --namespace=${NAMESPACE} --no-headers --output=custom-columns=NAME:.metadata.name) --namespace=${NAMESPACE} --follow

training_log:
	oc logs $(shell oc get pods --selector=app=training-worker --namespace=${NAMESPACE} --no-headers --output=custom-columns=NAME:.metadata.name) --namespace=${NAMESPACE} --follow

render_log:
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

bounce_rygg: ## Bounce the rygg services to trigger a pull from quay and a restart
	@oc scale --replicas=0 deployments/rygg-api --namespace=${NAMESPACE}
	@oc scale --replicas=0 deployments/rygg-worker --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/rygg-api --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/rygg-worker --namespace=${NAMESPACE}

bounce_kernel: ## Bounce the kernel services to trigger a pull from quay and a restart
	@oc scale --replicas=0 deployments/render --namespace=${NAMESPACE}
	@oc scale --replicas=0 deployments/training-worker --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/render --namespace=${NAMESPACE}
	@oc scale --replicas=1 deployments/training-worker --namespace=${NAMESPACE}

bounce_frontend: ## Bounce the kernel services to trigger a pull from quay and a restart
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

