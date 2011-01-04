#
# Recommendation with LDA (Latent Dirichret Allocation) On-Line Inference 
#
import sys
import getopt
import random

from lda_online_inference import OLDA

class Vector:
    def __init__(self, vid,  vector, threshold=0.15):
        self.vid = vid

        for i in range(len(vector)):
            if vector[i] > threshold:
                vector[i] = 1
            else:
                vector[i] = 0

        self.v = vector

    def __cmp__(self, other):
        return cmp(self.v, other.v)

    def __str__(self):
        return str(self.v) + "\t" + str(self.vid)

class ShuffleVectors:

    def __init__(self, vectors, adj=5, th=0.1):
        self.threshold = th
        self.adj   = adj    
        self.vects = vectors
        self.index = self.__suffule_index(len(vectors[0]))  # index of shuffled row
        self.shuffled_vects = self.__create_shufflled_vectors()

    def get_similar_vectors(self, target_vector):
        mapped_vector = self.__create_mapped_vector(target_vector)
        ids = self.__get_adjacency_vector_ids(mapped_vector)
        return ids

    def __get_adjacency_vector_ids(self, mapped_vector):
        target_id = self.__search_target_id(mapped_vector, 0, len(self.shuffled_vects))         
        
        ids   = []
        start = target_id - self.adj
        start = start if start > 0 else 0
        end   = target_id + self.adj
        end   = end if end < len(self.shuffled_vects) else len(self.shuffled_vects)

        for i in range(start, end):
            ids.append(self.shuffled_vects[i].vid)

        return ids

    def __suffule_index(self, topic_size):
        index = range(0, topic_size)
        random.shuffle(index)  # shuffle the index itself
        return index 

    def __create_shufflled_vectors(self):
        rt_shuffuled_vects = []
        for vi in range(len(self.vects)):
            rt_shuffuled_vects.append(self.__create_mapped_vector(self.vects[vi] , vi))

        rt_shuffuled_vects.sort()
        return rt_shuffuled_vects

    def __create_mapped_vector(self, target_vector, vector_id=-1): # -1 for inference items
        vec = []
        for i in self.index: # append in shuffuled index order
            vec.append(target_vector[i])

        return Vector(vector_id, vec, self.threshold)
        
    def __search_target_id(self, mapped_vect, low, high):
        if low >= high: # termination case (no identical vector)
            return high
        
        middle = (low + high) / 2 

        if mapped_vect == self.shuffled_vects[middle] :  
            return middle
        elif mapped_vect < self.shuffled_vects[middle]: 
            return self.__search_target_id(mapped_vect, low, middle-1)
        else: 
            return self.__search_target_id(mapped_vect, middle+1, high)

class Recommend:

    def __init__(self, model_prefix='model', riter=10):
        self.olda = OLDA()
        self.olda.load_model(model_prefix)
        self.examples           = self.olda.resource_pool.examples
        self.shuffle_iteration  = riter
        self.user_topic_vectors = self.report_theta() 
        self.shufflled_user_topic_vectors = []
        self.user_items         = [] 
        self.blocks = self.olda.make_block_list()

        # get shuffuled vectors
        for i in range(riter):
            self.shufflled_user_topic_vectors.append(ShuffleVectors(self.user_topic_vectors))
    

    def report_theta(self):
        theta = []  
        for m, line in enumerate(open(self.olda.model_prefix+'.theta', 'r')): # iterate number of traning examples
            vals = line[:].rstrip().split(" ")
            theta.append(map(float, vals))

        return theta

    def innerproduct(self, vec_one, vec_two):
        ip = 0
        for i in range(len(vec_one)):
            if vec_one[i] in vec_two:
                ip += 1

        return ip

    def get_recommend_items(self, line):
        items  = {}
        target_uid_str, words_str = line[:].rstrip().split("\t")
        target_uid = int(target_uid_str)
        uvecter   = self.olda.inference(line, 1000)   # online learning
        wvecter   = self.olda.new_resource_pool.examples[0] # need rewrite...
        sim_users = self.__get_similar_users(uvecter) # get the users who have the same interest as the input user

        for uid in sim_users:
            titems = self.__get_items(uid)
            if self.innerproduct(wvecter, titems) < 1:
                continue
                
            for item in titems:
                if not items.has_key(item):
                    items[item] = 0
                items[item] += 1

        rt_items = []
        #item_list = items.keys()
        #print "\titem_list:",item_list
        i = 0

        for itm, count in items.items():
            if (itm in wvecter) or (itm in self.__get_items(target_uid)):
                continue

            if i > 20:
                break

            if not self.blocks.has_key(itm):
                rt_items.append(itm)

            i += 1
        
        return rt_items
                    
    def __get_similar_users(self, uvecter):
        susers = []
        for i in range(self.shuffle_iteration):
            tlist = self.shufflled_user_topic_vectors[i].get_similar_vectors(uvecter)
            susers = susers + tlist
        
        return list(set(susers)) # uniq

    def __get_items(self, user_id):
        return self.examples[user_id].features
    
if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 
                                      "i:m:a:b:r:", 
                                      longopts=["input_file", 
                                                "model_prefix", 
                                                "iterations"])
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

    recommend = Recommend(model_prefix)

    print "run recommendation with on line lda"
    for m, line in enumerate(open(input_file, 'r')):
        print recommend.get_recommend_items(line)

#
