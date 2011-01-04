#
# LDA (Latent Dirichret Allocation) On-Line Inference 
#
import sys
import getopt

from lda import InfLDA
from example import Example

#
# Online Inference based on LDA 
#
class OLDA(InfLDA):
    
    def __init__(self):
        InfLDA.__init__(self)
    
    def inference(self, line, iterations=10000):
        user_id_str, new_words = self.__parse_line(line)
        words_history          = self.__create_updated_words(int(user_id_str), new_words)
        self.online_load_example(words_history)

        for inf_liter in range(iterations):
            for m in range(len(self.new_resource_pool.examples)): # always m=1
                for n in range(len(self.new_resource_pool.examples[m])):
                    self.new_resource_pool.word_topics[m][n] = self.inf_sampling(m, n) 

        return self.compute_newtheta()[0] # todo rewrite...

    def online_load_example(self, line): 
        # load updated data for inference
        example_list = [Example(line)]

        #print "Example(line)",Example(line)
        return self.load_infer_examples(example_list)

    def make_block_list(self): 
        words = {}
        for m in range(self.resource_pool.num_of_docs):
            for n in range(len(self.resource_pool.examples[m])):
                w = self.resource_pool.examples[m][n]
                if not words.has_key(w):
                    words[w] = 0
                words[w] += 1

        rt_words = {}
        word_list = words.keys()
        for w in word_list:
            if words[w] > 8:
                rt_words[w] = words[w]

        return rt_words
        
    def __parse_line(self, line):
        uid, words_str = line[:-1].split("\t")
        return (uid, words_str.split(" "))
    
    def __create_updated_words(self, user_id, new_words, window_size=4):
        target_example = self.resource_pool.examples[user_id]
        document_size  = len(target_example)
        start_position = document_size-window_size

        rt_words = []
        for i in range(start_position , document_size):
            rt_words.append(str(target_example[i]))

        for i in range(len(new_words)):
            rt_words.append(new_words[i])

        #print "made vector", rt_words
        return " ".join(rt_words)

if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 
                                      "i:m:a:b:r:", 
                                      longopts=["input_file", "model_prefix", "iterations"])
    except getopt.GetoptError:
        sys.exit(0)

    input_file   = "online_test"
    model_prefix = "model"
    iterations   = 100

    for opt, arg in optlist:
        if opt in ("-i", "--input_file"):
            input_file = arg
        elif opt in ("-m", "--model_prefix"):
            model_prefix = arg
        elif opt in ("-r", "--iterations"):
            iterations  = int(arg)

    print "run online inference"
    for m, line in enumerate(open(input_file, 'r')):
        olda = OLDA()
        olda.load_model(model_prefix)
        print olda.inference(line)
