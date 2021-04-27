from core.satd_finder import *

class Issue_Title:
    def __init__(self):
        self.text = ""
    
    def create_title(self, comment):
        
        patterns = load_strings()

        title = self.get_satd_line(comment)[0].strip()
        first_place = title.split(" ")[0]
        remove = ["*", "//", "/*", "#", "**"]

        if(first_place in remove):
            title = title.replace(first_place, "", 1).strip()
            
        title_list = title.split(" ")
        if(len(title_list) <= 2):
            return title

        first_place = title_list[0]
        for p in patterns:
            if(first_place.lower().count(p.lower()) > 0):
                title = title.replace(first_place, "", 1).strip()
        
        backup = (title + ".")[:-1]
        first_place = title.split(" ")[0]
        while(len(first_place) < 3):
            title = title.replace(first_place, "", 1).strip()
            first_place = title.split(" ")[0]

        if(len(title.split(" ")) < 1):
            self.text = backup.capitalize()
        else:
            self.text = title.capitalize()

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

    def set_title(self, str_title):
        self.text = str_title