#
# Example classes
#
class Example:

    def __init__(self, line):
        self.features = []
        rows  = line.rstrip().split(" ")
        self.features = [0 for i in range(len(rows)) ]
        for i,v in enumerate(rows):
            self.features[i]  = int(v)
            
    def __getitem__ (self, id):
        return self.features[id]

    def __len__(self):
        return len(self.features)

    def __str__(self):
        return str(self.features)

class LearnedExample(Example):

    def __init__(self, len):
        self.features = [0 for j in range(len) ]
        
    def __setitem__ (self, id, v):
        self.features[id] = int(v)
