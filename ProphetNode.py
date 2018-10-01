from Node import *

P_init = 0.5
beta = 0.9
gamma = 0.99

##P_init = 0.75
##beta = 0.25
##gamma = 0.98
delta=0.01
secondsInTimeUnit = 30

class ProphetNode(Node):
    def __init__(self, myid, bufferSize, dump_policy):
        self.myid = myid
        self.pac = []
        self.problist = {}
        self.dump_policy = dump_policy
        self.buffer = 0
        self.lastAgeTime = 0
        self.receivedPac = []
        self.bufferSize = bufferSize

    ##  Calculate direct probability
    def direct_prob(self, id2):
        p = 0
        oldP=0
        if(self.problist.__contains__(id2)):
            oldP = self.problist[id2]
        p =oldP +(1-oldP)* P_init
        self.problist.update({id2: p})


    ## Decay function
    def decay_prob(self, con_time):
        p = 0
        le = self.lastAgeTime
        if(le == 0):
            self.lastAgeTime = con_time
            le = con_time
        if(con_time > le):
           
            for id2 in self.problist:
                timediff = (con_time - le) / secondsInTimeUnit

                p = self.problist[id2]
                p *= gamma**timediff
                
                self.problist.update({id2:p})
            self.lastAgeTime=con_time       
                  
    
    ## Transitive probability
    def trans_prob(self, id2, entry):
        for i in entry:
            if(i != self.myid):
                oldP= 0
                if(self.problist.__contains__(i)):
                    oldP = self.problist[i]
              
                p = self.problist[id2] * entry[i] * beta
               
                if(p > oldP):
                    self.problist.update({i: p})
        if(len(self.problist)>100):
            self.remove_his()

    def remove_his(self):
        remove= []
        removelength = len(self.problist) -100

        for i in self.problist:
            if(self.problist[i]<0.001):
                remove.append(i)
            if(len(remove) == removelength):
                break
        for i in remove:
            del self.problist[i]

    def dump_packet(self,size):
        dropped = 0
        
        while(self.buffer > self.bufferSize-size):
         
            if(self.dump_policy == 'L'):
                if(not self.problist.__contains__(self.pac[0].des)):
                    lowprob = 0
                    lowpacket = self.pac[0]
                else:
                    lowprob = self.problist[self.pac[0].des]
                    lowpacket = self.pac[0]
                for packet in self.pac:
                    if(not self.problist.__contains__(packet.des)):
                        lowprob = 0
                        lowpacket = packet
                        break
                    else:
                        if(self.problist[packet.des] < lowprob):
                            lowprob = self.problist[packet.des]
                            lowpacket = packet
            
                self.remove_packet(lowpacket)
                dropped+=1
            

            elif(self.dump_policy == 'F'):
                self.remove_packet(self.pac[0])
                dropped+=1
 
        return dropped

    def update_history(self, other, time, start_time, end_time):
       
        while(start_time <= end_time):
            self.decay_prob(start_time)
            self.direct_prob(other.myid)
            self.trans_prob(other.myid, other.problist)
            start_time+=120
