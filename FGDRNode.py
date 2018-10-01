from Node import *
from Bitarray import *

class FGDRNode(Node):
    def __init__(self, myid, bufferSize, dump_policy, winLength, interval, m_jump):
        self.myid = myid
        self.winLength = winLength
        self.bufferSize = bufferSize
        self.buffer = 0
        self.dump_policy = dump_policy
        self.interval = interval
        self.m_jump = m_jump  
        self.pac = []
        self.bitmatrix = Bitarray(winLength)
        self.receivedPac = []
        self.contacting = []


    ## Store packet information
    def add_packet(self, pid, sta, des, born, deadline, size, prob, oval_prob, threshold, path=[]):
        dropped=0
        if(self.myid != sta):
            path.append(self.myid)

        dropped = self.dump_packet(size)
        self.pac.append(FGDRPacket(pid, sta, des, born, deadline, size, prob, oval_prob, threshold, path))
        self.receivedPac.append(pid)
 
        self.buffer +=size
       
        return dropped
    
    def update_history(self, other, empty1, empty2, empty3):
        if(not self.bitmatrix.matrix.__contains__(other.myid)):
            self.bitmatrix.add_node_to_matrix(other.myid)
        if(not self.contacting.__contains__(other.myid)):
            self.contacting.append(other.myid)
        #print(other.myid,self.contacting)

        
    def update_matrix(self, index):
     
        self.bitmatrix.update_all(index, self.contacting)
        self.contacting.clear()
        self.bitmatrix.delete_array()

    ## Update the overall probability and available path for a packet
    def update_prob(self, packet,path, p):
        curpack = self.pac[self.pac.index(packet)]
        curpack.problist.append(p)
        curpack.path_his.append(path)
        curpack.cur_prob = self.cal_pro(curpack.problist)

        ## Get the sliding window
    ## return:
    ## sw the sliding window
    ## c1 the number of 1 in the sliding window
    def get_slwindow(self, i1, checkstart):
        sw = []
        count = checkstart%self.m_jump
        c1 = 0
        while(count<len(self.bitmatrix.matrix[i1])):
            #print(self.myid, i1, self.bitmatrix.matrix[i1])
            if(self.bitmatrix.get_data(i1, count)!= -1):
                #print("in sliding window")
                sw.append(self.bitmatrix.get_data(i1, count))
                if(self.bitmatrix.get_data(i1, count) == 1):
                    c1+=1
            count += self.m_jump
        return sw, c1

    ## Calculate the overall probability between 2 users from current time to deadline, according
    ## to sliding window
    ##  p = p1 + (1-p1)p2 + ... +(1-p1)(1-p2)...(1-(pn-1))*pn
    ## return:
    ## p the direct probability
    def cal_direct_pro(self, i1, curmindex, deadline):
        weight = [0.4, 0.3, 0.2, 0.1]
        #weight = [0.25, 0.25, 0.25, 0.25]
        prob = []
        p=0
        checklength = (int)(deadline/self.interval)
        if(checklength > self.m_jump):
           checklength = self.m_jump
        #print("Checklength ", checklength, self.m_jump)
        for i in range(checklength+1):
            if(self.bitmatrix.matrix.__contains__(i1)):
                sw, c1 = self.get_slwindow(i1, curmindex+i)
                
                if(sw!=[]):
                    #print(sw)
                    p = 0
                    for j in range(len(sw)):
                        p+= sw[j]* weight[j]
                        #p+=sw[j]
                    #p/=len(sw)
##                    if(p!=0 and p!=1):
##                        print(p, curmindex,i, sw, self.myid, i1)
                       # print(self.spmatrix[i1].bitarray)
                    prob.append(p)
        if(prob !=[]):
            p = self.cal_pro(prob)
        
        return p


    ## Calculate the overall probability for a packet
    ## return:
    ## p the overall probability
    def cal_pro(self, prob):
        p=1
        
        for i in range(len(prob)):
            p *= (1- prob[i])
        p = 1 - p
        return p

##  Packet class
class FGDRPacket(Packet):

    def __init__(self, pid, sta, des, born, deadline, size, prob, oval_prob, fwd_threshold, path = []):
        self.pid=pid
        self.sta = sta
        self.des = des
        self.born = born
        self.deadline = deadline
        self.size = size
        self.pred_prob = oval_prob
        self.cur_prob = prob
        self.fwd_threshold = fwd_threshold
        self.path_his = path
        self.problist = [prob]
        self.copy = 0

    def update_fwd_threshold(self, cur_time):
        self.fwd_threshold = self.fwd_threshold *((self.deadline - cur_time)/(self.deadline - self.born))
        if(self.pred_prob > self.cur_prob):
            self.fwd_threshold = min(self.fwd_threshold, self.fwd_threshold *(1 - (self.pred_prob-self.cur_prob)/self.pred_prob))
            #self.fwd_threshold *= (1-((self.pred_prob-self.cur_prob)/self.pred_prob))
       
        if(self.fwd_threshold<0 or self.fwd_threshold>1):
            print("WRONG", self.fwd_threshold)
    def to_string(self):
        return str(self.pid)+" "+str(self.sta)+" "+str(self.des)+" "+str(self.deadline)+" "+str(self.pred_prob)+" "+str(self.cur_prob)+" "+str(self.path_his)+" "+str(self.problist)



        
