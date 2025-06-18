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
