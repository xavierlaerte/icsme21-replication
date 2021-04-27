from pathlib import Path

file_name = "datasets/selected/final_stats_current_complete.csv"
file_in_path = Path(__file__).parent / file_name

with open(file_in_path, "r") as the_file:
    repos = []
    for line in the_file.readlines():
        repo = line.split(",")[0]
        
        if(repo == "repository"):
            continue
        
        repos.append(repo.split("/")[1])

file_name = "datasets/selected/satdc_info.csv"
file_in_path = Path(__file__).parent / file_name

with open(file_in_path, "r") as in_file:
    for line in in_file.readlines():
        repo = line.split(";")[0].split("/")[1]

        if repo in repos:
            out_file_name = "datasets/selected/satdc_info_filtered.csv"
            file_out_path = Path(__file__).parent / out_file_name

            with open(file_out_path, "a") as out_file:
                out_file.write(line)
