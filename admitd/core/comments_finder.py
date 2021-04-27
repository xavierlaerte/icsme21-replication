import os
from pathlib import Path
from comment_parser import comment_parser as c
from comment_parser.parsers import common

def log_errors(file_name, error):
    doc_log = Path(__file__).parent.parent / "./results/errors.txt"
    with open(doc_log, "a") as the_file:
        the_file.write(file_name + ";" + error + "\n")

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

#returns list of tuples
def find_comments(repo_path):
    map_comments = {}
    files = get_repo_files(repo_path)

    for file_path in files:
        extension = ""
        #print(file_path)
        for ext in MIME_MAP.keys():
            if(file_path.endswith(ext)):
                extension = ext
        if(extension == ""):
            #print("extensio not found")
            print("Fail to analyze file: " +  file_path)
            continue

        try:
            comments = c.extract_comments(file_path, MIME_MAP[extension])
            #print(comments)
        except Exception as e:
            #log_errors(file_path, str(e))
            print(file_path + "\n" + str(e))
            continue
        
        if(len(comments) > 0):
            blocked_comments = group_comments(comments)
            map_comments[file_path] = blocked_comments

    return (map_comments, len(files))

#returns map: file: [comments]
def find_comments_old(repo_path):
    map_comments = {}
    files = get_repo_files(repo_path)

    for file_path in files:
        if(file_path.endswith(".js")):
            try:
                comments = comment_parser.extract_comments(file_path, "application/javascript")
            except Exception as e:
                log_errors(file_path, str(e))
                print(str(e))
                continue
        else:
            try:
                comments = comment_parser.extract_comments(file_path)
            except Exception as e:
                log_errors(file_path, str(e))
                print(file_path)
                print(str(e))
                continue

        if(len(comments) > 0):
            map_comments[file_path] = comments
    return (map_comments, len(files))

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

def group_comment_blocks(map_comments):
    map_result = {}

    for file_path in map_comments:
        for comment in map_comments[file_path]:
            continue
    return map_result