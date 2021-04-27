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
    elif request.status_code == 502:
        while request.status_code != 200:
            print("Erro 502, going to sleep!")
            time.sleep(200)
            request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}. {}"
                        .format(request.status_code, json['query'],
                                json['variables']))
   
def get_body(owner, name, issue, token):                           
    repo_owner = '"' + owner + '"'
    repo_name = '"' + name + '"' 

    query = """
    query example{
        repository(owner: {OWNER}, name: {NAME}) {
            issue(number: {ISSUE}) {
                body
            }
        }
    }
    """
    
    query_with_owner = query.replace("{OWNER}", repo_owner)
    query_with_name = query_with_owner.replace("{NAME}", repo_name)
    final_query = query_with_name.replace("{ISSUE}", issue)

    json = {
        "query":final_query, "variables":{}
    }

    headers = {"Authorization": "Bearer " + token}

    result = run_query(json, headers)

    return result['data']['repository']['issue']['body']

if __name__ == "__main__":

    t2 = '' #token 
    t1 = ''

    token = t1

    file_in_path = Path(__file__).parent / "datasets/satdi.csv"
    #file_in_path = Path(__file__).parent / "datasets/satdi_teste.csv"
    cnt = 0
    with open(file_in_path, "r") as read_file:
        for line in read_file.readlines():
            print(line.replace("\n", ""))
            data = line.split(",")
            repo_owner = data[0].split("/")[0].replace('"', "")
            repo_name = data[0].split("/")[1].replace('"', "")
            number = data[3]
        
            body = get_body(repo_owner, repo_name, number, token)
            cnt += 1

            if(body == ''):
                continue

            string = "github.com/" + repo_owner + "/" + repo_name + "/blob/"
            if(body.count(string) > 0):
                file_name = "datasets/satdc_from_issues_2.csv"
                file_out_path = Path(__file__).parent / file_name
                with open(file_out_path, "a") as the_file:
                    the_file.write(line.replace("\n","") + "\n")
            elif(body.count("#L") > 0):
                file_name = "datasets/satdc_from_issues_2.csv"
                file_out_path = Path(__file__).parent / file_name
                with open(file_out_path, "a") as the_file:
                    the_file.write(line.replace("\n","") + "\n")

            if(cnt == 100):
                print(">>> ALT TOKEN")
                cnt = 0
                time.sleep(200)
                if(token == t1):
                    token = t2
                else: 
                    token = t1
                