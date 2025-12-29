# Infrastructure as Code (IaC) with Terraform

## Introduction to IaC
Infrastructure as Code (IaC) is the managing and provisioning of computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools.

## Why Terraform?
Terraform is an open-source infrastructure as code software tool that provides a consistent CLI workflow to manage hundreds of cloud services. Terraform codifies cloud APIs into declarative configuration files.

### Key Concepts
- **Providers:** Plugins that implement resource types for a specific service (e.g., `azurerm` for Azure).
- **Resources:** The components of your infrastructure (virtual machines, security groups, etc.).
- **State:** Terraform keeps track of your real infrastructure in a state file, which acts as a source of truth for your environment.

## Azure Architecture Decisions

### Resource Group
A logical container into which Azure resources like web apps, databases, and storage accounts are deployed and managed. We use a dedicated resource group `rg-cryptoflow-prod` to isolate our environment.

### Azure Container Registry (ACR)
Managed, private Docker registry service based on the open-source Docker Registry 2.0. We chose the **Basic** tier as it provides a cost-effective entry point for development and light production scenarios.

### Azure Kubernetes Service (AKS)
Managed Kubernetes service that simplifies deploying, managing, and operations of Kubernetes.
- **Node Pool:** We use a `Standard_B2s` size for the node pool. B-series are burstable VMs that are cost-effective for workloads that do not need continuous full CPU performance.
- **Identity:** System Assigned Managed Identity is used to allow the AKS cluster to interact with other Azure resources (like ACR) securely without managing credentials manually.

## Security Considerations
- **Tags:** All resources are tagged (`Project`, `Environment`) for better governance and cost tracking.
- **RBAC:** We automatically assign the `AcrPull` role to the AKS kubelet identity, ensuring the cluster can pull images from the registry without exposing administrative credentials.
