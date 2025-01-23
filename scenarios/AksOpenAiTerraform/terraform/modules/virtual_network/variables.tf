variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "address_space" {
  type = list(string)
}

variable "subnets" {
  description = "Subnets configuration"
  type = list(object({
    name             = string
    address_prefixes = list(string)
    delegation = optional(object({
      name = string,
      service_delegation = object({
        name    = string
        actions = list(string)
      })
    }))
  }))
}

variable "log_analytics_workspace_id" {
  type = string
}