import os
import sys
import modules.file_operation as fo
import modules.data_manipulation as dm
import modules.swift as swift
import modules.aws_cmd as aws_cmd
import base64
import json
import requests


def main():

    dirname = os.path.dirname(__file__)
    run_chef_location = os.path.join(os.path.abspath(__file__ + "../../../../"),"run_chef")
    parent_dir = os.path.abspath(__file__ + "../../../../")

    user_input_dict = json.loads(base64.b64decode(sys.argv[1]))
    template_path = os.path.join(dirname,'template')

    base_config_dict = dm.prepare_base_json(template_path, 'customer-base-config-template.json',user_input_dict)
    s3_object_name = dm.prepare_s3_object_name(user_input_dict)
    fo.write_base_config_json(base_config_dict,f"{run_chef_location}/config/base-config.json")
    print("Generated base config for admin chamber")
    fo.create_chef_tar(run_chef_location,user_input_dict["recipe_tar"])

    data = open(os.path.join(run_chef_location.replace('run_chef',''), user_input_dict["recipe_tar"]), 'rb')

    swift.upload(user_input_dict['mirror'],s3_object_name,data, user_input_dict)
    os.remove(f"{run_chef_location}/config/base-config.json")
    os.remove(os.path.join(run_chef_location.replace('run_chef',''), user_input_dict["recipe_tar"]))

    mirror_bucket_uri = dm.prepare_s3_mirror_uri(user_input_dict)
    cc_chamber_dict = dm.prepare_base_json(template_path, 'cc-chamber-template.json',user_input_dict)
    cc_chamber_file = fo.write_base_config_json(cc_chamber_dict,f"{parent_dir}/{user_input_dict['chamber_info']['chamber_name']}.json")
    aws_cmd.upload_run_chef(mirror_bucket_uri, cc_chamber_file,user_input_dict["s3_mirror_access_details"])
    os.remove(cc_chamber_file)

if __name__ == "__main__":
    main()






#!/bin/bash

# Set hostname
hostnamectl set-hostname ${hostname}

# Create base config manually (if needed by any agent or logging)
cat <<EOF > /etc/base-config.json
{
  "hostname": "${hostname}",
  "environment": "test",
  "chamber": "TN05",
  "role": "baremetal-node"
}
EOF

# Example: simulate Chef's folder creation
mkdir -p /opt/nexem/config
echo "Node initialized on $(date)" > /opt/nexem/config/status.txt

# Start essential services (if image doesn’t already do this)
systemctl restart NetworkManager

# Optional: Touch log to show image boot
echo "Provision complete - no Chef" >> /etc/motd
