#!/usr/bin/env python3

import os
import sys
import argparse

BASE_DIR = "/eos/cms/store/group/phys_generator/cvmfs/gridpacks/PdmV/"

def copy_and_rename_files(source_dir, destination_dir):
    if not os.path.isdir(source_dir):
        print(f"Source directory does not exist: {source_dir}")
        return

    os.makedirs(destination_dir, exist_ok=True)

    for filename in os.listdir(source_dir):
        if filename.startswith("Zto2Nu-2Jets") and "PTNuNu" in filename:
            new_filename = filename.replace("2Jets_", "2Jets_Bin-")
            new_filename = new_filename.replace("J_PTNuNu", "J-PTNuNu")
            source_path = os.path.join(source_dir, filename)
            destination_path = os.path.join(destination_dir, new_filename)

            try:
                with open(source_path, "rb") as src, open(destination_path, "wb") as dst:
                    dst.write(src.read())
                print(f"Copied and renamed: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error copying {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy and rename files by replacing 'PTG-' with 'Bin-PTG-' in filenames.")
    parser.add_argument(
        "--source_dirs",
        nargs="+",
        required=True,
        help="List of source directories containing the files.",
    )
    parser.add_argument(
        "--destination_dirs",
        nargs="+",
        required=True,
        help="List of destination directories corresponding to source directories.",
    )

    args = parser.parse_args()

    # Validate input lengths
    if len(args.source_dirs) != len(args.destination_dirs):
        print("Error: Number of source directories must match number of destination directories.")
        sys.exit(1)

    # Process each source-destination pair
    for source_dir, destination_dir in zip(args.source_dirs, args.destination_dirs):
        full_source_dir = os.path.join(BASE_DIR, source_dir)
        full_destination_dir = os.path.join(BASE_DIR, destination_dir)
        print(f"Processing: {full_source_dir} -> {full_destination_dir}")
        copy_and_rename_files(full_source_dir, full_destination_dir)

    print("All files processed successfully!")

