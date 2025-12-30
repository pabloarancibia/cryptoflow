# GitHub Actions CI Pipeline

This document describes the Continuous Integration (CI) pipeline implemented for CryptoFlow using GitHub Actions.

## Overview

The pipeline is designed to ensure code quality, build stability, and configuration validity on every push and pull request to the `main` branch.

## Pipeline Architecture

The pipeline consists of three main jobs that run on `ubuntu-latest` runners.

--8<-- "docs/documentation/diagrams/ci/ci_pipeline_flow.mmd"

## Jobs Description

### 1. Quality Control (Fast)
This job is the first line of defense. It focuses on code correctness and quality.

- **Fast Feedback**: Designed to fail fast if there are syntax errors or test failures.
- **Linting**: Uses `ruff` for extremely fast Python linting.
- **Testing**: Runs unit tests using `pytest` located in `tests/unit_tests`.

### 2. Docker Validation (Linting)
This job ensures that the Dockerfile follows best practices and is syntactically correct.

- **Dependency**: Runs only if `Quality Control` passes.
- **Tool**: Uses `hadolint` for static analysis of the Dockerfile.
- **Mock Build**: Due to GitHub Free Tier disk limitations (~14GB), the full Docker build is mocked in the CI environment. The pipeline validates the *definition* rather than the *artifact*.
- **Self-Hosted Ready**: The pipeline structure is consistent with a full build, allowing for easy enabling of the build step on self-hosted runners.

### 3. Kubernetes Validation (Static Analysis)
This job ensures that the Kubernetes manifests are syntactically correct.

- **Parallel Execution**: Runs in parallel with Quality Control as it doesn't depend on code quality, only on manifest syntax.
- **Tool**: Uses `kubeconform` to validate the files (a modern replacement for `kubeval`).
- **Scope**: Checks all `.yaml` files in the `k8s/` directory.

## Configuration

The pipeline is defined in `.github/workflows/ci.yml`.

### Triggers
```yaml
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
```

### Environment
- **Python**: 3.11
- **OS**: Ubuntu Latest
