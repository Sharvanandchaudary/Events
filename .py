#!/usr/bin/python3




def main():
    ## use argparse to take command line options
    ## CLIOPTONS - environment, target, chamber, nservers

    ## {environment}/{target}/{chamber}
    ## {prod}/{prod-1}/oa01


    ## check the file exists - Example oa01 file exists in the path (use os library or path)

    ## make sure add_chamber, {chamber}-sensiive.tfvars.json & {chamber}.tfvars.json

    ## Read the file - {chamber}.tfvars.json

    ## validate compute -> compute_details -> node_details exists

    ## check ls01 exists -> if not add the config (append the valid json into an list)
    ## check haproxy exists -> if not add the config (append the valid json into an list)
    ## get all the keys which match the wrk<number>,
    ## when no keys exists - start adding workers from wrk01, wrk02 ....wrkn
    ## when keys exists until wrk03 - start adding workers from wrk04, wrk05 ....wrkn

    ## write back the json file after validating and printing the nodes being added to the config
    pass


    

if __name__ == "__main__":
    main()
===============================================================================================================================================
#!/usr/bin/python3

import argparse
import os

# Step 1: Parse CLI arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Dynamic Terraform Config Generator")
    parser.add_argument("--environment", required=True, help="Environment name, e.g., prod")
    parser.add_argument("--target", required=True, help="Target path, e.g., prod-1")
    parser.add_argument("--chamber", required=True, help="Chamber name, e.g., oa01")
    parser.add_argument("--nservers", type=int, required=True, help="Number of worker nodes to add")
    return parser.parse_args()

# Step 2: Build and verify path
def get_chamber_path(env, target, chamber):
    base_path = os.path.join(
        "CustomerVPC", "terraform", "config", "envs", env, target, chamber
    )
    full_path = os.path.abspath(base_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Chamber path does not exist: {full_path}")
    
    print(f"✅ Chamber path found: {full_path}")
    return full_path

# Main entry
def main():
    args = parse_args()
    chamber_path = get_chamber_path(args.environment, args.target, args.chamber)

if __name__ == "__main__":
    main()
=============================================================
#!/usr/bin/python3

import argparse
import os

# Step 1: Parse CLI arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Dynamic Terraform Config Generator")
    parser.add_argument("--environment", required=True, help="Environment name, e.g., prod")
    parser.add_argument("--target", required=True, help="Target path, e.g., prod-1")
    parser.add_argument("--chamber", required=True, help="Chamber name, e.g., oa01")
    parser.add_argument("--nservers", type=int, required=True, help="Number of worker nodes to add")
    return parser.parse_args()

# Step 2: Build and verify path
def get_chamber_path(env, target, chamber):
    base_path = os.path.join(
        "CustomerVPC", "terraform", "config", "envs", env, env, target, chamber
    )
    full_path = os.path.abspath(base_path)

    print(f"🔍 Looking for chamber path: {full_path}")
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"❌ Chamber path does not exist: {full_path}")
    
    print(f"✅ Chamber path found: {full_path}")
    return full_path

# Main entry
def main():
    args = parse_args()
    chamber_path = get_chamber_path(args.environment, args.target, args.chamber)
    def main():
    args = parse_args()
    chamber_path = get_chamber_path(args.environment, args.target, args.chamber)
    tfvars_path, config_data = read_chamber_config(chamber_path, args.chamber)

if __name__ == "__main__":
    main()

========================================================================
import json

def read_chamber_config(chamber_path, chamber):
    # Look for file ending in `.tfvars.json`, preferably {chamber}.tfvars.json
    tfvars_filename = f"{chamber}.tfvars.json"
    tfvars_path = os.path.join(chamber_path, tfvars_filename)

    if not os.path.exists(tfvars_path):
        raise FileNotFoundError(f"❌ Expected config file not found: {tfvars_path}")

    print(f"📖 Reading config: {tfvars_path}")
    with open(tfvars_path, "r") as f:
        data = json.load(f)

    # Validate structure
    if "compute" not in data or \
       "compute_details" not in data["compute"] or \
       "node_details" not in data["compute"]["compute_details"]:
        raise ValueError("❌ Config is missing required structure: compute → compute_details → node_details")

    print(f"✅ Valid config loaded for chamber: {chamber}")
    return tfvars_path, data
    ================================================================================
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

def main():
    args = parse_args()
    chamber_path = get_chamber_path(args.environment, args.target, args.chamber)
    tfvars_path, config_data = read_chamber_config(chamber_path, args.chamber)


def add_worker_nodes(data, nservers):
    node_details = data["compute"]["compute_details"]["node_details"]
    eni_mapping = data.get("networking", {}).get("customer_eni_mapping", {})

    # Find all existing wrkNN keys
    existing_workers = [k for k in node_details.keys() if k.startswith("wrk") and k[3:].isdigit()]
    existing_nums = sorted([int(k[3:]) for k in existing_workers])
    next_index = max(existing_nums, default=0) + 1

    # Base configs
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

        # Add to node_details
        node_details[wrk_name] = {
            **default_worker,
            "name": wrk_name,
            "eni_name": eni_name
        }

        # Add to eni mapping
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

    # Update eni_mapping back into data
    data["networking"]["customer_eni_mapping"] = eni_mapping

    if added:
        print(f"🚀 Added worker nodes: {', '.join(added)}")
    else:
        print("⚠️ No new worker nodes added.")
