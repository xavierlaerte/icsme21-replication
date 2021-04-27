import os
import shutil
import requests
import time
import re

from pathlib import Path
from github import Github
from git import Repo

def run_query(json, headers): # A simple function to use requests.post to make the API call. 

    request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}. {}"
                        .format(request.status_code, json['query'],
                                json['variables']))
   
def get_satdi(owner, name, label):                           
    repo_owner = '"' + owner + '"'
    repo_name = '"' + name + '"'
    label = '"' + label + '"'
    #repo_owner = '"admitd"'
    #repo_name =  '"satd_test"'
    #label = '"technical debt"'

    query = """
    query example {
        repository(owner: {OWNER}, name: {NAME}) {
            issues(first: 5{AFTER}, labels: {LABEL}) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
            nodes {
                number
                url
                state
                createdAt
                closedAt
                timeline(first: 100) {
                    nodes {
                        ... on LabeledEvent {
                            createdAt
                            label {
                                name
                                }
                            }
                        }
                    }
                }
            }
        }
        rateLimit {
            remaining
            resetAt
        }
    }   
    """
    query_with_owner = query.replace("{OWNER}", repo_owner)
    query_with_name = query_with_owner.replace("{NAME}", repo_name)
    query_with_label = query_with_name.replace("{LABEL}", label)
    final_query = query_with_label.replace("{AFTER}", "")

    json = {
        "query":final_query, "variables":{}
    }

    token = '' #token 
    headers = {"Authorization": "Bearer " + token}

    result = run_query(json, headers)
    print(result)
    nodes = result['data']['repository']['issues']['nodes']
    next_page  = result['data']['repository']['issues']['pageInfo']['hasNextPage']

    while(next_page):
        print("PAGINATING")
        if(result['data']['rateLimit']['remaining'] == 0):
            token = ''
            headers = {"Authorization": "Bearer " + token}

        cursor = result['data']['repository']['issues']['pageInfo']['endCursor'] 
        next_query = query_with_label.replace("{AFTER}", ", after: \"%s\"" % cursor) 
        json["query"] = next_query
        result = run_query(json, headers)         
        nodes += result['data']['repository']['issues']['nodes']
        next_page  = result['data']['repository']['issues']['pageInfo']['hasNextPage']
        time.sleep(5)

    #print(nodes)
    for issue in nodes:
        labeled_at = ""
        closed_at = ""
        for event in issue['timeline']['nodes']:
            if(len(event) == 0):
                continue
            print(event)
            if str(event['label']['name']) == label.replace('"', ""):
                labeled_at = event['createdAt']
                break
        if(issue['state'] == "CLOSED"):
            closed_at = issue['closedAt']
        
        file_out_path = Path(__file__).parent / "datasets/satdi_teste.csv"
        with open(file_out_path, "a") as the_file:
            the_file.write(repo_owner + "/" + repo_name + "," + label + "," + \
                issue['url'] + "," + str(issue['number']) + "," + \
                issue['state'] + "," + issue['createdAt'] + "," + \
                closed_at + "," + labeled_at + "\n")

if __name__ == "__main__":

    file_in_path = Path(__file__).parent / "datasets/satd_repos_teste.csv"
    with open(file_in_path, "r") as read_file:
        for line in read_file.readlines():
            print(line.replace("\n", ""))
            data = line.split(",")
            repo_owner = data[0].split("/")[0]
            repo_name = data[0].split("/")[1]
            label = data[2]

            get_satdi(repo_owner, repo_name, label)