#
# a classifier implementation. This classifier calssify the inputs 
# based on the model from sequential minimal optimization algorithm
#

import sys
import random

class SVMClassify:
    def __init__(self, model_file, input_file):
        self.model = Model(model_file)
        for line in open(input_file, 'r'):
           e = TestExample(line)
           print "e.label",e.label
           if (e.label == self.classify(e)):
               print "ok"
           else:
               print "miss"

    def classify(self, test_example):
        sum = 0.0
        for e in self.model.examples:
            sum += self.ip(test_example, e)
        
        print "sum = ",sum
        if sum > self.model.threshold:
            return 1
        else:
            return -1
    
    def ip(self, texample, mexample):
        dot = 0.0
        for findex, val in texample.feature.iteritems():
            if mexample.feature.has_key(findex):
                dot += (val * mexample.feature[findex])
        return mexample.weight * dot

class Model:
    def __init__(self, model_file):
        self.examples = []
        for line in open(model_file, 'r'):
            rows  = line[:-1].split(" ")
            if len(rows) > 1:
                self.examples.append(Example(rows))
            else:
                self.threshold = float(rows[0])

class TestExample:
    def __init__(self, line):
        rows  = line[:-1].split(" ")
        self.label   = int(rows.pop(0))
        self.feature = {}
        for feature_str in rows:
            id, value = feature_str.split(":")
            self.feature[id] = float(value)    

class Example:
    def __init__(self, rows):
        self.weight   = float(rows.pop(0))
        self.feature = {}
        for feature_str in rows:
            if len(feature_str) > 0:
                id, value = feature_str.split(":")
                self.feature[id] = float(value) 

if __name__ == '__main__':
    svm = SVMClassify('model.txt', "test_training.txt")
