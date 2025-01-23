resource "azurerm_user_assigned_identity" "aks_identity" {
  name                = "${var.name}Identity"
  resource_group_name = var.resource_group_name
  location            = var.location
}

resource "azurerm_kubernetes_cluster" "aks_cluster" {
  name                             = var.name
  location                         = var.location
  resource_group_name              = var.resource_group_name
  kubernetes_version               = var.kubernetes_version
  dns_prefix                       = lower(var.name)
  private_cluster_enabled          = false
  automatic_upgrade_channel        = "stable"
  sku_tier                         = var.sku_tier
  workload_identity_enabled        = true
  oidc_issuer_enabled              = true
  open_service_mesh_enabled        = true
  image_cleaner_enabled            = true
  image_cleaner_interval_hours     = 72
  azure_policy_enabled             = true
  http_application_routing_enabled = false

  default_node_pool {
    name           = "system"
    node_count     = 1
    vm_size        = var.system_node_pool_vm_size
    vnet_subnet_id = var.system_node_pool_subnet_id
    pod_subnet_id  = var.pod_subnet_id
    zones          = ["1", "2", "3"]
    max_pods       = 50
    os_disk_type   = "Ephemeral"

    upgrade_settings {
      drain_timeout_in_minutes      = 0
      max_surge                     = "10%"
      node_soak_duration_in_minutes = 0
    }
  }

  identity {
    type         = "UserAssigned"
    identity_ids = tolist([azurerm_user_assigned_identity.aks_identity.id])
  }

  network_profile {
    dns_service_ip = "10.2.0.10"
    network_plugin = "azure"
    outbound_type  = "userAssignedNATGateway"
    service_cidr   = "10.2.0.0/24"
  }

  oms_agent {
    msi_auth_for_monitoring_enabled = true
    log_analytics_workspace_id      = var.log_analytics_workspace_id
  }

  azure_active_directory_role_based_access_control {
    tenant_id          = var.tenant_id
    azure_rbac_enabled = true
  }

  workload_autoscaler_profile {
    keda_enabled                    = true
    vertical_pod_autoscaler_enabled = true
  }

  lifecycle {
    ignore_changes = [microsoft_defender]
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "node_pool" {
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks_cluster.id
  name                  = "user"
  vm_size               = var.user_node_pool_vm_size
  mode                  = "User"
  zones                 = ["1", "2", "3"]
  vnet_subnet_id        = var.user_node_pool_subnet_id
  pod_subnet_id         = var.pod_subnet_id
  orchestrator_version  = var.kubernetes_version
  max_pods              = 50
  os_disk_type          = "Ephemeral"
  os_type               = "Linux"
  priority              = "Regular"
}

resource "azurerm_monitor_diagnostic_setting" "settings" {
  name                       = "AksDiagnosticsSettings"
  target_resource_id         = azurerm_kubernetes_cluster.aks_cluster.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "kube-apiserver"
  }

  enabled_log {
    category = "kube-audit"
  }

  enabled_log {
    category = "kube-audit-admin"
  }

  enabled_log {
    category = "kube-controller-manager"
  }

  enabled_log {
    category = "kube-scheduler"
  }

  enabled_log {
    category = "cluster-autoscaler"
  }

  enabled_log {
    category = "guard"
  }

  metric {
    category = "AllMetrics"
  }
}