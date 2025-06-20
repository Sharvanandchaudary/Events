
locals {

  workspace_name     = basename(abspath(get_terragrunt_dir()))
  secret_global_vars = jsondecode(sops_decrypt_file(find_in_parent_folders("global-sensitive.tfvars.json","${get_parent_terragrunt_dir()}/config/global-sensitive.tfvars.json")))
  secret_env_vars    = try(jsondecode(sops_decrypt_file("${get_terragrunt_dir()}/${local.workspace_name}-sensitive.tfvars.json")), {})

  global_vars        = jsondecode(file(find_in_parent_folders("global.tfvars.json","${get_parent_terragrunt_dir()}/config/global.tfvars.json")))
  env_vars           = try(jsondecode(file("${get_terragrunt_dir()}/${local.workspace_name}.tfvars.json")), {})

  config_map         = merge(local.secret_global_vars,local.secret_env_vars,local.global_vars,local.env_vars)

  compute_common     = lookup(local.global_vars,"compute", {})
  compute_env        = lookup(local.env_vars,"compute", {})
  storage_common     = lookup(local.global_vars,"storage", {})
  storage_env        = lookup(local.env_vars,"storage", {})
  networking_common  = lookup(local.global_vars,"networking", {})
  networking_env     = lookup(local.env_vars,"networking", {})
  settings_common    = lookup(local.global_vars,"settings", {})
  settings_env       = lookup(local.env_vars,"settings", {})
  security_common    = lookup(local.global_vars,"security", {})
  tags_env           = lookup(local.env_vars,"tags", {})
  tags_common        = lookup(local.global_vars,"tags", {})
  security_env       = lookup(local.env_vars,"security", {})
  final_tags         =  join("", [for key, value in local.config_map.tags : "\"${key}\"=\"${value}\"\n"])
  name_prefix        = lookup(local.config_map,"name_prefix", "")
  source_url         = lookup(local.config_map,"source_url", "")
  release            = lookup(local.config_map,"release", "")
  openstack_region   = lookup(local.config_map, "openstack_region", "")
}


generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite"
  contents  = <<EOF
terraform {
  required_version =  "${local.config_map.TF_VERSION}"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.21.0"
    }

    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "2.0.0"
    }

    null = {
      source  = "hashicorp/null"
      version = "3.2.1"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.4.0"
    }

    netapp-ontap = {
      source = "NetApp/netapp-ontap"
      version = "${local.config_map.netapp_version}"
    }
  }
}


provider "openstack" {
  user_name   = "${local.config_map.openstack.username}"
  tenant_id   = "${local.config_map.openstack_project_id}"
  password    = "${local.config_map.openstack.password}"
  auth_url    = "${local.config_map.openstack.openstack_auth_url}"
  region      = "${local.config_map.openstack_region}"
}

provider "aws" {
  region = "${local.config_map.region}"
  access_key = "${local.config_map.aws_key.access}"
  secret_key = "${local.config_map.aws_key.secret}"

  default_tags {
    tags = {
       ${local.final_tags}
    }
  }

}

provider "netapp-ontap" {
  connection_profiles = [
    {
      name           = "${local.config_map.netapp_credentials.profile_name}"
      hostname       = "${local.config_map.netapp_credentials.hostname}"
      username       = "${local.config_map.netapp_credentials.username}"
      password       = "${local.config_map.netapp_credentials.password}"
      validate_certs = false
    },
    {
      name           = "${local.config_map.fsxn_credentials.profile_name}"
      hostname       = "${local.config_map.networking.customer_eni_mapping.haproxy-eni.ip.public_ip}"
#      hostname       = "cidrhost(templatestring(${local.config_map.networking.customer_eni_mapping.haproxy-eni.ip.public_ip},local.config_map.networking.provider_cidr), eni_info.ip.hostnum)"
      username       = "${local.config_map.fsxn_credentials.username}"
      password       = "${local.config_map.fsxn_credentials.password}"
      validate_certs = false
    }
  ]
}

EOF
}

remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite"
  }
  config = {
    bucket         = "cloud30-chambers-terraform-state"
    key            = "cloud30-openstack-chambers/${path_relative_to_include()}/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "cloud30-terraform-locks"

    skip_bucket_ssencryption = true
    skip_bucket_root_access  = true
    skip_bucket_enforced_tls = true
    skip_credentials_validation = true
    skip_bucket_public_access_blocking = true
  }
}

terraform {

  source = "${local.source_url}?ref=${local.release}"

  extra_arguments "disable_input" {
    commands  = get_terraform_commands_that_need_input()
    arguments = ["-input=false"]
  }

  # Force Terraform to keep trying to acquire a lock for up to 5 minutes if someone else already has the lock
  extra_arguments "retry_lock" {
    commands  = get_terraform_commands_that_need_locking()
    arguments = ["-lock-timeout=5m"]
  }

  after_hook "validate_tflint" {
    commands = ["validate"]
    execute = [
      "sh", "-c", <<EOT
        echo "Run tflint for project '${path_relative_to_include()}'..."
        (tflint --module --recursive -f compact --ignore-module=git::https://github.cadence.com/IT/terraform-null-deepmerge.git?ref=v0.1.5)
        error_code=$?
        echo "Run tflint for project '${path_relative_to_include()}'...DONE\n"
        exit $error_code
      EOT
    ]
  }
  # Pass var files to var commands
}

inputs = merge(
  local.global_vars,
  local.env_vars,
  local.compute_common,
  local.compute_env,
  local.storage_common,
  local.storage_env,
  local.networking_common,
  local.networking_env,
  local.secret_global_vars,
  local.secret_env_vars,
  {
    compute_common      = local.compute_common
    compute_env         = local.compute_env
    storage_common      = local.storage_common
    storage_env         = local.storage_env
    networking_common   = local.networking_common
    networking_env      = local.networking_env
    settings_common     = local.settings_common
    settings_env        = local.settings_env
    security_common     = local.security_common
    security_env        = local.security_env
    tags_common         = local.tags_common
    tags_env            = local.tags_env
    env_dir             = path_relative_to_include()
    openstack_auth_url  = local.config_map.openstack.openstack_auth_url
    netapp_profile_name = local.config_map.netapp_credentials.profile_name
    fsxn_profile_name   = local.config_map.fsxn_credentials.profile_name
  }
)


  "source_url": "git::https://github.cadence.com/IT/terraform-openstack-chamber.git//modules/baremetal_only",
  "release": "feature/baremetal-only",
