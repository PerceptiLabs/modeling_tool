# copied from operator-tools Makefile. It would be nice to not need this
TEMPLATE_CMD         = @sed 's+REPLACE_NAMESPACE+${NAMESPACE}+g'#; s+REPLACE_GPU_COUNT+${GPU_COUNT}+g; s+REPLACE_SUBSCRIPTION_NAME+${APP_REPOSITORY}+g'
DEPLOYMENT_NAME 		 = perceptilabs

undeploy: ## remove the helm chart
	helm uninstall --namespace=${NAMESPACE} ${DEPLOYMENT_NAME}

deploy: require-NAMESPACE require-PERCEPTILABS_AZURECR_PWD #secret ## deploy the helm chart
	helm install --namespace=${NAMESPACE} --create-namespace ${DEPLOYMENT_NAME} --set imageCredentials.password=${PERCEPTILABS_AZURECR_PWD} ./chart --debug

remove_namespace:  ## delete the namespace completely
	oc delete namespace ${NAMESPACE} --ignore-not-found

redeploy: remove_namespace deploy  ## delete the namespace and redeploy everything


#######################################################
# Plumbing

require-%:
	@: $(if ${${*}},,$(error You must pass the $* environment variable))


# script-kiddied from https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# .PHONY: clean-cluster clean-namespace clean-storage deploy install-custom-operator instance persistentvolume frontend-route

