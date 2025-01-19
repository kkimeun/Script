#!/usr/bin/env python3

import os
import sys
import argparse

sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import *

mcm = McM(dev=False,id=McM.OIDC)

CLONE_TARGETS = {
    "RunIII2024Summer24wmLHEGS" : 6.
    # nevents scheme
    # 22:22EE:23:23Bpix:24 = 1:3.5:2:1:12
}
PREPID_HEADER = "GEN-Run3Summer23wmLHEGS"

def parse_arguments() :

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",\
                        action="store", dest="prepids", required = True,\
                        help = "prepids")

    return parser.parse_args()

def set_prepids(prepids) :
    
    prepids_to_clone = []
    for prepid_ in prepids.split(","):
        if "-" in prepid_:
            start = prepid_.split("-")[0]
            end = prepid_.split("-")[1]
            if int(start) > int(end):
                sys.exit(f"ERROR :: Arrange prepids properly : smaller to larger number")
            for prepid in range(int(start), int(end)+1):
                prepid = str(prepid).zfill(5)
                prepids_to_clone.append(f"{PREPID_HEADER}-{prepid}")
        else:
            prepid = str(prepid_).zfill(5)
            prepids_to_clone.append(f"{PREPID_HEADER}-{prepid}")
       
    return prepids_to_clone

def clone_prepid(prepid) :

    for CLONE_TARGET, SCALE in CLONE_TARGETS.items():

        request = mcm.get('requests', prepid)
        print(request['prepid'])
        request["member_of_campaign"] = CLONE_TARGET

        ############################################
        # change the gridpack path in the fragment
        ############################################
        fragment = request['fragment']
        fragment = fragment.replace('/PdmV/Run3Summer22/MadGraph5_aMCatNLO/W/','/PdmV/RunIII2024Summer24/MadGraph5_aMCatNLO/W/')
        fragment = fragment.replace('_2J_', '_')
        fragment = fragment.replace('-2Jets_','-2Jets_Bin-2J-')
        request['fragment'] = fragment
        ############################################

        ############################################
        # change the dataset name
        ############################################
        dataset_name = request['dataset_name']
        print(f"Original dataset_name: {dataset_name}")
        dataset_name = dataset_name.replace('_2J_', '_')
        dataset_name = dataset_name.replace('-2Jets_','-2Jets_Bin-2J-')
        print(f"Modified dataset_name: {dataset_name}")
        request['dataset_name'] = dataset_name

        nevents = int(request["total_events"] * SCALE)
        if nevents <= 5e11:
            request["total_events"] = nevents
            clone_request = mcm.clone_request(request)
            print(f"LOG :: Cloning {prepid}, {clone_request}")
        else:
            print(f"LOG :: {prepid} very large in nevents {nevents} <====== WARNING, do not cloning")

def main() :

    args = parse_arguments()
    prepids = args.prepids
    prepids_to_clone = set_prepids(prepids)
    
    for prepid in prepids_to_clone:
        clone_prepid(prepid)


if __name__ == "__main__" :

    main()
