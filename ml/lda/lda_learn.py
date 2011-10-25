#
# LDA (Latent Dirichret Allocation) learner 
#
import sys
import getopt
import random

import lda

if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 
                                      "i:m:a:b:r:n:", 
                                      longopts=["input_file", "model_prefix",
                                                "alpha", "beta", "iterations",
                                                "topic_num"])
    except getopt.GetoptError:
        sys.exit(0)

    input_file    = "train"
    model_prefix  = "model"
    alpha         = 2
    beta          = 0.5
    iterations    = 100    
    num_of_topics = 2

    for opt, arg in optlist:
        if opt in ("-i", "--input_file"):
            input_file = arg
        elif opt in ("-m", "--model_prefix"):
            model_prefix = arg
        elif opt in ("-a", "--alpha"):
            alpha = float(arg)
        elif opt in ("-b", "--beta"):
            beta  = float(arg)
        elif opt in ("-r", "--iterations"):
            iterations  = int(arg)
        elif opt in ("-n", "--topic_num"):
            num_of_topics = int(arg)

    lda = lda.LDA()
    print "run estimation"
    lda.estimate(input_file, alpha, beta, num_of_topics, model_prefix, iterations)