add_worker_nodes(config_data, args.nservers)



def write_updated_config(tfvars_path, data):
    with open(tfvars_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Config successfully updated and written to: {tfvars_path}")
  write_updated_config(tfvars_path, config_data)



=======================================================
import glob

def find_chamber_tfvars_file(chamber):
    root_path = os.path.join("CustomerVPC", "terraform", "config", "envs")
    pattern = os.path.join(root_path, "**", f"{chamber}.tfvars.json")
    matches = glob.glob(pattern, recursive=True)

    if not matches:
        raise FileNotFoundError(f"❌ Could not find {chamber}.tfvars.json anywhere under {root_path}")

    # If multiple matches, take the first
    tfvars_path = os.path.abspath(matches[0])
    print(f"✅ Found chamber tfvars: {tfvars_path}")
    return tfvars_path



def main():
    args = parse_args()
    tfvars_path = find_chamber_tfvars_file(args.chamber)

    with open(tfvars_path, "r") as f:
        config_data = json.load(f)

    if "compute" not in config_data or \
       "compute_details" not in config_data["compute"] or \
       "node_details" not in config_data["compute"]["compute_details"]:
        raise ValueError("❌ Config is missing required structure: compute → compute_details → node_details")

    ensure_static_nodes(config_data)
    add_worker_nodes(config_data, args.nservers)
    write_updated_config(tfvars_path, config_data)


def get_chamber_path(env, target, chamber):
    path = os.path.join("CustomerVPC", "terraform", "config", "envs", env, env, target, chamber)
    full_path = os.path.abspath(path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"❌ Chamber path does not exist: {full_path}")

    print(f"✅ Chamber path found: {full_path}")
    return full_path







#!/usr/bin/python3

import argparse
import os
import json
import glob

# Step 1: Parse CLI arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Dynamic Terraform Worker Node Config Generator")
    parser.add_argument("--environment", required=True, help="Environment name, e.g., prod or test-3")
    parser.add_argument("--target", required=True, help="Target directory, e.g., prod-1 or to01")
    parser.add_argument("--chamber", required=True, help="Chamber name, e.g., oa98 or to01")
    parser.add_argument("--nservers", type=int, required=False, help="(Optional) Number of new worker nodes to add")
    return parser.parse_args()

# Step 2: Build and verify chamber path
def get_chamber_path(env, target, chamber):
    if env == "prod":
        path = os.path.join("CustomerVPC", "terraform", "config", "envs", env, env, target, chamber)
    else:
        path = os.path.join("CustomerVPC", "terraform", "config", "envs", env, target)

    full_path = os.path.abspath(path)
    print(f"🔍 Looking for chamber path: {full_path}")

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"❌ Chamber path does not exist: {full_path}")

    print(f"✅ Chamber path found: {full_path}")
    return full_path

# Step 3: Read and validate the .tfvars.json file
def read_chamber_config(chamber_path, chamber):
    pattern = os.path.join(chamber_path, "*.tfvars.json")
    matches = glob.glob(pattern)

    if not matches:
        raise FileNotFoundError(f"❌ No .tfvars.json file found in: {chamber_path}")

    tfvars_path = matches[0]
    print(f"📖 Found chamber tfvars: {tfvars_path}")

    with open(tfvars_path, "r") as f:
        data = json.load(f)

    if "compute" not in data or \
       "compute_details" not in data["compute"] or \
       "node_details" not in data["compute"]["compute_details"]:
        raise ValueError("❌ Missing required structure: compute → compute_details → node_details")

    print(f"✅ Valid config loaded from: {os.path.basename(tfvars_path)}")
    return tfvars_path, data

# Step 4: Ensure ls01 and haproxy nodes (optional/static)
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
        print(f"🛠️ Added missing static nodes: {', '.join(added)}")
    else:
        print("✅ Static nodes 'ls01' and 'haproxy' already exist.")

# Step 5: Add worker nodes interactively
def add_worker_nodes(data, nservers_arg=None):
    node_details = data["compute"]["compute_details"]["node_details"]
    eni_mapping = data.get("networking", {}).get("customer_eni_mapping", {})

    existing_workers = [k for k in node_details if k.startswith("wrk") and k[3:].isdigit()]
    existing_nums = sorted([int(k[3:]) for k in existing_workers])
    next_index = max(existing_nums, default=0) + 1

    print(f"🔍 Found {len(existing_workers)} existing worker node(s): {', '.join(existing_workers) if existing_workers else 'none'}")

    if nservers_arg is None:
        try:
            nservers = int(input("💬 How many new worker nodes would you like to add? "))
        except ValueError:
            print("❌ Invalid number entered. Aborting.")
            return
    else:
        nservers = nservers_arg

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

        if wrk_name in node_details:
            print(f"⚠️ Skipping already existing node: {wrk_name}")
            continue

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
        print(f"🚀 Added new worker nodes: {', '.join(added)}")
    else:
        print("⚠️ No new worker nodes added.")

# Step 6: Write back to JSON file
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
