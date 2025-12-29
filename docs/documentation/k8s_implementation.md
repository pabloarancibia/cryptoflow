# Kubernetes Implementation

This guide explains how to deploy the CryptoFlow application on a local Kubernetes cluster (Minikube or Kind).

## Overview

The deployment consists of:
- **Configuration**: ConfigMaps and Secrets.
- **Infrastructure**: PostgreSQL, Redis, RabbitMQ, ChromaDB (running as simple Deployments).
- **Application Services**: API, Worker, MCP, Market Data (gRPC), Order Service (gRPC).

## Directory Structure

The manifests are located in the `k8s/` directory:

```text
k8s/
├── apply.sh               # Script to apply all manifests
├── test.sh                # Script to verify deployment
├── configmap.yaml         # Configuration
├── secrets.yaml           # Secrets (base64 encoded)
├── postgres.yaml          # Database
├── redis.yaml             # Cache
├── rabbitmq.yaml          # Message Broker
├── chroma.yaml            # Vector Store
├── deployment-api.yaml    # REST API
├── deployment-worker.yaml # Celery Worker
├── deployment-mcp.yaml    # MCP Server
├── deployment-*.yaml      # gRPC Services
└── service-*.yaml         # K8s Services
```

## How to Deploy

1. **Start Minikube**:
   ```bash
   minikube start
   ```

2. **Load Image** (if using local image):
   ```bash
   minikube image load cryptoflow:latest
   ```

3. **Run Apply Script**:
   ```bash
   bash k8s/apply.sh
   ```

## Verification

Run the test script to check the status of pods and services:

```bash
bash k8s/test.sh
```

## Accessing the API

The API service is exposed via **NodePort**. You can access it via:

```bash
minikube service api
```

Or directly at `http://<minikube-ip>:30000`.
