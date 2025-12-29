# Terraform Infrastructure Implementation

## Overview
This document describes the Terraform implementation for provisioning the Azure infrastructure required for CryptoFlow. The infrastructure includes a Resource Group, an Azure Container Registry (ACR), and an Azure Kubernetes Service (AKS) cluster.

## Architecture
The infrastructure is designed to be cost-effective for development and testing purposes, utilizing a single node AKS cluster with a standard burstable VM size.

![Azure Infrastructure Diagram](diagrams/infra/azure_infrastructure.mmd)

## Prerequisites
- [Terraform](https://www.terraform.io/downloads.html) installed (v1.0+).
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and configured.
- Active Azure subscription.

## Configuration Files
The Terraform configuration is located in the `infra/` directory and consists of the following files:

- `main.tf`: Contains the main resource definitions (Resource Group, ACR, AKS).
- `variables.tf`: Defines input variables for customization (Location, Resource Group Name, Cluster Name).
- `outputs.tf`: Defines the outputs (Kube Config, ACR Login Server).

## Deployment Steps

1.  **Initialize Terraform:**
    Navigate to the `infra/` directory and run:
    ```bash
    terraform init
    ```

2.  **Review the Plan:**
    See what resources will be created:
    ```bash
    terraform plan
    ```

3.  **Apply the Configuration:**
    Provision the resources:
    ```bash
    terraform apply
    ```
    Type `yes` when prompted to confirm.

4.  **Connect to the Cluster:**
    After successful application, you can retrieve the kubeconfig:
    ```bash
    terraform output -raw kube_config > ~/.kube/config
    ```

5.  **Push Images to ACR:**
    Get the ACR login server name:
    ```bash
    terraform output -raw acr_login_server
    ```
    Login and push your Docker images.

## Clean Up
To destroy the infrastructure and stop incurring costs:
```bash
terraform destroy
```
