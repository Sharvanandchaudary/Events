#!/usr/bin/python3

import argparse
import os
import json

# Step 1: Parse CLI arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Dynamic Terraform Config Generator")
    parser.add_argument("--environment", required=True, help="Environment name, e.g., prod or test-3")
    parser.add_argument("--target", required=True, help="Target path, e.g., prod-1 or to01")
    parser.add_argument("--chamber", required=True, help="Chamber name (and filename prefix), e.g., to01")
    parser.add_argument("--nservers", type=int, required=True, help="Number of worker nodes to add")
    return parser.parse_args()

# Step 2: Build and verify chamber path
def get_chamber_path(env, target, chamber):
    path = os.path.join("CustomerVPC", "terraform", "config", "envs", env, env, target, chamber)
    full_path = os.path.abspath(path)

    print(f"🔍 Looking for chamber path: {full_path}")
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"❌ Chamber path does not exist: {full_path}")
    
    print(f"✅ Chamber path found: {full_path}")
    return full_path

# Step 3: Read and validate the tfvars JSON file
def read_chamber_config(chamber_path, chamber):
    tfvars_filename = f"{chamber}.tfvars.json"
    tfvars_path = os.path.join(chamber_path, tfvars_filename)

    if not os.path.exists(tfvars_path):
        raise FileNotFoundError(f"❌ Expected config file not found: {tfvars_path}")

    print(f"📖 Reading config: {tfvars_path}")
    with open(tfvars_path, "r") as f:
        data = json.load(f)

    # Validate essential structure
    if "compute" not in data or \
       "compute_details" not in data["compute"] or \
       "node_details" not in data["compute"]["compute_details"]:
        raise ValueError("❌ Config is missing required structure: compute → compute_details → node_details")

    print(f"✅ Valid config loaded for chamber: {chamber}")
    return tfvars_path, data

# Step 4: Ensure ls01 and haproxy exist
def ensure_static_nodes(data):
    node_details = data["compute"]["compute_details"]["node_details"]

    default_ls01 = {
        "image": "71e5ed26-05bc-4e6e-b107-d1eb3ab65a7f",
        "volume_size": 100,
        "additional_volumes": "ls01_vol"
    }

    default_haproxy = {
        "image": "fe8ba8c6-9c98-4f45-ba96-802ef7a37391",
        "volume_size": 100,
        "additional_volumes": None
    }

    added = []

    if "ls01" not in node_details:
        node_details["ls01"] = default_ls01
        added.append("ls01")

    if "haproxy" not in node_details:
        node_details["haproxy"] = default_haproxy
        added.append("haproxy")

    if added:
        print(f"🛠️ Added missing static node(s): {', '.join(added)}")
    else:
        print("✅ Static nodes 'ls01' and 'haproxy' already exist.")

# Step 5: Add worker nodes and ENI mappings
def add_worker_nodes(data, nservers):
    node_details = data["compute"]["compute_details"]["node_details"]
    eni_mapping = data.get("networking", {}).get("customer_eni_mapping", {})

    existing_workers = [k for k in node_details if k.startswith("wrk") and k[3:].isdigit()]
    existing_nums = sorted([int(k[3:]) for k in existing_workers])
    next_index = max(existing_nums, default=0) + 1

    default_worker = {
        "instance_type": "baremetal",
        "image": "a3b8b3b7-0fe0-402c-9e35-8999dc07e564",
        "volume_size": 100,
        "additional_volumes": None
    }

    hostnum_base = 101 + len(existing_workers)
    added = []

    for i in range(nservers):
        wrk_name = f"wrk{next_index + i:02d}"
        eni_name = f"{wrk_name}-eni"
        hostnum = hostnum_base + i

        node_details[wrk_name] = {
            **default_worker,
            "name": wrk_name,
            "eni_name": eni_name
        }

        eni_mapping[eni_name] = {
            "name": eni_name,
            "subnet": "ComputeSubnet2a",
            "security_groups": [
                "Chm-AccessFromUtlSvr",
                "PrivateSG",
                "CLA-SG",
                "Platform-SG"
            ],
            "ip": {
                "private_ip": "${{cc_chamber_internal_cidr}}",
                "public_ip": "${{cc_chamber_cidr}}",
                "hostnum": hostnum
            }
        }

        added.append(wrk_name)

    data["networking"]["customer_eni_mapping"] = eni_mapping

    if added:
        print(f"🚀 Added worker nodes: {', '.join(added)}")
    else:
        print("⚠️ No new worker nodes added.")

# Step 6: Write updated config back to file
def write_updated_config(tfvars_path, data):
    with open(tfvars_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Config successfully updated and written to: {tfvars_path}")

# Main execution
def main():
    args = parse_args()
    chamber_path = get_chamber_path(args.environment, args.target, args.chamber)
    tfvars_path, config_data = read_chamber_config(chamber_path, args.chamber)

    ensure_static_nodes(config_data)
    add_worker_nodes(config_data, args.nservers)
    write_updated_config(tfvars_path, config_data)

if __name__ == "__main__":
    main()
