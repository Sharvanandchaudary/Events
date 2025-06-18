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
