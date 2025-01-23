data "azurerm_client_config" "current" {
}

resource "random_string" "rg_suffix" {
  length  = 6
  special = false
  lower   = false
  upper   = false
  numeric = true
}

resource "random_string" "storage_account_suffix" {
  length  = 8
  special = false
  lower   = true
  upper   = false
  numeric = false
}

locals {
  tenant_id       = data.azurerm_client_config.current.tenant_id
  subscription_id = data.azurerm_client_config.current.subscription_id
  random_id       = random_string.rg_suffix.result

  namespace            = "magic8ball"
  service_account_name = "magic8ball-sa"
}

###############################################################################
# Resource Group
###############################################################################
resource "azurerm_resource_group" "rg" {
  name     = "${var.resource_group_name_prefix}-${local.random_id}-rg"
  location = var.location

  lifecycle {
    ignore_changes = [tags]
  }
}

###############################################################################
# Application
###############################################################################
module "openai" {
  source              = "./modules/openai"
  name                = "OpenAi-${local.random_id}"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  sku_name = "S0"
  deployments = [
    {
      name = "gpt-4"
      model = {
        name    = "gpt-4"
        version = "turbo-2024-04-09"
      }
    }
  ]
  custom_subdomain_name = var.openai_subdomain

  log_analytics_workspace_id = module.log_analytics_workspace.id
}

module "aks_cluster" {
  source              = "./modules/aks"
  name                = "AksCluster"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  resource_group_id   = azurerm_resource_group.rg.id
  tenant_id           = local.tenant_id

  kubernetes_version       = var.kubernetes_version
  sku_tier                 = "Free"
  system_node_pool_vm_size = "Standard_D8ds_v5"
  user_node_pool_vm_size   = "Standard_D8ds_v5"

  system_node_pool_subnet_id = module.virtual_network.subnet_ids["SystemSubnet"]
  user_node_pool_subnet_id   = module.virtual_network.subnet_ids["UserSubnet"]
  pod_subnet_id              = module.virtual_network.subnet_ids["PodSubnet"]

  log_analytics_workspace_id = module.log_analytics_workspace.id

  depends_on = [module.nat_gateway]
}

module "container_registry" {
  source              = "./modules/container_registry"
  name                = "acr${local.random_id}"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  sku = "Premium"

  log_analytics_workspace_id = module.log_analytics_workspace.id
}

module "storage_account" {
  source              = "./modules/storage_account"
  name                = "boot${random_string.storage_account_suffix.result}"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
}

module "key_vault" {
  source              = "./modules/key_vault"
  name                = "KeyVault-${local.random_id}"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  tenant_id = local.tenant_id
  sku_name  = "standard"

  log_analytics_workspace_id = module.log_analytics_workspace.id
}

module "log_analytics_workspace" {
  source              = "./modules/log_analytics"
  name                = "Workspace"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  sku               = "PerGB2018"
  retention_in_days = 30
}

###############################################################################
# Networking
###############################################################################
module "virtual_network" {
  source              = "./modules/virtual_network"
  name                = "AksVNet"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  address_space = ["10.0.0.0/8"]
  subnets = [
    {
      name : "VmSubnet"
      address_prefixes : ["10.243.1.0/24"]
    },
    {
      name : "AzureBastionSubnet"
      address_prefixes : ["10.243.2.0/24"]
    },
    {
      name : "SystemSubnet"
      address_prefixes : ["10.240.0.0/16"]
    },
    {
      name : "UserSubnet"
      address_prefixes : ["10.241.0.0/16"]
    },
    {
      name : "PodSubnet"
      address_prefixes : ["10.242.0.0/16"]
      delegation = {
        name = "delegation"
        service_delegation = {
          name    = "Microsoft.ContainerService/managedClusters"
          actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
        }
      }
    },
  ]

  log_analytics_workspace_id = module.log_analytics_workspace.id
}

module "nat_gateway" {
  source              = "./modules/nat_gateway"
  name                = "NatGateway"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  subnet_ids = module.virtual_network.subnet_ids
}

module "bastion_host" {
  source              = "./modules/bastion_host"
  name                = "BastionHost"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  subnet_id = module.virtual_network.subnet_ids["AzureBastionSubnet"]

  log_analytics_workspace_id = module.log_analytics_workspace.id
}

###############################################################################
# Private DNS Zones
###############################################################################
module "acr_private_dns_zone" {
  source              = "./modules/dns"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  name                           = "privatelink.azurecr.io"
  subresource_name               = "account"
  private_connection_resource_id = module.openai.id
  virtual_network_id             = module.virtual_network.id
  subnet_id                      = module.virtual_network.subnet_ids["VmSubnet"]
}

module "openai_private_dns_zone" {
  source              = "./modules/dns"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  name                           = "privatelink.openai.azure.com"
  subresource_name               = "registry"
  private_connection_resource_id = module.container_registry.id
  virtual_network_id             = module.virtual_network.id
  subnet_id                      = module.virtual_network.subnet_ids["VmSubnet"]
}

module "key_vault_private_dns_zone" {
  source              = "./modules/dns"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  name                           = "privatelink.vaultcore.azure.net"
  subresource_name               = "vault"
  private_connection_resource_id = module.key_vault.id
  virtual_network_id             = module.virtual_network.id
  subnet_id                      = module.virtual_network.subnet_ids["VmSubnet"]
}

module "blob_private_dns_zone" {
  source              = "./modules/dns"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  name                           = "privatelink.blob.core.windows.net"
  subresource_name               = "blob"
  private_connection_resource_id = module.storage_account.id
  virtual_network_id             = module.virtual_network.id
  subnet_id                      = module.virtual_network.subnet_ids["VmSubnet"]
}

###############################################################################
# Identities/Roles
###############################################################################
resource "azurerm_user_assigned_identity" "aks_workload_identity" {
  name                = "WorkloadManagedIdentity"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
}

resource "azurerm_federated_identity_credential" "federated_identity_credential" {
  name                = "${title(local.namespace)}FederatedIdentity"
  resource_group_name = azurerm_resource_group.rg.name

  audience  = ["api://AzureADTokenExchange"]
  issuer    = module.aks_cluster.oidc_issuer_url
  parent_id = azurerm_user_assigned_identity.aks_workload_identity.id
  subject   = "system:serviceaccount:${local.namespace}:${local.service_account_name}"
}

resource "azurerm_role_assignment" "cognitive_services_user_assignment" {
  role_definition_name = "Cognitive Services User"
  scope                = module.openai.id
  principal_id         = azurerm_user_assigned_identity.aks_workload_identity.principal_id
}

resource "azurerm_role_assignment" "network_contributor_assignment" {
  role_definition_name = "Network Contributor"
  scope                = azurerm_resource_group.rg.id
  principal_id         = module.aks_cluster.aks_identity_principal_id
}

resource "azurerm_role_assignment" "acr_pull_assignment" {
  role_definition_name = "AcrPull"
  scope                = module.container_registry.id
  principal_id         = module.aks_cluster.kubelet_identity_object_id
}
