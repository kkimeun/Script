#!/usr/bin/env python3
import os
import subprocess
import re
import shutil

def transform_name(old_name):
    match = re.match(r"DYto2L-2Jets_MLL-50_PTLL-([0-9to-]+)_([0-9]+)J_amcatnloFXFX-pythia8", old_name)
    if match:
        PTLL, J = match.groups()
        new_name = f"DYto2L-2Jets_Bin-{J}J-MLL-50-PTLL-{PTLL}_amcatnloFXFX-pythia8"
        print(f"Transformed name: {old_name} -> {new_name}")
        return new_name
    print(f"Name transformation failed for: {old_name}")
    return None

def copy_and_rename_files_and_folders(directory):
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return

    for foldername in os.listdir(directory):
        if "DYto2L-2Jets_MLL-50_PTLL" in foldername and "J_" in foldername and "amcatnloFXFX" in foldername:
            old_folder_path = os.path.join(directory, foldername)
            if not os.path.isdir(old_folder_path):
                print(f"Skipping non-folder: {foldername}")
                continue

            new_folder_name = transform_name(foldername)
            if not new_folder_name:
                print(f"Skipping folder due to transformation failure: {foldername}")
                continue

            new_folder_path = os.path.join(directory, new_folder_name)
            shutil.copytree(old_folder_path, new_folder_path)
            print(f"Copied and Renamed folder: {foldername} -> {new_folder_name}")

            for filename in os.listdir(new_folder_path):
                old_file_path = os.path.join(new_folder_path, filename)
                if filename.endswith(".json") or filename.endswith(".dat") or filename.endswith(".f"):
                    new_file_name = filename.replace(foldername, new_folder_name)
                    new_file_path = os.path.join(new_folder_path, new_file_name)
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed file: {filename} -> {new_file_name}")

                    if new_file_name.endswith(".dat"):
                        try:
                            subprocess.run(
                                ["sed", "-i", f"s|output {foldername}|output {new_folder_name}|g", new_file_path],
                                check=True
                            )
                            print(f"Updated .dat file: {new_file_name}")
                        except subprocess.CalledProcessError as e:
                            print(f"Error updating .dat file: {new_file_name}, Error: {e}")
                            

if __name__ == "__main__":
    directory = "/afs/cern.ch/user/e/eunsu/private/GridpackFiles/Cards/MadGraph5_aMCatNLO/DY"
    copy_and_rename_files_and_folders(directory)

