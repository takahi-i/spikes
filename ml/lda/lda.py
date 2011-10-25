#
# LDA (Latent Dirichret Allocation) 
#
import sys
import getopt
import random

import example
import util

#
# contains the temporal results of lda leanring
#
class LDAResourcePool:
    def __init__(self):
        self.examples      = []  # list of Example objects
        self.word_topics   = []  # topic assignments for each word (word_topics[m][n] = topic).  ==z==
        self.nword_topics  = []  # number of instances of word i (term?) assigned to topic k. ==nw==
        self.nd_topics     = []  # number of words in document i assigned to topic j. ==nd==
        self.nw_sum        = []  # total number of words assigned to topic j
        self.nd_sum        = []  # total number of words in document i
        self.num_of_words  = 0   # vocabulary size
        self.num_of_docs   = 0   # number of input examples
#
# LDA for learning
#
class LDA:
    def __init__(self):
        self.alpha         = 0    # Symmetric Dirichlet parameter (document--topic associations)       
        self.beta          = 0.0  # Dirichlet parameter (topic--term associations)
        self.numstats      = 0    # size of statistics
        self.thin_interval = 10   # sampling lag (?)
        self.burn_in       = 100  # burn-in period
        self.iterations    = 1000 # max iterations
        self.sample_lag    = 10   # sample lag (if -1 only one sample taken)
        self.model_prefix  = "model"
        self.dispcol       = 0    # 
        self.theta_sum     = []   # cumulative statistics of theta 
        self.phi_sum       = []   # cumulative statistics of phi   
        self.resource_pool = LDAResourcePool()     # for resouce pooling for traning
        random.seed()

    def estimate(self, input_file, alpha, beta, num_of_topics, model_prefix="model", iterations=1000):
        self.alpha = alpha
        self.beta  = beta
        self.num_of_topics = num_of_topics
        self.model_prefix  = model_prefix
        self.iterations    = iterations
        self.resource_pool.examples     = self.load_examples(input_file)         
        self.resource_pool.num_of_words = self.__return_max_word_id()

        # init parameters
        if self.sample_lag > 0:
            self.theta_sum  = [[0.0 for j in range(self.num_of_topics) ] for i in range(len(self.resource_pool.examples)) ]
            self.phi_sum    = [[0.0 for j in range(self.resource_pool.num_of_words) ]  for i in range(self.num_of_topics) ]
            self.numstats = 0;

        # init markov chain        
        self.init_state() 
        self.gibbs()
        print self.report_theta()
        self.save_models()


    def load_examples(self, input_file):
        examples = []
        for line in open(input_file, 'r'):
            examples.append(example.Example(line))

        return examples

    def __return_max_word_id(self):
        max_id = 0
        for m in range(len(self.resource_pool.examples)):
            for n in range(len(self.resource_pool.examples[m])):
                if max_id < self.resource_pool.examples[m][n]:
                    max_id = self.resource_pool.examples[m][n]
        return  max_id + 1 #

    def init_state(self):
        i = 0
        M = len(self.resource_pool.examples)
        self.resource_pool.nword_topics = [[0 for j in range(self.num_of_topics) ] \
                                               for i in range(self.resource_pool.num_of_words) ]
        self.resource_pool.nd_topics    = [[0 for j in range(self.num_of_topics) ] for i in range(M) ]
        self.resource_pool.nw_sum  =  [0 for i in range(self.num_of_topics) ]
        self.resource_pool.nd_sum  =  [0 for i in range(M) ]

        # The self.resource_pool.word_topics[i] are are initialised to values in [1,K] to determine the
        # initial state of the Markov chain.
        self.resource_pool.word_topics = [0 for i in range(M)]
        for m in range(M):
            N = len(self.resource_pool.examples[m])
            self.resource_pool.word_topics[m] = [0 for i in range(N) ]
            for n in range(N):
                topic = int(random.random() * self.num_of_topics) # ~Mult(1/K)
                self.resource_pool.word_topics[m][n] = topic # z_m_n
                # number of instances of word i assigned to topic j 
                self.resource_pool.nword_topics[self.resource_pool.examples[m][n]][topic] +=1
                # number of words in document i assigned to topic j
                self.resource_pool.nd_topics[m][topic] +=1  # (==nd==) document*topic += 1
                # total number of words assigned to topic j.            
                self.resource_pool.nw_sum[topic] +=1  
                self.resource_pool.nd_sum[m]     = N  

    def gibbs(self):
        # run
        for i in range(self.iterations):
            for m in range(self.num_of_topics):
                for n in range(len(self.resource_pool.word_topics[m])):
                    # sample the topic for the word in m-th document at n-th position
                    self.resource_pool.word_topics[m][n] = self.__sampleFullConditional(m, n) 

            if (i < self.burn_in)  and  (i % self.thin_interval == 0):
                self.dispcol += 1

            # get statistics after burn-in
            if ((i > self.burn_in)  and  (self.sample_lag > 0)  and  (i % self.sample_lag == 0)):
                self.__update_parameters()
                if (i % self.thin_interval != 0):
                    self.dispcol += 1

            #  display progress
            if ((i > self.burn_in) and (i % self.thin_interval == 0)):
                self.dispcol+=1

            if (self.dispcol >= 100):
                self.dispcol = 0
        
        self.__update_parameters()


    def report_theta(self):
        print "report theta in LDA"
        theta = [[0 for j in range(self.num_of_topics) ] for i in range(len(self.resource_pool.examples)) ]
        if self.sample_lag > 0:
            for m in range(len(self.resource_pool.examples)):
                for k in range(self.num_of_topics):
                    if self.numstats != 0:
                        theta[m][k] = self.theta_sum[m][k] / self.numstats
        else:
            for m in range(len(self.resource_pool.examples)):
                for k in range(self.num_of_topics):
                    theta[m][k] = (self.resource_pool.nd_topics[m][k] + self.alpha) \
                        / (self.resource_pool.nd_sum[m] + self.num_of_topics * self.alpha);

        return theta

    def report_phi(self):
        phi = [[0 for j in range(self.resource_pool.num_of_words) ] for i in range(self.num_of_topics) ]
        if self.sample_lag > 0:
            for k in range(self.num_of_topics):
                for w in range(self.resource_pool.num_of_words):
                    if self.numstats != 0:
                        phi[k][w] = self.phi_sum[k][w] / self.numstats;
        else:
            for k in range(self.num_of_topics):
                for w in range(self.resource_pool.num_of_words):
                    phi[k][w] = (self.resource_pool.nword_topics[w][k] + self.beta) \
                        / (self.resource_pool.nw_sum[k] + self.resource_pool.num_of_words * self.beta)
        return phi

    def get_theta(self):
        theta = [[0 for i in range(len(self.resource_pool.examples)) ] for i in range(self.num_of_topics) ]
        if self.sample_lag > 0:
            for m in range(len(self.resource_pool.examples)):
                for k in self.num_of_topics:
                    theta[m][k] = self.theta_sum[m][k] / self.numstats
        else:
            for m in range(len(self.resource_pool.examples)):
                for k in self.num_of_topics:
                    theta[m][k] = (self.resource_pool.nd_topics[m][k] + self.alpha) \
                        / (self.resource_pool.nd_sum[m] + self.num_of_topics * self.alpha)

        return theta

    def save_models(self):
        # save theta
        f     = open(self.model_prefix+'.theta' , 'w')
        theta = self.report_theta()
        for th in theta:
            for th_z in th:
                f.writelines(str(th_z)+" ")
            f.writelines("\n")
        f.close()
        # save phi
        f   = open(self.model_prefix+'.phi' , 'w')
        phi = self.report_phi()
        for p in phi:
            for p_w in p:
                f.writelines(str(p_w)+" ")        
            f.writelines("\n")
        f.close()

        # save word_topics
        f = open(self.model_prefix+'.examples' , 'w')
        for m in range(len(self.resource_pool.word_topics)):
            for n in range(len(self.resource_pool.word_topics[m])):
                f.writelines(str(self.resource_pool.examples[m][n]) + ":" + str(self.resource_pool.word_topics[m][n]) + " ")
            f.writelines("\n")
        f.close

        # save global settings
        f = open(self.model_prefix+'.global' , 'w')
        f.writelines("number of topic:" + str(self.num_of_topics) + "\n")
        f.writelines("number of words:" + str(self.resource_pool.num_of_words)  + "\n")
        f.writelines("number of documents:" + str(len(self.resource_pool.examples))  + "\n")
        f.writelines("alpha:" + str(self.alpha)  + "\n")
        f.writelines("beta:" + str(self.beta)  + "\n")        
        f.close

    def __update_parameters(self):
        for m in range(len(self.resource_pool.examples)):
            for k in range(self.num_of_topics):
                self.theta_sum[m][k] += float(self.resource_pool.nd_topics[m][k] + self.alpha) \
                    / (self.resource_pool.nd_sum[m] + self.num_of_topics * self.alpha)
        
        for k in range(self.num_of_topics):
            for v in range(self.resource_pool.num_of_words):
               self.phi_sum[k][v] += float(self.resource_pool.nword_topics[v][k] + self.beta) \
                   / (self.resource_pool.nw_sum[k] + self.resource_pool.num_of_words * self.beta)

        self.numstats +=1

    def __sampleFullConditional(self, m, n):
        # remove z_i from the count variables
        topic = self.resource_pool.word_topics[m][n]
        self.resource_pool.nword_topics[self.resource_pool.examples[m][n]][topic] -= 1
        self.resource_pool.nd_topics[m][topic] -=1
        self.resource_pool.nw_sum[topic]       -=1
        self.resource_pool.nd_sum[m]           -=1

        # do multinomial sampling via cumulative method:
        p = [0 for i in range(self.num_of_topics) ]
        for k in range(self.num_of_topics):
            p[k] = (self.resource_pool.nword_topics[self.resource_pool.examples[m][n]][k] + self.beta) \
                / (self.resource_pool.nw_sum[k] + self.resource_pool.num_of_words * self.beta) \
                * (self.resource_pool.nd_topics[m][k] + self.alpha) / (self.resource_pool.nd_sum[m] \
                                                                           + self.num_of_topics * self.alpha)
        
        # cumulate multinomial parameters
        for k in range(1,len(p)):
            p[k] += p[k-1]

        # scaled sample because of unnormalised p[]
        u = random.random() * p[self.num_of_topics - 1]
        for topic in range(self.num_of_topics):
            if u < p[topic]:
                break

        # add newly estimated z_i to count variables
        self.resource_pool.nword_topics[self.resource_pool.examples[m][n]][topic]+=1
        self.resource_pool.nd_topics[m][topic] +=1
        self.resource_pool.nw_sum[topic]       +=1
        self.resource_pool.nd_sum[m]           +=1
        return topic


