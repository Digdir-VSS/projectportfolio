variable "location" { default = "norwayeast" }
variable "resource_group_name" { default = "project-portfolio-resource" }
variable "aca_name" { default = "project-portfolio-app" }
variable "dev_aca_name" { default = "project-portfolio-dev-app" }
variable "acr_name" { default = "projectportfolioregistry" }
variable "container_image" { default = "myapp:latest" }
variable "container_environment" { default = "Project-Portfolio-Environment" }
variable "log_analytics_workspace" { default = "logprojectportfolio" }