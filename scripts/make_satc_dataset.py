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

def find_comments(file_path, str_code):
    mime = None
    for ext in MIME_MAP.keys():
        if(file_path.endswith(ext)):
            mime = MIME_MAP[ext]

    comment = None 
    try:
        comment = c.extract_comments_from_str(str_code, mime)
    except Exception as e:
        #log_errors(file_path, str(e))
        #print(file_path + "\n" + str(e))
        comment = []

    return comment

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

def is_supported(file_path):
    for ext in MIME_MAP.keys():
        if(file_path.endswith(ext)):
            return True
    return False

def get_added_lines(list_tuple_additions):
    lines = []
    for addition in list_tuple_additions:
        lines.append(addition[0])
    return lines

def is_satdc(str_comment):
    patterns = ["TODO", "workaround", "fixme", "hack", "technical debt", "tech debt"]

    for p in patterns:
        if(str(str_comment).lower().count(p.lower()) > 0):
            return True
    
    return False

def get_satdc(repo_path, branch):
    satdc = []
    commits_cnt = 0
    for commit in RepositoryMining(repo_path, only_in_branch = branch, only_no_merge = True).traverse_commits():
        commits_cnt += 1
        for mod in commit.modifications:
            if(mod.source_code == None):
                 continue

            lines_added_in_commit = get_added_lines(mod.diff_parsed['added'])
            if(is_supported(mod.filename)):
                comments_in_file = group_comments(find_comments(mod.filename, mod.source_code))
                for comment in comments_in_file:
                    if(comment.is_multiline()):
                        init = comment.line_number()
                        end = comment.line_number() + len(comment.text().split("\n")) - 1

                        for i in range(init, end + 1):
                            if i in lines_added_in_commit:
                                if is_satdc(comment.text()):
                                    satdc.append((comment, commit, mod))
                                    break

                    else:
                        if(comment.line_number() in lines_added_in_commit):
                            if is_satdc(comment.text()):
                                    satdc.append((comment, commit, mod))

    print(">> Total de commits analisados {}".format(commits_cnt))                      
    return satdc

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

def find_references(comment_commits, issues):
    references = []

    for comment in comment_commits:
        comment_list = re.split('[\n\s\/$n$]', str(comment[0]))
        for id in issues:
            if(id in comment_list):
                references.append((comment[0], comment[1], comment[2], id))
            elif(("#"+ id) in comment_list):
                references.append((comment[0], comment[1], comment[2], id))
            elif(("issues/"+ id) in comment_list):
                references.append((comment[0], comment[1], comment[2], id))
    
    return references

def save_commits(repo_owner, repo_name, comment_commits):
    file_name = "datasets/satdc" + ENV + ".csv"
    file_out_path = Path(__file__).parent / file_name
    with open(file_out_path, "a") as the_file:
        for save in comment_commits:
            comment = save[0]
            commit = save[1]
            mod = save[2]

            the_file.write(repo_owner + "/" + repo_name + ";" +  mod.new_path + ";" + \
                comment.text().replace("\n", "$n$") + ";" +\
                str(comment.line_number()) + ";" + commit.hash + ";" +\
                str(commit.committer_date) + "\n")

def save_refs(repo_owner, repo_name, refs):
    file_name = "datasets/refs" + ENV + ".csv"
    file_out_path = Path(__file__).parent / file_name
    with open(file_out_path, "a") as the_file:
        for save in refs:
            comment = save[0]
            commit = save[1]
            mod = save[2]
            issue = save[3]

            the_file.write(repo_owner + "/" + repo_name + ";" +  mod.new_path + ";" + \
                issue + ";"+ comment.text().replace("\n", "$n$") + ";" +\
                str(comment.line_number()) + ";" + commit.hash + ";" +\
                str(commit.committer_date) + "\n")

def run(repo_owner, repo_name, label):
    g = Github("", "")
    github_user = g.get_user()

    original_repo = g.get_repo(repo_owner + "/" + repo_name)

    #clone repository
    repo_path = Path(__file__).parent / "./temp/" / original_repo.name
    cloned_repo = Repo.clone_from(original_repo.clone_url, repo_path)

    #print(cloned_repo.active_branch)
    
    print('Finding comment commits')
    comment_commits = get_satdc(str(repo_path), cloned_repo.active_branch)
    print(">> Total satdc commits " + str(len(comment_commits)))

    print('Saving SATDC')
    save_commits(repo_owner, repo_name, comment_commits)

    issue_number_list = load_issues()
    
    print('Finding refs')
    repo = repo_owner + "/" + repo_name
    refs = []

    if(repo in issue_number_list.keys()):
        refs = find_references(comment_commits, issue_number_list[repo])
        print(">> Total refs: " + str(len(refs)))

    print('Saving refs')
    save_refs(repo_owner, repo_name, refs)

    shutil.rmtree(repo_path)

    return (len(comment_commits), len(refs))

if __name__ == "__main__":

    #ENV = "_teste"
    
    file_name = "datasets/satd_repos" + ENV + ".csv"
    file_in_path = Path(__file__).parent / file_name

    with open(file_in_path, "r") as read_file:
        satdc = 0
        refs = 0
        analyzed = []

        for line in read_file.readlines():
            print(line.replace("\n", ""))
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
        
            file_name = "datasets/final_stats" + ENV + ".csv"
            file_out_path = Path(__file__).parent / file_name
            with open(file_out_path, "a") as the_file:
                the_file.write(data[0] + ";" + str(total[0]) + ";" +\
                     str(total[1]) + "\n")

        print("\n======== Final Report ========")
        print(">> Total satdc comments: " + str(satdc))
        print(">> Total refs: " + str(refs))