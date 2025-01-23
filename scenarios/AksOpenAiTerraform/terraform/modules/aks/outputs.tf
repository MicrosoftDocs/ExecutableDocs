output "name" {
  value = azurerm_kubernetes_cluster.aks_cluster.name
}

output "id" {
  value = azurerm_kubernetes_cluster.aks_cluster.id
}

output "aks_identity_principal_id" {
  value = azurerm_user_assigned_identity.aks_identity.principal_id
}

output "kubelet_identity_object_id" {
  value = azurerm_kubernetes_cluster.aks_cluster.kubelet_identity.0.object_id
}

output "oidc_issuer_url" {
  value = azurerm_kubernetes_cluster.aks_cluster.oidc_issuer_url
}