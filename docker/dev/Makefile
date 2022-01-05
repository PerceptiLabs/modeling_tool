ROOT=$(shell git rev-parse --show-toplevel)

rygg_dev: require-ROOT ## make the developmet rygg image
	cd ${ROOT}/rygg && \
	docker build . --file Dockerfile-dev --tag=dev/rygg:latest

kernel_dev: require-ROOT ## make the developmet kernel image
	cd ${ROOT}/backend && \
	docker build . --file Dockerfile-dev --tag=dev/kernel:latest

frontend_dev: require-ROOT ## make the developmet frontend image
	cd ${ROOT}/frontend && \
	docker build . --file Dockerfile-dev --tag=dev/frontend:latest

.env:
	echo PL_ROOT=${ROOT} > .env

dev_all: rygg_dev kernel_dev frontend_dev .env ## All dev images and env file


#######################################################
# Plumbing

require-%:
	@: $(if ${${*}},,$(error You must pass the $* environment variable))


# script-kiddied from https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

