variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
  default     = "rg-cryptoflow-prod"
}

variable "location" {
  description = "The Azure region to deploy resources"
  type        = string
  default     = "East US"
}

variable "cluster_name" {
  description = "The name of the AKS cluster"
  type        = string
  default     = "aks-cryptoflow-prod"
}
