SHELL := /bin/bash
ENV ?= dev

.PHONY: init plan apply destroy fmt validate

init:
	cd envs/$(ENV) && terraform init

plan:
	cd envs/$(ENV) && terraform plan -out=tfplan

apply:
	cd envs/$(ENV) && terraform apply -auto-approve tfplan

destroy:
	cd envs/$(ENV) && terraform destroy

fmt:
	cd envs/$(ENV) && terraform fmt -recursive

validate:
	cd envs/$(ENV) && terraform validate
