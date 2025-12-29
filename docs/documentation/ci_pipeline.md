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

### 2. Docker Build (Heavy)
This job verifies that the application can be containerized successfully.

- **Dependency**: Runs only if `Quality Control` passes.
- **Optimization**: Utilizes GitHub Actions Cache to cache Docker layers, significantly reducing build times for subsequent runs.
- **Buildx**: Uses Docker Buildx for advanced build capabilities.
- **No Push**: Currently, the image is built to verify correctness but is not pushed to a registry.

### 3. Kubernetes Validation (Static Analysis)
This job ensures that the Kubernetes manifests are syntactically correct.

- **Parallel Execution**: Runs in parallel with Quality Control as it doesn't depend on code quality, only on manifest syntax.
- **Tool**: Uses `kubeval` to validate the files against Kubernetes schemas.
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
