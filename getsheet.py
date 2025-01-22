import os
import csv
import sys
import argparse

spreadsheet_id = "1PmShmeSLNmbcRhUQJpwvQo9ucWh7sn5l_FDl1oMxX0g" 
csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&id={spreadsheet_id}"
input_file = "spreadsheet.csv"
output_file = "filtered_D_E.csv"

os.system(f"wget -O {input_file} '{csv_url}'")

old_name = []
new_name = []

with open(input_file, mode="r", encoding="utf-8") as infile, open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
    csv_reader = csv.reader(infile)
    csv_writer = csv.writer(outfile)

    csv_writer.writerow(["old_name", "new_name"])

    for row in csv_reader:
        if len(row) > 4:
            d_value = row[3].strip() if row[3].strip() else "blank"
            e_value = row[4].strip() if row[4].strip() else "blank"
            old_name.append(d_value)
            new_name.append(e_value)
            csv_writer.writerow([d_value, e_value])

print(f"Saved into: {output_file}")

search_keyword = "Zto2Nu"

column_width = 80

print(f"new_name to old_name that includes '{search_keyword}': ")
for old, new in zip (old_name,new_name):
    if search_keyword in old:
        print(f"{old.ljust(column_width)}{new.ljust(column_width)}")

