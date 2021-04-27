import re
from core.satd_finder import *

class Issue_Body:

    def __init__(self):
        self.text = ""

    def get_commit_info(self, cloned_repo, td_line, in_file):
        log = cloned_repo.git.log("-L{},{}:{}".format(td_line, td_line, in_file))
        
        return self.parse_commit2(log, td_line, in_file)

    def create_body(self, cloned_repo, forked_repo, detected_file, comment):
        file_name = detected_file.split("temp/" + forked_repo.name + "/")[-1]
        commit = forked_repo.get_commits()[0]

        with open(detected_file) as f:
            count = sum(1 for _ in f)
            
        log = self.get_commit_info(cloned_repo, self.get_satd_line(comment)[1], file_name)
        pattern = get_satd_str(comment.text())
        
        body = "On {}, {} added the following **{} comment** in [{}/{}](https://github.com/{}/blob/{}/{})\n\n".format(log['date'], \
            log['author'], pattern, forked_repo.name, file_name, forked_repo.full_name, commit.sha, file_name.replace(" ", "%20"))
        
        body = body + "https://github.com/{}/blob/{}/{}#L{}-L{}".format(forked_repo.full_name, commit.sha, \
        file_name.replace(" ", "%20"), comment.line_number(), min(comment.line_number() + len(comment.text().split("\n")) + 6, count))

        body = body + "\n\nSee also the complete commit: \
            [{}](https://github.com/{}/commit/{})\n".format(log['message'], forked_repo.full_name, log['commit'])
        
        #body = body + "\n\n---\n\n###### This issue was generated to report a Technical Debt comment."
        
        self.text = body
    
    def parse_commit2(self, log_lines, td_line, in_file):
        commit = None

        data = log_lines.split("\n")
        for line in data:
            if line == '' or line == '\n':
                pass # ignore empty lines
            elif bool(re.match('commit', line, re.IGNORECASE)):
                # commit xxxx
                commit = {'commit' : re.match('commit (.*)', line, re.IGNORECASE).group(1),
                        'file' : in_file,
                        'line' : td_line}
            elif bool(re.match('author:', line, re.IGNORECASE)):
                # Author: xxxx <xxxx@xxxx.com>
                m = re.compile('Author: (.*) <(.*)>').match(line)
                commit['author'] = m.group(1)
                commit['email'] = m.group(2)
            elif bool(re.match('date:', line, re.IGNORECASE)):
                    # Date: xxx
                    date_full = line.split("   ")[1].split(" ")
                    commit['date'] = "{} {}, {}".format(date_full[1], date_full[2], date_full[4])
            elif bool(re.match('    ', line, re.IGNORECASE)):
                # (4 empty spaces)
                if commit.get('message') is None:
                    commit['message'] = line.strip()
            else:
                pass
        return commit
    
    def get_satd_line(self, comment):
        lines = comment.text().split("\n")

        if(len(lines) > 1):
            i = 0
            for line in lines:
                comment_line = comment.line_number() + i
                if is_satd_sub(line):
                    return line, comment_line
                i = i + 1

        return comment.text(), comment.line_number()
    
    def append_body(self, similar_issue):
        self.text = self.text + "\n\n\n" + similar_issue.body.text
        return self.text
    
    def set_body(self, text):
        self.text = text