#!/bin/bash
set -e

echo "Applying Configuration..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

echo "Applying Infrastructure..."
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/rabbitmq.yaml
kubectl apply -f k8s/chroma.yaml

echo "Waiting for Infrastructure to be ready (optional, but good practice)..."
# In a real script we might wait here, but for now we proceed.

echo "Applying Services..."
kubectl apply -f k8s/service-api.yaml
kubectl apply -f k8s/service-grpc.yaml

echo "Applying Application Deployments..."
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/deployment-worker.yaml
kubectl apply -f k8s/deployment-mcp.yaml
kubectl apply -f k8s/deployment-market-data.yaml
kubectl apply -f k8s/deployment-order-service.yaml

echo "Done! Access the API at http://localhost:30000 (if using NodePort on Minikube) or via 'minikube service api'."
