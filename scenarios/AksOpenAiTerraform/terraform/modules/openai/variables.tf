variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "sku_name" {
  type = string
}

variable "custom_subdomain_name" {
  type = string
}

variable "deployments" {
  type = list(object({
    name = string
    model = object({
      name    = string
      version = string
    })
  }))
}

variable "log_analytics_workspace_id" {
  type = string
}