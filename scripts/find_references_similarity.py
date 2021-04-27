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
            issue = {
                'url': data[2],
                'body': data[8]}

            if(issues.get(repo) == None):
                issues[repo] = [issue]
            else:
                issues[repo].append(issue)
    return issues

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
    satdi = load_satdi() #repo: [{}, {}...]
    print("SATD-I Loaded")
    file_name = "datasets/selected/satdc_current.csv"
    file_in_path = Path(__file__).parent / file_name
    
    with open(file_in_path, "r") as the_file:
        for line in the_file.readlines():
            data = line.replace("\n", "").split(";")
            repo = data[0]
            file = data[1]
            comment = data[2]
            init = data[-1]

            if(satdi.get(repo) == None): continue

            for issue in satdi[repo]:
                if similar(issue['body'], comment) > 0.5:
                    print("FOUND SIMILARITY")
                    new_file_name = "datasets/selected/refs_similarity.csv"
                    file_out_path = Path(__file__).parent / new_file_name
    
                    with open(file_out_path, "a") as out_file:
                        out_file.write(repo + ";" + issue['url'] + ";"\
                            + issue['body'] + ";"\
                            + comment + ";" + file + ";"\
                            + str(init) + "\n")

