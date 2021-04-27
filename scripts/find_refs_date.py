from pathlib import Path
import datetime as dt
from dateutil.parser import parse 


def load_satdi():
    file_name = "datasets/selected/satdi_info_complete.csv"
    file_in_path = Path(__file__).parent / file_name
    
    with open(file_in_path, "r") as the_file:
        issues = {}
        for line in the_file.readlines():
            data = line.replace("\n", "").split(";")
            repo = data[0]

            if(repo == "repository"): continue
            repo = data[0].split("/")[1]

            issue = {
                'url': data[2],
                'created_at': data[5]}

            if(issues.get(repo) == None):
                issues[repo] = [issue]
            else:
                issues[repo].append(issue)
    return issues

def time_delta(date_issue, date_comment):
    comment_date = parse(date_comment).replace(tzinfo=None)
    issue_date = parse(date_issue).replace(tzinfo=None)
    delta = abs(comment_date - issue_date)
    return round(delta.total_seconds()/3600, 2)

if __name__ == "__main__":
    satdi = load_satdi() #repo: [{}, {}...]
    print("SATD-I Loaded")
    file_name = "datasets/selected/satdc_info_filtered.csv"
    file_in_path = Path(__file__).parent / file_name
    
    with open(file_in_path, "r") as the_file:
        for line in the_file.readlines():
            data = line.replace("\n", "").split(";")
            repo = data[0]

            if(repo == "repository"): continue

            name = repo.split("/")[1]
            file = data[1]
            init = str(data[2])
            created_at = data[-2]

            if(satdi.get(name) == None): continue

            for issue in satdi[name]:
                if time_delta(issue['created_at'], created_at) <= 1:
                    print("FOUND SIMILARITY")
                    new_file_name = "datasets/selected/refs_date.csv"
                    file_out_path = Path(__file__).parent / new_file_name
    
                    with open(file_out_path, "a") as out_file:
                        out_file.write(issue['url'].split(".com/")[-1] + ";" + issue['url'] + ";"\
                            + issue['created_at'] + ";"\
                            + created_at + ";" + file + ";"\
                            + str(init) + "\n")

