variable "name" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "resource_group_id" {
  type = string
}

variable "location" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "kubernetes_version" {
  type = string
}

variable "sku_tier" {
  type = string
}

variable "system_node_pool_vm_size" {
  type = string
}

variable "user_node_pool_vm_size" {
  type = string
}

variable "log_analytics_workspace_id" {
  type = string
}

variable "user_node_pool_subnet_id" {
  type = string
}

variable "system_node_pool_subnet_id" {
  type = string
}

variable "pod_subnet_id" {
  type = string
}