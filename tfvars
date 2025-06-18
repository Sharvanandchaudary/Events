{
  "tags": {
    "hyperscaler": "rhops"
  },
  "environment": "test-2",
  "name_prefix": "to01",
  "openstack_project_id": "59c2d928ef6046069a0175d74dc3dc23",
  "openstack_project_name": "cc-test-oa-chm01-prj",
  "release" : "main",
  "settings": {
    "hybrid_deployment": false,
    "aws_chamber_tfstate_key": "cloud30-chambers/config/envs/non-prod/dev/dc01/terraform.tfstate",
    "cc_chamber_json_s3_location": "s3://cadencecloud-mirrors-eu-central-1/projects/orchestrator/c30-cust/to01/awscbtb02slurm01/to01.json",
    "cc_hub_tfstate_key": "cloud30-openstack-shr/config/envs/non-prod/qa/test-2/to00/terraform.tfstate",
    "drm_cidr": "10.3.120.0/23",
    "aws_admin_cidr": "10.3.64.0/27",
    "aws_chamber_cidr": "10.3.66.0/23",
    "openstack_mgmt_ip": "10.107.178.0/24"
  },
  "compute": {
    "compute_details": {
      "node_details": {
        "ls01": {
          "image": "71e5ed26-05bc-4e6e-b107-d1eb3ab65a7f",
          "volume_size": 100,
          "additional_volumes" : "ls01_vol"
        },
        "haproxy": {
          "image": "fe8ba8c6-9c98-4f45-ba96-802ef7a37391",
          "volume_size": 100,
          "additional_volumes" : null
        },
        "wrk01": {
          "name": "wrk01",
          "instance_type": "baremetal",
          "image": "a3b8b3b7-0fe0-402c-9e35-8999dc07e564",
          "volume_size": 100,
          "additional_volumes": null,
          "eni_name": "wrk01-eni"
        }
      }
    }
  },
  "storage": {
    "volume_type": "netapp_iscsi_enc",
    "ebs_volume_details": {
      "ls01_vol": {
        "scratch": {
          "disk": "tmp",
          "volume_size": 100,
          "device": "/dev/vdb"
        }
      }
    }
  },
  "networking": {
    "provider_vlan" : "1168",
    "provider_cidr" : "10.107.168.0/23",
    "baremetal" : {
      "network_id": "5c79a1a8-b294-4435-a2e6-ef1b992735d3",
      "subnet_id" : "c83e54b1-822e-4931-ac73-b731d1f6c966"
    },
    "customer_vpc": {
      "cidr_block": "10.154.180.0/23"
    },
    "customer_eni_mapping": {
      "haproxy-eni": {
        "ip": {
          "public_ip": "10.107.168.52",
          "hostnum": 52
        }
      },
      "wrk01-eni": {
        "name": "wrk01-eni",
        "subnet": "ComputeSubnet2a",
        "security_groups": [
          "Chm-AccessFromUtlSvr",
          "PrivateSG",
          "CLA-SG",
          "Platform-SG"
        ],
        "ip": {
          "private_ip" : "$${cc_chamber_internal_cidr}",
          "public_ip"  : "$${cc_chamber_cidr}",
          "hostnum" : 101
        }
      }
    }
  }
}
