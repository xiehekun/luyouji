
class NoNodeParsed(Exception):

    def __init__(self, msg=""):
        self.msg = msg

    def __str__(self):
        return self.msg

class AntiCrawler(Exception):

    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return self.msg
