class WikiNode(object):
    def __init__(self, namein, textin, descriptin=None, distractin=[]):
        self.title = namein
        self.text = textin
        self.descript = descriptin
        self.distract = distractin
        self.children = []
        
    def addchild(self, new_child):
        self.children.append(new_child)