#
# lda for inference
#
class InfLDA(LDA):

    def __init__(self):
        LDA.__init__(self)
        self.new_resource_pool = LDAResourcePool() # for resouce pooling for inference
    
    def inference(self, input_file, model_prefix="model", iterations=100):
        self.load_model(model_prefix)
        self.load_infer_examples(self.load_examples(input_file) )
        
        for inf_liter in range(iterations):
            for m in range(len(self.new_resource_pool.examples)):
                for n in range(len(self.new_resource_pool.examples[m])):
                    self.new_resource_pool.word_topics[m][n] = self.inf_sampling(m, n)
                    
        return self.compute_newtheta()

    def compute_newtheta(self):
        new_theta = [[0 for i in range(self.num_of_topics) ] for i in range(len(self.new_resource_pool.examples)) ]        
        for m in range(len(self.new_resource_pool.examples)):
            for k in range(self.num_of_topics):
                new_theta[m][k] = (self.new_resource_pool.nd_topics[m][k] + self.alpha) \
                    / (self.new_resource_pool.nd_sum[m] + self.num_of_topics * self.alpha)
        return new_theta
            
    def inf_sampling(self, m, n):
        topic = self.new_resource_pool.word_topics[m][n]
        w     = self.new_resource_pool.examples[m][n]
        self.new_resource_pool.nword_topics[w][topic] -= 1
        self.new_resource_pool.nd_topics[m][topic] -=1
        self.new_resource_pool.nw_sum[topic]       -=1
        self.new_resource_pool.nd_sum[m]           -=1        
        
        Vbeta  = self.resource_pool.num_of_words * self.beta
        Kalpha = self.num_of_topics * self.alpha

        # do multinomial sampling via cumulative method  
        p = [0 for i in range(self.num_of_topics) ]
        for k in range(self.num_of_topics): 
            p[k] = float((self.resource_pool.nword_topics[w][k] + self.new_resource_pool.nword_topics[w][k] + self.beta)) \
                / (self.resource_pool.nw_sum[k] + self.new_resource_pool.nw_sum[k] + Vbeta) \
                * (self.new_resource_pool.nd_topics[m][k] + self.alpha) / (self.new_resource_pool.nd_sum[m] + Kalpha);
        
        # cumulate multinomial parameter
        for k in range(1,len(p)):
            p[k] += p[k-1]

        # scaled sample because of unnormalised p[]
        u = random.random() * p[self.num_of_topics - 1]
        for topic in range(self.num_of_topics):
            if u < p[topic]:
                break

        # add newly estimated z_i to count variables        
        self.new_resource_pool.nword_topics[w][topic] +=1
        self.new_resource_pool.nd_topics[m][topic] +=1
        self.new_resource_pool.nw_sum[topic]       +=1
        self.new_resource_pool.nd_sum[m]           +=1
        
        return topic

    def load_model(self, model_prefix): 
        # load global settings
        self.model_prefix = model_prefix
        for m, line in enumerate(open(self.model_prefix+'.global', 'r')):
            tag, val = line[:-1].split(":")
            if tag == "number of topic":
                self.num_of_topics = int(val)
            elif tag == "number of words":
                self.resource_pool.num_of_words  = int(val)
            elif tag == "number of documents":
                self.resource_pool.num_of_docs  = int(val) 
            elif tag == "alpha":
                self.alpha  = float(val)
            elif tag == "beta":
                self.beta   = float(val)           

        # load trained examples 
        self.resource_pool.word_topics = [0 for i in range(self.resource_pool.num_of_docs)]
        for m, line in enumerate(open(self.model_prefix+'.examples', 'r')):
            rows  = line[:-2].split(" ")
            self.resource_pool.word_topics[m] = [0 for i in range(len(rows))]
            self.resource_pool.examples.append(example.LearnedExample(len(rows)))
            for n, r in enumerate(rows):
                w, t =  r.split(":")
                self.resource_pool.word_topics[m][n] = int(t)
                self.resource_pool.examples[m][n]    = int(w)
                
        # init nword_topic
        self.resource_pool.nword_topics = [[0 for j in range(self.num_of_topics) ] \
                                               for i in range(self.resource_pool.num_of_words) ]
        # init nd_topics
        self.resource_pool.nd_topics = [[0 for j in range(self.num_of_topics) ] \
                                            for i in range(self.resource_pool.num_of_docs) ]
        # init nw_sum
        self.resource_pool.nw_sum  =  [0 for i in range(self.num_of_topics) ]
        # init nd_sum
        self.resource_pool.nd_sum  =  [0 for i in range(self.resource_pool.num_of_docs) ]
        
        for m in range(self.resource_pool.num_of_docs):
            for n in range(len(self.resource_pool.examples[m])):
                topic = self.resource_pool.word_topics[m][n]
                # number of instances of word i assigned to topic j
                self.resource_pool.nword_topics[self.resource_pool.examples[m][n]][topic] += 1
                # number of words in document i assigned to topic j
                self.resource_pool.nd_topics[m][topic] += 1
                # total number of words assigned to topic j                
                self.resource_pool.nw_sum[topic] += 1        
            self.resource_pool.nd_sum[m] += len(self.resource_pool.examples[m])

    def load_infer_examples(self, examples): 
        # load new (testing) data for inference
        self.new_resource_pool.examples     = examples
        self.new_resource_pool.nword_topics = [[0 for j in range(self.num_of_topics) ] \
                                                   for i in range(self.resource_pool.num_of_words) ]
        self.new_resource_pool.nd_topics    = [[0 for j in range(self.num_of_topics) ] \
                                                   for i in range(len(self.new_resource_pool.examples)) ]
        self.new_resource_pool.nw_sum       = [0 for i in range(self.num_of_topics) ]
        self.new_resource_pool.nd_sum       = [0 for i in range(len(self.new_resource_pool.examples)) ]
        self.new_resource_pool.word_topics  = [0 for i in range(len(self.new_resource_pool.examples))]

        for m in range(len(self.new_resource_pool.examples)):
            self.new_resource_pool.word_topics[m] = [0 for i in range(len(self.new_resource_pool.examples[m]))]
            for n in range(len(self.new_resource_pool.examples[m])):
                w = self.new_resource_pool.examples[m][n]
                topic = int(random.random() / self.num_of_topics)
                self.new_resource_pool.word_topics[m][n] = topic   # new_z
                self.new_resource_pool.nword_topics[w][topic] += 1 # new_nw
                self.new_resource_pool.nd_topics[m][topic]    += 1 # new_nd
                self.new_resource_pool.nw_sum[topic] += 1
            self.new_resource_pool.nd_sum[m] = len(self.new_resource_pool.examples[m])
