from comments_finder import *
from satd_finder import *


def analyze(repo_path):
    print("Retrieving Comments")
    #find all comments in clonned repository
    comments, read = find_comments(repo_path)
    print(comments)

    print("Analyzing SATD")
    #filter satd comments from a list of comments
    satd = identify_stad(comments)

    return satd
