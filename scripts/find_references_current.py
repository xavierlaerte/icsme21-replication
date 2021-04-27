import os
import shutil
import requests
import time
import re

from pathlib import Path
from github import Github
from git import Repo
from pydriller import RepositoryMining
from comment_parser import comment_parser as c
from comment_parser.parsers import common

ENV = ""
MIME_MAP = {
        ".js" : 'application/javascript',  # Javascript
        ".ts" : 'application/javascript',  # Javascript
        ".tsx" : 'application/javascript',  # Javascript
        ".mjs" : 'application/javascript',  # Javascript
        ".html" : 'text/html',  # HTML
        ".c" : 'text/x-c',  # C
        ".cpp" : 'text/x-c++',  # C++
        ".cs" : 'text/x-c++',  # C#
        ".go" : 'text/x-go',  # Go
        ".java" : 'text/x-java',  # Java
        ".py" : 'text/x-python',  # Python
        ".rb" : 'text/x-ruby',  # Ruby
        ".sh" : 'text/x-shellscript',  # Unix shell
        ".xml" : 'text/xml',  # XML
    }

def group_comments(list_comments):
    comments_grouped = []
    passed_comments = []
    for i in range(len(list_comments)):
        if(list_comments[i] in passed_comments):
            continue

        blocked_comment = list_comments[i]
        first_line = list_comments[i].line_number()
        actual_line = list_comments[i].line_number()
        for j in range(i+1, len(list_comments)):
            if(list_comments[j].line_number() == actual_line + 1): #found block to group
                text = blocked_comment.text() + "\n" + list_comments[j].text()
                blocked_comment = common.Comment(text, first_line, True)
                passed_comments.append(list_comments[j])
                actual_line = list_comments[j].line_number()
            else:
                break
        comments_grouped.append(blocked_comment)

    return comments_grouped

def is_satdc(str_comment):
    patterns = ["TODO", "workaround", "fixme", "hack", "technical debt", "tech debt"]

    for p in patterns:
        if(str(str_comment).lower().count(p.lower()) > 0):
            return True
    
    return False

#returns list of tuples
def find_comments(repo_path):
    map_comments = {}
    files = get_repo_files(repo_path)

    for file_path in files:
        extension = ""
        for ext in MIME_MAP.keys():
            if(file_path.endswith(ext)):
                extension = ext
        if(extension == ""):
            #print("Fail to analyze file: " +  file_path)
            continue

        try:
            comments = c.extract_comments(file_path, MIME_MAP[extension])
        except Exception as e:
            #log_errors(file_path, str(e))
            #print(file_path + "\n" + str(e))
            continue
        
        if(len(comments) > 0):
            blocked_comments = group_comments(comments)
            map_comments[file_path] = blocked_comments

    return map_comments

def get_repo_files(repo_path):
    r_files = []

    exclude = set(['.git'])
    for subdir, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in exclude]
        for filename in files:
            if filename.endswith(".md"):
                continue
            r_files.append(subdir + os.sep + filename)  
    return r_files 

def get_satdc(repo_path):

    comments = find_comments(repo_path)
    satd_comments = {}
    
    for file_name in comments.keys():
        satd = []
        for comment in comments[file_name]:
            if is_satdc(comment.text()):
                satd.append(comment)

        if(len(satd) > 0):
            satd_comments[file_name] = satd

    return satd_comments

def load_issues():
    map_issues = {}
    
    file_name = "datasets/satdi" + ENV + ".csv"
    file_in_path = Path(__file__).parent / file_name
    with open(file_in_path, "r") as read_file:
        for line in read_file.readlines():
            repo = line.split(",")[0].replace('"', '')
            number = line.split(",")[3]

            if(repo in map_issues.keys()):
                map_issues[repo].append(number)
            else:
                map_issues[repo] = [number]

    return map_issues

def find_references(map_comments, issues):
    references = []

    for file in map_comments:
        for comment in map_comments[file]:
            comment_list = re.split('[\n\s\/$n$]', str(comment))
            for id in issues:
                if(id in comment_list):
                    references.append((file, comment.text(), comment.line_number(), id))
                elif(("#"+ id) in comment_list):
                    references.append((file, comment.text(), comment.line_number(), id))
                elif(("issues/"+ id) in comment_list):
                    references.append((file, comment.text(), comment.line_number(), id))
        
    return references

def save_commits(repo_owner, repo_name, map_comments):
    file_name = "datasets/satdc_current" + ENV + ".csv"
    file_out_path = Path(__file__).parent / file_name

    with open(file_out_path, "a") as the_file:
        for file in map_comments:
            for comment in map_comments[file]:
                file_name = file.split("/temp/" + repo_name)[-1]
                the_file.write(repo_owner + "/" + repo_name + ";" +  file_name + ";" + \
                    comment.text().replace("\n", "$n$") + ";" +\
                    str(comment.line_number()) + "\n")

def save_refs(repo_owner, repo_name, refs):
    file_name = "datasets/refs_current" + ENV + ".csv"
    file_out_path = Path(__file__).parent / file_name
    with open(file_out_path, "a") as the_file:
        for save in refs:
            file_name = save[0].split("/temp/" + repo_name)[-1]

            the_file.write(repo_owner + "/" + repo_name + ";" +  file_name + ";" + \
                save[3] + ";"+ save[1].replace("\n", "$n$") + ";" +\
                str(save[2]) + "\n")

def count_comments(map_comments):
    total = 0
    for file in map_comments:
        total += len(map_comments[file])
    return total

def run(repo_owner, repo_name, label):
    g = Github("", "")
    github_user = g.get_user()

    original_repo = g.get_repo(repo_owner + "/" + repo_name)

    #clone repository
    repo_path = Path(__file__).parent / "./temp/" / original_repo.name
    cloned_repo = Repo.clone_from(original_repo.clone_url, repo_path)
    
    print('Finding satdc comments')
    satdc_comments = get_satdc(str(repo_path))
    print(">> Total satdc comments " + str(count_comments(satdc_comments)))

    print('Saving SATDC')
    save_commits(repo_owner, repo_name, satdc_comments)

    issue_number_list = load_issues()
    
    print('Finding refs')
    repo = repo_owner + "/" + repo_name
    refs = []

    if(repo in issue_number_list.keys()):
        refs = find_references(satdc_comments, issue_number_list[repo])
        print(">> Total refs: " + str(len(refs)))

    print('Saving refs')
    save_refs(repo_owner, repo_name, refs)

    shutil.rmtree(repo_path)

    return (count_comments(satdc_comments),len(refs))

if __name__ == "__main__":

    ENV = "_teste"
    
    file_name = "datasets/satd_repos" + ENV + ".csv"
    file_in_path = Path(__file__).parent / file_name
    
    with open(file_in_path, "r") as read_file:
        satdc = 0
        refs = 0

        analyzed = []

        for line in read_file.readlines():
            print(line)
            data = line.split(",")

            if(data[0] in analyzed):
                continue

            repo_owner = data[0].split("/")[0]
            repo_name = data[0].split("/")[1]
            label = data[2]

            total = run(repo_owner, repo_name, label)
            satdc += total[0]
            refs += total[1]
            analyzed.append(data[0])
        
            file_name = "datasets/final_stats_current" + ENV + ".csv"
            file_out_path = Path(__file__).parent / file_name
            with open(file_out_path, "a") as the_file:
                the_file.write(data[0] + ";" + str(total[0]) + ";" +\
                     str(total[1]) + "\n")

        print("\n======== Final Report ========")
        print(">> Total satdc comments: " + str(satdc))
        print(">> Total refs: " + str(refs))