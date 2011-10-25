#
# SMO (Sequential Minimal Optimization) algorithm
#
import sys
import random

VERBOSE = 1

class SMO:

    def kernel(self, i1, i2):
        # TODO
        # - define other kernels
        return self.dot_product(i1, i2) #Dot product x*y
    
    def dot_product(self,i1, i2):
        dot = 0.0
        for index, val in self.training_data[i1].feature.iteritems():
            #print "index=",index,"\tval=",val
            if self.training_data[i2].feature.has_key(index):
                dot += val * self.training_data[i2].feature[index]
        #print "dot_product: ",dot
        return dot

    def __init__(self, training_file):
        self.alpha         = []
        self.threshold     = 0
        self.cost          = 0.1
        self.tolerance     = 0.01 #Tolerance in KKT condition
        self.errors        = []
        self.training_data = self.create_training_data(training_file)
        self.end_support   = len(self.training_data)
        self.run_train()
        self.save_model()
    
    def save_model(self):
        for i,v in enumerate(self.alpha):
            if abs(v) <= self.tolerance:
                continue

            sys.stdout.write(str(v * self.training_data[i].label) + " ")
            for fid, val in self.training_data[i].feature.iteritems():
                sys.stdout.write(str(fid)+ ":" + str(val) + " ")
            sys.stdout.write("\n")

        print self.threshold

    def learned_func(self, id):
        s = 0.0
        for i in range(0, len(self.alpha)):
            if(self.alpha[i] > 0): 
                s += self.alpha[i] * self.training_data[i].label * self.kernel(i,id)
        s -= self.threshold
        #print "learned_func: s=",s
        return s

    def create_training_data(self, training_file):
        training_data = []
        for line in open(training_file, 'r'):
            training_data.append(TrainingExample(line))
        return training_data

    def run_train(self):
        numChanged = 0
        examineAll = 1
        while (numChanged > 0) or (examineAll == 1):
            numChanged = 0
            if examineAll == 1:
                # loop all the training items
                for i,t in enumerate(self.training_data):
                    numChanged += self.examineExample(i)
            else:
                # loop training items over example where alpha is not 0 & [0 < alpha < C]
                for i,t in enumerate(self.training_data):
                    if (self.alpha[i] != 0) and (self.alpha[i] != self.cost):
                        numChanged += self.examineExample(i)
                
            if examineAll == 1:
                examineAll = 0
            elif numChanged == 0:
                examineAll = 1

    def select_by_huristics(self, e1):
        i2   = -1
        tmax = 0
        for i in range(0, self.end_support):
            if((self.alpha[i] > 0) and (self.alpha[i] < self.cost)):
                e2  = self.errors[i]
                tmp = abs(e1 - e2)
                if tmp > tmax:
                    tmax = tmp
                    i2   = i
        return i2
        
    def examineExample(self, i1):
        t1     = self.training_data[i1]
        y1     = t1.label
        alpha1 = self.alpha[i1]
        e1 = 0.0
        if alpha1 > 0 and alpha1 < self.cost:
            e1 = self.errors[i1]
        else:
            e1 = self.learned_func(i1) - y1 

        r1 = y1 * e1
        #print "e1=",e1,"\tr1=",r1,"\ty1=",y1
        if (r1 < -self.tolerance and alpha1 < self.cost) or ((r1 > self.tolerance) and (alpha1 > 0)):
            #print "Try to find suitable example LM (index i2)"
            #Try to find suitable example LM (index i2)

            # 1. Try boundary points with the largest difference |E1 - E2|
            i2 = self.select_by_huristics(e1)
            if i2 > 0:
                #print "optimize1"
                if self.optimize(i1, i2):
                    return 1
            
            # 2. Try all boundary points
            k0 = int(random.random() * self.end_support) # random returns 0.0 <= F < 1.0
            k = k0 * self.end_support
            for id in range(k, (self.end_support+k0)-1): # rewrite by iterator!!!
                i2 = id % self.end_support
                #print "k=",k
                #print "self.alpha[k]: ",self.alpha[k]
                if self.alpha[k] > 0 and self.alpha[k] < self.cost:
                    #print "optimize2"
                    if self.optimize(i1, i2):
                        return 1

            # 3. Try the entire set
            k0 = int(random.random() * self.end_support) # random returns 0.0 <= F < 1.0
            k = k0 * self.end_support
            #print "k=",k,"\tk0=",k0,"\tend_support=",self.end_support

            for id in range(k, (self.end_support+k0)):
                i2 = id % self.end_support
                #print "optimize3"
                if self.optimize(i1, i2):
                    return 1
        return 0 
        
    def optimize(self, i1, i2):
        #print "i1: ",i1,"\ti2: ",i2
        t1 = self.training_data[i1]
        t2 = self.training_data[i2]
        y1 = t1.label
        y2 = t2.label
        a1o = self.alpha[i1]
        a2o = self.alpha[i2]

        if ((a1o > 0) and (a1o < self.cost)): 
            e1 = self.errors[i1]
        else:
            e1 = self.learned_func(i1) - y1
            
        if ((a2o > 0) and (a2o < self.cost)): 
            e2 = self.errors[i2]
        else:
            e2 = self.learned_func(i2) - y2
            
        s = t1.label * t2.label
        # Computation of L and H, low and high end a2n on line segment            
        sum = 0
        L   = 0
        H   = 0
        if t1.label == t2.label:
            sum = a1o + a2o
            if sum > self.cost:
                L =  sum - self.cost
                H =  self.cost
            else: 
                L = 0
                H = sum
        else:
            diff = a1o - a2o
            if diff > 0:
                L = 0
                H = self.cost - diff
            else:
                L = -diff
                H = self.cost

        #print "L=",L,"\tH=",H
        if L == H:
            #print "return 0 since L == H"
            return 0

        # Computation of eta
        k11 = self.kernel(i1, i1)
        k22 = self.kernel(i2, i2)
        k12 = self.kernel(i1, i2)
        #print "k11: ",k11,"\tk22",k22,"\tk12:",k12
        eta = 2 * k12 - k11 - k22 #Computation of eta from kernel
        #print "eta=",eta
        a2n = 0.0
        #print "a2o = ",a2o,"\te1=",e1,"\te2",e2
        if eta < -0.01:
            a2n = float(a2o) + float(y2) * (float(e2) - float(e1)) / float(eta)
            #print "when eta < 0.01 :a2n=",a2n
            if a2n < L:
                a2n = L
            elif a2n > H:
                a2n = H
        else: 
            c1 = eta/2
            c2 = y2 * (e1-e2) - eta * a2o
            lobj = c1 * L * L * c2 * L
            hobj = c1 * H * H + c2 * H
            if lobj > hobj + self.tolerance:
                a2n = L
            elif lobj < hobj - self.tolerance:
                a2n = H
            else: 
                a2n = a2o
        
        #print "a2n=",a2n
        if abs(a2n - a2o) < (self.tolerance * (a2n + a2o + self.tolerance)):  
            #print "return 0 abs(a2n - a2o) < (self.tolerance * (a2n + a2o + self.tolerance))"
            return 0
            
        a1n = a1o - s * (a2n - a2o)
        if a1n < 0:
            a2n += s * a1n
            a1n = 0
        elif a1n > self.cost:
            a2n += s * (a1n - self.cost)
            a1n = self.cost
            
        # Update threshold b to reflect change in a
        bnew = self.threshold
        if (a1n > 0) and (a1n < self.cost):
            bnew = self.threshold + e1 + y1 * (a1n - a1o) * k11 + y2 * (a2n - a2o) * k12
        else:
            b1 = self.threshold + e1 + y1 * (a1n - a1o) * k11 + y2 * (a2n - a2o) * k12
            b2 = self.threshold + e2 + y1 * (a1n - a1o) * k12 + y2 * (a2n - a2o) * k22
            bnew = (b1 + b2) / 2
        deltab = bnew - self.threshold
        self.threshold = bnew
    
        # Update e vector
        t1 = y1 * (a1n - a1o)
        t2 = y2 * (a2n - a2o) 
        for i in range(0,self.end_support):
            if 0 < self.alpha[i] and self.alpha[i] < self.cost:
                self.errors[i] += t1 * self.kernel(i1,i) + t2 * self.kernel(i2,i) - deltab
            
        # update alphas and errors 
        # #print "a1n=",a1n,"\ta2n=",a2n
        self.errors[i1] = 0.0
        self.errors[i2] = 0.0
        self.alpha[i1]  = a1n #Store the optimized pair of LMs
        self.alpha[i2]  = a2n
        #print "return 1 since success"
        return 1 #Success!
                 
class TrainingExample:
    def __init__(self, line):
        rows  = line[:-1].split(" ")
        self.label   = int(rows.pop(0))
        self.feature = {}
        for feature_str in rows:
            id, value = feature_str.split(":")
            self.feature[id] = float(value)

if __name__ == '__main__':
    smo = SMO('test_training.txt')
