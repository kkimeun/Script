#!/usr/bin/env python3
import os
import subprocess

base_path = "/afs/cern.ch/user/e/eunsu/private/GridpackFiles/Cards/MadGraph5_aMCatNLO/VBF/"
old_folder_name = "VBFto2L_MLL-50_madgraph-pythia8"
new_folder_name = "VBFto2L_Bin-MLL-50_madgraph-pythia8"

old_folder_path = os.path.join(base_path, old_folder_name)
new_folder_path = os.path.join(base_path, new_folder_name)
os.rename(old_folder_path, new_folder_path)

files_to_update = [
    "VBFto2L_MLL-50_madgraph-pythia8_proc_card.dat",
]

for old_file_name in files_to_update:
    old_file_path = os.path.join(new_folder_path, old_file_name)
    new_file_name = old_file_name.replace("MLL-", "Bin-MLL-")
    new_file_path = os.path.join(new_folder_path, new_file_name)

    os.rename(old_file_path, new_file_path)

    if "proc_card" in new_file_name:
        subprocess.run(
            [
                "sed",
                "-i",
                r"/^output VBFto2L_MLL-50_madgraph-pythia8 -nojpeg/s/MLL-/Bin-MLL/",
                new_file_path,
            ],
            check=True,
        )

