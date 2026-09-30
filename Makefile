# Temporary compatibility shim for ADR-0024. Taskfile.yml owns every implementation.
# Remove this file after active descendants no longer need Make compatibility.

.PHONY: help setup format lint test test-unit test-integration coverage build run \
        security-scan sbom clean doctor fleet-audit

FILE ?=
FLEET_WORKSPACE_ROOT ?= ..
export FILE FLEET_WORKSPACE_ROOT

help:
	@task help

setup test test-unit test-integration coverage build run security-scan sbom clean doctor:
	@task "$@"

format lint:
	@task "$@" FILE="$${FILE}"

fleet-audit:
	@task fleet-audit FLEET_WORKSPACE_ROOT="$${FLEET_WORKSPACE_ROOT}"
