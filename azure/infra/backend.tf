terraform {
  backend "azurerm" {
    resource_group_name  = "<TFSTATE_RG>"
    storage_account_name = "<TFSTATE_STORAGE>"
    container_name       = "<TFSTATE_CONTAINER>" # vd: tfstate
    key                  = "azure-mlops/terraform.tfstate"
  }
}
