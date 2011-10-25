#
# LDA (Latent Dirichret Allocation) Inference 
#
import sys
import getopt

import lda

if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 
                                      "i:m:a:b:r:", 
                                      longopts=["input_file", "model_prefix",
                                                "alpha", "beta", "iterations"])
    except getopt.GetoptError:
        sys.exit(0)

    input_file   = "test"
    model_prefix = "model"
    alpha        = 2
    beta         = 0.5
    iterations   = 100    

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

    ilda = lda.InfLDA()
    print "run inference"
    theta = ilda.inference(input_file, model_prefix, iterations)
    print "theta: ",theta
