import comment_parser
from subprocess import Popen, PIPE
from pathlib import Path

def identify_stad(comments):
    satd_comments = {}
    for file_name in comments.keys():
        satd = []
        for comment in comments[file_name]:
            if select_method(str(comment), "SUB"):
                satd.append(comment)

        if(len(satd) > 0):
            satd_comments[file_name] = satd

    return satd_comments

def select_method(str_comment, method):
    if method == "NLP":
        return is_satd_nlp(str_comment)
    return is_satd_sub(str_comment)

def is_satd_nlp(str_comment):
    
    satd_detector = Path(__file__).parent.parent / "./lib/SATDDetectorClient.jar"
    p = Popen(['java', '-jar', satd_detector, str_comment], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate(b"input data that is passed to subprocess' stdin")
    rc = p.returncode
    
    return str(output).rfind("true") > 0

def load_strings():
    input_path = Path(__file__).parent.parent / "./lib/satd_patterns.txt"
    with open(input_path, "r") as the_file:
        patterns = the_file.read().split("\n")
    
    return patterns

def is_satd_sub(str_comment):
    patterns = load_strings()

    for p in patterns:
        if(str(str_comment).lower().count(p.lower()) > 0):
            return True
    
    return False

def get_satd_str(str_comment):
    patterns = load_strings()

    for p in patterns:
        if(str(str_comment).lower().count(p.lower()) > 0):
            return p
    
    return ""
            