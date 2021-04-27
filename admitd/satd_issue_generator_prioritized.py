import shutil
import git

from github import Github
from git import Repo
from pathlib import Path 
from core.satd_analiser import *
from utils.log_parser import * 
from core.issue_title import *
from core.issue_body import *
from core.issue import *
from utils.get_commits_for_file import *
import time

#login 
g = Github("", "")
github_user = g.get_user()

try:
    previous = g.get_repo('')
    previous.delete()
except:
    pass
    
original_repo = g.get_repo('')
original_label = original_repo.get_label("") #label used in orginal repository

#clone repository
repo_path = Path(__file__).parent / "./temp/" / original_repo.name
cloned_repo = Repo.clone_from(original_repo.clone_url, repo_path)

satd = analyze(repo_path)

#just fork and create issues if we find any SATD
if(len(satd.items()) > 0):
    print("Analyzing commits")
    filter_files = get_important_files(str(repo_path), 0.8)

    forked_repo = github_user.create_fork(original_repo) 

    forked_repo.edit(has_issues=True) #enable issue creation to forked repositories
    label = forked_repo.create_label(original_label.name, original_label.color)
    label_priority = forked_repo.create_label("top", "DC143C")
    
    issues = {} #titlle : [issue]
    for detected_file in satd.keys():
        labels = [label]
        if(detected_file not in filter_files):
            continue
            #labels.append(label_priority)

        for comment in satd[detected_file]:
            issue_title = Issue_Title()
            issue_title.create_title(comment)
            #print(issue_title.text)
            issue_body = Issue_Body()
            issue_body.create_body(cloned_repo, forked_repo, detected_file, comment)
            #print(issue_body.text)
            issue = Issue(issue_title, issue_body, labels)
            
            if(issues.get(issue.title.text) == None):
                issues[issue.title.text] = [issue]
            else:
                issues[issue.title.text].append(issue)
    
    to_publish = []
    #join issues
    for title in issues.keys():
        if(len(issues[title]) == 1): #nothing to join
            to_publish.append(issues[title][0])
        else:
            str_body = issues[title][0].body.text
            labels = [label]
            for issue in issues[title][1:]:
                str_body = str_body + "\n\n---\n\n" + issue.body.text
                if (len(issue.labels) == 2):
                    labels.append(label_priority)

            new_title = Issue_Title()
            new_title.set_title(title)

            new_body = Issue_Body()
            new_body.set_body(str_body)

            new_issue = Issue(new_title, new_body, labels)
            to_publish.append(new_issue)

    #print(issues)
    cnt = 1    
    for issue in to_publish:
        #print(">>>> titulo: " + issue.title.text)
        if(len(issue.title.text.split(" ")) <= 1): #skip issues with just a word
            print("skipped")
            continue
        print("Publishing issue: " + str(cnt) + "/" + str(len(to_publish)))
        issue.publish(forked_repo)
        cnt += 1
        time.sleep(2)
        

shutil.rmtree(repo_path)
