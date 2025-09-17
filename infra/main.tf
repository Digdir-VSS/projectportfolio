terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.52.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "intactivity" {
    name     = var.resource_group_name
    location = var.location
}

resource "azurerm_log_analytics_workspace" "intactivity" {
  name                = "logintactivity"
  location            = azurerm_resource_group.intactivity.location
  resource_group_name = azurerm_resource_group.intactivity.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "intactivity" {
    name               = var.container_environment
    location           = azurerm_resource_group.intactivity.location
    resource_group_name= azurerm_resource_group.intactivity.name
    log_analytics_workspace_id = azurerm_log_analytics_workspace.intactivity.id
    
}

resource "azurerm_container_registry" "intactivity" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.intactivity.name
  location            = azurerm_resource_group.intactivity.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_container_app" "intactivity" {
  name                         = "int-activity-app"
  container_app_environment_id = azurerm_container_app_environment.intactivity.id
  resource_group_name          = azurerm_resource_group.intactivity.name
  revision_mode                = "Single"

  template {
    container {
      name   = "internationalactivitycontainerapp"
      image  = "mcr.microsoft.com/k8se/quickstart:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 80
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server   = azurerm_container_registry.intactivity.login_server
    identity = "System"
  }

  identity {
    type = "SystemAssigned"
  }
}
