import os
import shutil
import requests
import time
import re
import datetime as dt

from pathlib import Path
from github import Github
from git import Repo
from pydriller import RepositoryMining
from dateutil.parser import parse 

ENV = ""

def load_satc_file(repo):
    file_name = "datasets/selected/satdc_current" + ENV + ".csv"
    file_in_path = Path(__file__).parent / file_name

    result = []
    with open(file_in_path, "r") as the_file:
        for line in the_file.readlines():
            data = line.replace("\n", "").split(";")

            if(repo != data[0]):
                continue
            
            file = data[1].replace("/", "", 1)
            init_line = int(data[-1])
            #fix cases of comments with ;
            comment = data[2]
            if len(data) > 4:
                comment = ""
                for i in range(2, len(data) - 1):
                    comment = comment + data[i] + ";"
            end_line = init_line + len(comment.split("$n$")) - 1
            total_char = len(comment) - (comment.count("$n$") * 3)
            #file, init_line, end_line
            add = (file, init_line, end_line, total_char)
            result.append(add)
    
    return result

def get_log_info(cloned_repo, init_line, end_line, in_file):
    log = cloned_repo.git.log("-L{},{}:{}".format(init_line, end_line, in_file))
        
    return log

def parse_log(log):
    stats = {'total_commits': 0,
            'total_authors': 0,
            'age': 0,
            'created_at': "", 
            'author' : "", 
            'author_email' : "", 
            'commit_hash' : ""}

    hash = ""
    author_name = ""
    author_mail = ""
    authors = []
    data = log.split("\n")
    for line in data:
        if bool(re.match('commit', line, re.IGNORECASE)):
            stats['total_commits'] = stats['total_commits'] + 1
            hash = line.split(" ")[-1]
        if bool(re.match('author:', line, re.IGNORECASE)):
            # Author: xxxx <xxxx@xxxx.com>
            m = re.compile('Author: (.*) <(.*)>').match(line)
            author = (m.group(1), m.group(2))
            authors.append(author)
            author_name = author[0]
            author_mail = author[1]
        if bool(re.match('date:', line, re.IGNORECASE)):
            # Date: xxx
            date_str = str(line.split("   ")[1])
            commit_date = parse(date_str).replace(tzinfo=None)
            now = dt.datetime.now()
            delta = now - commit_date
            days_life = round(delta.total_seconds()/86400, 2)
            stats['age'] = days_life
            stats['created_at'] = date_str

    stats['total_authors'] = len(set(authors))
    stats['commit_hash'] = hash
    stats['author_name'] = author_name
    stats['author_mail'] = author_mail
    return stats

def run(repo_owner, repo_name):
    g = Github("", "")
    github_user = g.get_user()

    original_repo = g.get_repo(repo_owner + "/" + repo_name)

    #clone repository
    repo_path = Path(__file__).parent / "./temp/" / original_repo.name
    cloned_repo = Repo.clone_from(original_repo.clone_url, repo_path)

    satdc = load_satc_file(repo_owner + "/" + repo_name)

    for comment in satdc:
        try:
            log = get_log_info(cloned_repo, comment[1], comment[2], comment[0])
        except:
            print(comment)
            continue
        stats  = parse_log(log)

        file_name = "datasets/selected/satdc_info_full" + ENV + ".csv"
        file_out_path = Path(__file__).parent / file_name

        with open(file_out_path, "a") as out_file:   
            out_file.write(repo_owner + "/" + repo_name + ";"\
                + comment[0] + ";"\
                + str(comment[1]) + ";"\
                + str(comment[2]) + ";"\
                + str(stats['total_commits']) + ";"\
                + str(stats['total_authors']) + ";"\
                + str(stats['age']) + ";"\
                + stats['created_at'] + ";"\
                + str(comment[3]) + ";"\
                + stats['commit_hash'] + ";"\
                + stats['author_name'] + ";"\
                + stats['author_mail'] + "\n")

    shutil.rmtree(repo_path)


if __name__ == "__main__":

    ENV = "_teste"
    
    file_name = "datasets/satd_repos" + ENV + ".csv"
    file_in_path = Path(__file__).parent / file_name

    with open(file_in_path, "r") as read_file:
        analyzed = []

        for line in read_file.readlines():
            print(line.replace("\n", ""))
            data = line.split(",")

            if(data[0] in analyzed):
                continue

            repo_owner = data[0].split("/")[0]
            repo_name = data[0].split("/")[1]

            run(repo_owner, repo_name)
            analyzed.append(data[0])