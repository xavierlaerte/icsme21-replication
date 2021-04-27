from github import Github

class Issue:
    def __init__ (self, title, body, labels):
        self.title = title
        self.body = body
        self.labels = labels
    
    def publish(self, repository):
        repository.create_issue(title=self.title.text, body=self.body.text, labels=self.labels)
    
    def append(self, another_issue):
        self.body = self.body.append_body(another_issue)
    
    def is_equal(self, another_issue):
        return self.title.text == another_issue.title.text