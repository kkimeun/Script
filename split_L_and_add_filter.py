#!/usr/bin/env python3
import os
import shutil
import subprocess

base_path = "/afs/cern.ch/user/e/eunsu/private/GridpackFiles/Cards/MadGraph5_aMCatNLO/DY/"
example_path = "/afs/cern.ch/user/e/eunsu/private/example/20250113_sample.json"
source_dat_path = os.path.join(base_path, "DYto2L-4Jets_Bin-MLL-10to50_madgraphMLM-pythia8")
source_dat_file = "DYto2L-4Jets_Bin-MLL-10to50_madgraphMLM-pythia8_proc_card.dat"

targets = {
    "DYto2E-4Jets_Bin-MLL-10to50_madgraphMLM-pythia8": "E",
    "DYto2Mu-4Jets_Bin-MLL-10to50_madgraphMLM-pythia8": "Mu",
    "DYto2Tau-4Jets_Bin-MLL-10to50_madgraphMLM-pythia8": "Tau",
}

for folder_name, target in targets.items():
    new_folder_path = os.path.join(base_path, folder_name)
    
    os.makedirs(new_folder_path, exist_ok=True)

    new_json_name = f"{folder_name}.json"
    new_json_path = os.path.join(new_folder_path, new_json_name)
    shutil.copy2(example_path, new_json_path)

    subprocess.run(
        [
            "sed",
            "-i",
            f's|"Filter/AtLeastOneL.dat"|"Filter/AtLeastOne{target}.dat"|g',
            new_json_path,
        ],
        check=True,
    )


    new_dat_name = f"{folder_name}_proc_card.dat"
    new_dat_path = os.path.join(new_folder_path, new_dat_name)
    shutil.copy2(os.path.join(source_dat_path, source_dat_file), new_dat_path)

    subprocess.run(
        [
            "sed",
            "-i",
            f"s|output DYto2L-4Jets_Bin-MLL-10to50_madgraphMLM-pythia8 -nojpeg|output {folder_name} -nojpeg|g",
            new_dat_path,
        ],
        check=True,
    )

print("spliting completed")

