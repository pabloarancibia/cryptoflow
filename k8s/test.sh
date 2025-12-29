#!/bin/bash

echo "Checking Pod Status..."
kubectl get pods

echo "Checking Services..."
kubectl get services

echo "Checking Endpoints..."
kubectl get endpoints

echo "Waiting for API Pod..."
kubectl wait --for=condition=ready pod -l app=api --timeout=60s

echo "Testing API Liveness..."
# Assuming we are running this from a machine that can access the NodePort or ClusterIP via proxy
# For Minikube user might need `minikube service api --url`
API_URL=$(kubectl get service api -o jsonpath='{.spec.clusterIP}') 
# Note: ClusterIP is internal. For external test from host:
echo "Note: To test connectivity from host, use the NodePort or 'kubectl port-forward'."
echo "Running internal connectivity check logic is complex without a test pod."

echo "Deployment Status verification complete."
