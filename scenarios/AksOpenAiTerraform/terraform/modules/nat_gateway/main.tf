locals {
  zones = ["1"]
}

resource "azurerm_public_ip" "nat_gategay_public_ip" {
  name                = "${var.name}PublicIp"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  zones               = local.zones
}

resource "azurerm_nat_gateway" "nat_gateway" {
  name                    = var.name
  location                = var.location
  resource_group_name     = var.resource_group_name
  idle_timeout_in_minutes = 4
  zones                   = local.zones
}

resource "azurerm_nat_gateway_public_ip_association" "nat_gategay_public_ip_association" {
  nat_gateway_id       = azurerm_nat_gateway.nat_gateway.id
  public_ip_address_id = azurerm_public_ip.nat_gategay_public_ip.id
}

resource "azurerm_subnet_nat_gateway_association" "nat-avd-sessionhosts" {
  for_each       = var.subnet_ids
  subnet_id      = each.value
  nat_gateway_id = azurerm_nat_gateway.nat_gateway.id
}