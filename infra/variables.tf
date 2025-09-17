variable "location" { default = "norwayeast" }
variable "resource_group_name" { default = "int-activity-resource" }
variable "aca_name" { default = "int-activity-app" }
variable "acr_name" { default = "intactivitydigdirdockerregistry" }
variable "container_image" { default = "myapp:latest" }
variable "container_environment" {default = "Int-Activity-Environment"}