resource "random_pet" "rg_name" {
  prefix = "rg"
}

resource "azurerm_resource_group" "rg" {
  name     = "TFrg${random_pet.rg_name.id}"
  location = var.location

  tags = {
    Environment = "Dev Pipeline"
    Team        = "Data Engineering"
  }
}

# Random String for unique naming
resource "random_string" "name" {
  length  = 8
  special = false
  upper   = false
  lower   = true
  numeric = false
}

resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = "TFpsql-source-db"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  version                = "13"
  administrator_login    = "psqladmin"
  administrator_password = "StrongPassword123!" # Use variables/KeyVault in prod
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
}

resource "azurerm_postgresql_flexible_server_database" "default" {
  name      = "TFsource_data"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

resource "azurerm_storage_account" "sa" {
  name                     = "TFSa${random_string.name.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  account_kind             = "StorageV2"
  min_tls_version          = "TLS1_2"
  is_hns_enabled           = true # Critical: Enables Hierarchical Namespace (ADLS Gen2)
}

resource "azurerm_storage_data_lake_gen2_filesystem" "data_lake" {
  name               = "TFdata_lake${random_string.name.result}"
  storage_account_id = azurerm_storage_account.sa.id
}

resource "azurerm_eventhub_namespace" "evhn" {
  name                = "TFevh-streaming-${random_string.name.result}"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
  capacity            = 1
}

resource "azurerm_eventhub" "evh" {
  name              = "TFeventhub-${random_string.name.result}"
  namespace_id      = azurerm_eventhub_namespace.evhn.id
  partition_count   = 2
  message_retention = 1
}

resource "azurerm_synapse_workspace" "workspace" {
  name                                 = "TFworkspace${random_string.name.result}"
  resource_group_name                  = azurerm_resource_group.rg.name
  location                             = azurerm_resource_group.rg.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.data_lake.id
  sql_administrator_login              = "sqladmin"
  sql_administrator_login_password     = "P@ssw0rd1234!"

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_account" "synapse_store" {
  name                     = "sasynapseprimary"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  is_hns_enabled           = true
}

resource "azurerm_storage_data_lake_gen2_filesystem" "synapse_fs" {
  name               = "synapse-system"
  storage_account_id = azurerm_storage_account.synapse_store.id
}

resource "azurerm_synapse_workspace" "synapse" {
  name                                 = "synapse-ws-prod"
  resource_group_name                  = azurerm_resource_group.rg.name
  location                             = azurerm_resource_group.rg.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.synapse_fs.id
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = "StrongPassword123!"
}

# Module 3: Data Warehouse (Dedicated SQL Pool)
resource "azurerm_synapse_sql_pool" "dw" {
  name                 = "syndp_sales_dw"
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  sku_name             = "DW100c" # Smallest production SKU
  create_mode          = "Default"
}

# Module 5: Batch Processing (Spark Pool)
resource "azurerm_synapse_spark_pool" "spark" {
  name                 = "sparkpoolsmall"
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  node_size_family     = "MemoryOptimized"
  node_size            = "Small"
  auto_scale {
    max_node_count = 3
    min_node_count = 1
  }
}
