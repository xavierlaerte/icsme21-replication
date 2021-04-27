from pathlib import Path
from difflib import SequenceMatcher

def load_satdi():
    file_name = "datasets/selected/satdi_info_complete.csv"
    file_in_path = Path(__file__).parent / file_name
    
    with open(file_in_path, "r") as the_file:
        issues = {}
        for line in the_file.readlines():
            data = line.replace("\n", "").split(";")
            repo = data[0]

            if(repo == "repository"): continue
            issues[data[2]] = data[8]
    return issues

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
    satdi = load_satdi() #url: body
    print("SATDI loaded")
    file_name = "datasets/selected/refs_date_complete.csv"
    file_in_path = Path(__file__).parent / file_name
    
    with open(file_in_path, "r") as the_file:
        cnt = 0
        for line in the_file.readlines():
            cnt += 1
            print(cnt)
            data = line.replace("\n", "").split(";")

            if(similar(data[2], satdi[data[1]]) >= 0.5):
                print("FOUND COMMENT")
                new_file_name = "datasets/selected/refs_date_sim_complete2.csv"
                file_out_path = Path(__file__).parent / new_file_name
    
                with open(file_out_path, "a") as out_file:
                    out_file.write(line.replace("\n", "") + ";"\
                        + satdi[data[1]] + "\n")