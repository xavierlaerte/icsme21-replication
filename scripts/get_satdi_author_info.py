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
            time.sleep(100)
            request = requests.post('https://api.github.com/graphql', json=json, headers=headers)
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}. {}"
                        .format(request.status_code, json['query'],
                                json['variables']))
   
def get_info(owner, name, issue, token):                           
    repo_owner = '"' + owner + '"'
    repo_name = '"' + name + '"' 

    query = """
    query example {
        repository(owner: {OWNER}, name: {NAME}) {
            issue(number: {ISSUE}) {
                author {
                    ... on User {
                        email
                        name
                        login
                    }
                }
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
    
    return result['data']['repository']['issue']['author']

if __name__ == "__main__":
    file_in_path = Path(__file__).parent / "datasets/selected/satdi_info_complete2.csv"
    ready = []
    with open(file_in_path, "r") as read_file:
        for line in read_file.readlines():
            data = line.split(";")

            ready.append((data[0], data[3]))


    t2 = '' #token 
    t1 = ''

    token = t1

    file_in_path = Path(__file__).parent / "datasets/selected/satdi_info_complete.csv"
    cnt = 0
    with open(file_in_path, "r") as read_file:
        for line in read_file.readlines():
            data = line.split(";")

            if(data[0] == 'repository'): continue 

            if ((data[0], data[3]) in ready): continue

            repo_owner = data[0].split("/")[0]
            repo_name = data[0].split("/")[1]
            number = data[3]

            print(data[0] + ": " + number)
            
            author_name = ""
            author_email = ""
            author_login = ""
            author_company = ""

            issue = get_info(repo_owner, repo_name, number, token)

            if issue != None:
                author_name = issue['name'] if issue['name'] != None else ""
                author_email = issue['email'] if issue['email'] != None else ""
                author_login = issue['login'] if issue['login'] != None else ""
                author_company = issue['company'] if issue['company'] != None else ""

            file_name = "datasets/selected/satdi_info_complete2.csv"
            file_out_path = Path(__file__).parent / file_name
            with open(file_out_path, "a") as the_file:
                the_file.write(line.replace("\n", "") + ";" \
                    + author_name + ";"\
                    + author_email + ";"\
                    + author_login + ";"\
                    + author_company + "\n")
            
            cnt += 1
            if(cnt == 100):
                print(">>> ALT TOKEN")
                cnt = 0
                time.sleep(100)
                if(token == t1):
                    token = t2
                else: 
                    token = t1
                