#!/usr/bin/env python3

import os
import csv
import argparse
import shutil
import sys

# Base path for EOS
EOS_BASE = "/eos/cms/store/group/phys_generator/cvmfs/gridpacks/PdmV/"
event = "Z"

# Import McM module
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import *

mcm = McM(dev=False, id=McM.OIDC)

CLONE_TARGETS = {
    "RunIII2024Summer24wmLHEGS": 6.  # nevents scale factor
}

PREPID_HEADER = "GEN-Run3Summer23wmLHEGS"

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", action="store", dest="prepids", required=True, help="Comma-separated prepids"
    )
    return parser.parse_args()

def set_prepids(prepids):
    """Generate a list of prepids to process."""
    prepids_to_clone = []
    for prepid_ in prepids.split(","):
        if "-" in prepid_:
            start, end = prepid_.split("-")
            if int(start) > int(end):
                sys.exit("ERROR :: Arrange prepids properly: smaller to larger number")
            for prepid in range(int(start), int(end) + 1):
                prepids_to_clone.append(f"{PREPID_HEADER}-{str(prepid).zfill(5)}")
        else:
            prepids_to_clone.append(f"{PREPID_HEADER}-{str(prepid_).zfill(5)}")
    return prepids_to_clone

def process_prepid(prepid):
    """Process McM prepid to extract dataset_name, generators, and fragment."""
    request = mcm.get('requests', prepid)
    dataset_name = request['dataset_name']
    generators = request['generators']
    fragment = request['fragment']

    name = dataset_name.split("_TuneCP5")[0]

    print(f"Extracted name: {name}")
    print(f"Generator: {generators}")
    return name, generators, fragment

def extract_gridpack_path(fragment):
    """Extract gridpack directory path from fragment."""
    start = fragment.find("/PdmV/") + len("/PdmV/")
    end = fragment.find(".tar.xz")
    path = fragment[start:end]

    last_slash = path.rfind("/")
    if last_slash != -1:
        path = path[:last_slash + 1]

    print(f"Extracted path: {path}")
    return path


def update_names_from_csv(name):
    """Retrieve old and new names from CSV."""
    old_name, new_name = None, None
    with open("filtered_D_E.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if name in row["old_name"]:
                old_name = row["old_name"]
                new_name = row["new_name"]
                break

    if old_name and new_name:
        # Remove everything after '_TuneCP5_13p6TeV_'
        if "_TuneCP5_13p6TeV_" in old_name:
            old_name = old_name.split("_TuneCP5_13p6TeV_")[0]
        if "_TuneCP5_13p6TeV_" in new_name:
            new_name = new_name.split("_TuneCP5_13p6TeV_")[0]

    print(f"Updated old_name: {old_name}, new_name: {new_name}")
    return old_name, new_name

def copy_and_rename_files(old_path, new_path, old_name, new_name):
    """Copy and rename files in EOS."""
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    for file_name in os.listdir(old_path):
        if old_name in file_name:
            print(f"Found file: {file_name}")
            original_file_path = os.path.join(old_path, file_name)
            new_file_path = os.path.join(new_path, file_name)

            with open(original_file_path, 'rb') as src, open(new_file_path, 'wb') as dest:
                dest.write(src.read())

            print(f"Copied original file: {file_name} to {new_path}")

            renamed_file_path = os.path.join(new_path, file_name.replace(old_name, new_name))
            os.rename(new_file_path, renamed_file_path)
            print(f"Renamed file to: {os.path.basename(renamed_file_path)}")

def update_afs_folder(generator, event, old_name, new_name):
    """Update folder and file names in /afs/ directory."""
    base_path = f"/afs/cern.ch/user/e/eunsu/private/GridpackFiles/Cards/{generator}/{event}"

    if not os.path.exists(base_path):
        print(f"Path {base_path} does not exist.")
        return

    for folder_name in os.listdir(base_path):
        if old_name in folder_name:
            old_folder_path = os.path.join(base_path, folder_name)
            new_folder_name = folder_name.replace(old_name, new_name)
            new_folder_path = os.path.join(base_path, new_folder_name)

            os.rename(old_folder_path, new_folder_path)
            print(f"Renamed folder: {folder_name} to {new_folder_name}")

            for file_name in os.listdir(new_folder_path):
                old_file_path = os.path.join(new_folder_path, file_name)
                new_file_name = file_name.replace(old_name, new_name)
                new_file_path = os.path.join(new_folder_path, new_file_name)

                os.rename(old_file_path, new_file_path)
                print(f"Renamed file: {file_name} to {new_file_name}")

                if generator == "MadGraph5_aMCatNLO" and new_file_name.endswith(".dat"):
                    with open(new_file_path, 'r') as file:
                        content = file.read()
                    content = content.replace(old_name, new_name)
                    with open(new_file_path, 'w') as file:
                        file.write(content)
                    print(f"Updated content in file: {new_file_name}")

def clone_prepid(path, generator, event, prepid, old_name, new_name):
    """Clone McM prepid with updated parameters."""
    for CLONE_TARGET, SCALE in CLONE_TARGETS.items():
        request = mcm.get('requests', prepid)
        print(request['prepid'])
        request["member_of_campaign"] = CLONE_TARGET

        fragment = request['fragment']
        new_path = f"RunIII2024Summer24/{generator}/{event}/"
        fragment = fragment.replace(path, new_path)
        #fragment = fragment.replace("Run3Summer22","RunIII2024Summer24")
        fragment = fragment.replace(old_name, new_name)
        request['fragment'] = fragment

        dataset_name = request['dataset_name']
        dataset_name = dataset_name.replace(old_name, new_name)
        request['dataset_name'] = dataset_name

        nevents = int(request["total_events"] * SCALE)
        if nevents <= 5e11:
            request["total_events"] = nevents
            clone_request = mcm.clone_request(request)
            print(f"LOG :: Cloning {prepid}, {clone_request}")
        else:
            print(f"LOG :: {prepid} very large in nevents {nevents} <====== WARNING, do not cloning")

def main():
    args = parse_arguments()
    prepids = args.prepids
    print(f"Received prepids: {prepids}")

    prepids_to_clone = set_prepids(prepids)

    if not prepids_to_clone:
        print("No prepids to process. Exiting...")
        return

    for prepid in prepids_to_clone:
        name, generators, fragment = process_prepid(prepid)
        generator_str = generators[0]
        path = extract_gridpack_path(fragment)
        old_name, new_name = update_names_from_csv(name)
        old_path = os.path.join(EOS_BASE, path)
        new_path = os.path.join(EOS_BASE, "RunIII2024Summer24", generator_str, event)
        copy_and_rename_files(old_path, new_path, old_name, new_name)
        update_afs_folder(generator_str, event, old_name, new_name)
        clone_prepid(path, generator_str, event, prepid, old_name, new_name)

if __name__ == "__main__":
    main()

