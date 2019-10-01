current_dir = $(shell pwd)

PROJECT = ml_mining

# Including ci Makefile
CI_REPOSITORY ?= https://github.com/src-d/ci.git
CI_BRANCH ?= v1
CI_PATH ?= .ci
MAKEFILE := $(CI_PATH)/Makefile.main
$(MAKEFILE):
	git clone --quiet --depth 1 -b $(CI_BRANCH) $(CI_REPOSITORY) $(CI_PATH);
-include $(MAKEFILE)

.PHONY: check
check:
	! (grep -R /tmp sourced/ml/mining/tests)
	flake8 --count
	pylint sourced

.PHONY: test
test:
	python3 -m unittest discover

.PHONY: bblfsh-start
bblfsh-start:
	! docker ps | grep bblfshd # bblfsh server should not be running already
	docker run -d --name ml_mining_bblfshd --privileged -p 9432\:9432 bblfsh/bblfshd\:v2.14.0
	docker exec -it ml_mining_bblfshd bblfshctl driver install python bblfsh/python-driver\:v2.10.0
