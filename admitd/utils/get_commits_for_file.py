from pydriller import RepositoryMining
from pathlib import Path

def get_important_files(str_path, percent):
    c_files = {}
    commits = 0
    commit_modifications = 0 
    for commit in RepositoryMining(str_path).traverse_commits():
        commits += 1
        for mod in commit.modifications:
            commit_modifications += 1
            path = mod.old_path
            if(path == None):
                path = mod.new_path
            complete_path = str_path + "/" + path
            if(c_files.get(complete_path) == None):
                c_files[complete_path] = 1
            else:
                c_files[complete_path] = c_files[complete_path] + 1

    #print(sorted(c_files.items(), key = lambda x: x[1], reverse=True))
    #print(int(commits*0.8))

    up = int(commit_modifications*percent)
    ret = []
    for tuple_files in sorted(c_files.items(), key = lambda x: x[1], reverse=True):
        if(up - tuple_files[1] >= 0):
            ret.append(tuple_files[0])
            atual = tuple_files[1]
            up = up - tuple_files[1]
        else:
            up = 0
            if(tuple_files[1] == atual):
                ret.append(tuple_files[0])

    file_path = "./results/" + str_path.split("/")[-1] + "_all_commits_files.csv"
    stats_path = Path(__file__).parent.parent / file_path
    with open(stats_path, 'a') as the_file:
        for t in (c_files.items()):
            prior = False
            if(t[0] in ret): prior = True
            the_file.write(t[0] + ";" + str(t[1]) + ";" + str(prior) + "\n")
    
    return ret