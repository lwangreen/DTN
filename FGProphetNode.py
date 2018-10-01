from Node import *


class FGProphetNode(Node):

    def __init__(self, myid, bufferSize, dump_policy, interval, windowSize, no_of_best):
        self.myid = myid
        self.pac = []
        self.dump_policy = dump_policy
        self.buffer = 0
        self.receivedPac = []
        self.bufferSize = bufferSize
        self.STW = {} # STW in format of {1:30, 2:159 ...}
        self.LTW = [] # LTW in format of [{1:30, 2:159 ...},{},{},{}]
        self.interval = interval
        self.windowSize = windowSize
        self.forwarder_list = {} #{id1:{id2:prob, id3:prob},id2{}} 
        self.no_of_best = no_of_best


    ## Store packet information
    def add_packet(self, pid, sta, des, born, deadline, size, path=[]):
        dropped=0
        if(self.myid != sta):
            path.append(self.myid)
        if(self.buffer > self.bufferSize-size):
            dropped = self.dump_packet(size)
            
        self.pac.append(FGProPacket(pid, sta, des, born, deadline, size, path))     
        self.receivedPac.append(pid)
        self.buffer +=size
        return dropped

    def update_forwarder_list(self, other):
        calculated = []
        for i in self.LTW:
            for j in i:
                if(j not in calculated):
                    prob=self.cal_prob(j)
                    #print(prob)
                    calculated.append(j)
                    if(prob>0):
                        if(self.myid not in self.forwarder_list):
                            self.forwarder_list.update({self.myid:{j:prob}})
                        else:
                            self.forwarder_list[self.myid].update({j:prob})
                    elif(prob==0):
                        print("wrong")
                        print(i, j)
                        print(self.LTW)
        for i in self.forwarder_list[self.myid]:
            if i not in calculated:
                del self.forwarder_list[self.myid][i]
        calculated.clear()
        #print("Before:", len(self.forwarder_list), len(other.forwarder_list))
        #print(self.forwarder_list, other.forwarder_list)
        for i in other.forwarder_list:
            if(i != self.myid):
                if(i not in self.forwarder_list):
                    self.forwarder_list.update({i:other.forwarder_list[i].copy()})
                else:
                    self.forwarder_list[i].update(other.forwarder_list[i].copy())
        #print("After:", len(self.forwarder_list))
        #print(self.forwarder_list)


    def fill_best_list(self, packet, i, j):
        if(packet.des == i):
            sou = j
            des = i
        elif(packet.des == j):
            sou = i
            des = j
        #print(j, self.forwarder_list[i])
        if(len(packet.best_list)<self.no_of_best):
            packet.best_list.update({sou:self.forwarder_list[des][sou]})
        else:
            minID = min(packet.best_list)
            if(packet.best_list[minID] < self.forwarder_list[sou][des]):
                del packet.best_list[minID]
                packet.best_list.update({sou:self.forwarder_list[des][sou]})
        #print(len(packet.best_list), packet.best_list)
        

                
    def update_best_list(self, packet):
        
        for i in self.forwarder_list:
            if(i == packet.des):
                for j in self.forwarder_list[i]:
                   self.fill_best_list(packet, i, j)
            else:
                if(packet.des in self.forwarder_list[i]):
                    self.fill_best_list(packet, i, packet.des)
##        print("------------------------------------------")
##        print(self.myid, packet.des)
##        print(len(packet.best_list), packet.best_list)
##        print("------------------------------------------")
                 
        if(len(packet.best_list)>self.no_of_best):
            print("Wrong best list", len(packet.best_list), packet.best_list)
        
    def update_history(self, other, time, start_time, end_time):
        contact_dur = end_time-start_time
 
        if(contact_dur>0):
            if(other.myid not in self.STW):
            
                self.STW.update({other.myid: 0})
            self.STW[other.myid] += contact_dur

            self.update_forwarder_list(other)
        if(self.STW[other.myid]>self.interval):
            print("WRONG cd", contact_dur, self.myid, other.myid, self.STW[other.myid])
##        if(self.myid ==6 and other.myid == 7 or self.myid==7 and other.myid ==6):
##            print(contact_dur, start_time, end_time)
##            print(self.STW)
        
   
    def LTW_append(self):
        temp = {}
     
        while(len(self.LTW) >= self.windowSize):
            del self.LTW[0]
       
        if(len(self.STW)>0):
            self.LTW.append(self.STW.copy())
        
        self.STW.clear()
   

    def cal_prob(self, id2):
        total_cd = 0
        prob = 0
        
        if(len(self.LTW)>0):
            for i in self.LTW:
                #print(i)
                if(id2 in i):
                    total_cd += i[id2]
            #print("Total_cd", total_cd)
        else:
            if(id2 in self.STW):
                total_cd += self.STW[id2]
        
        if(len(self.LTW)>0):
            
            prob = float(total_cd)/(len(self.LTW) * self.interval)
        else:
            prob = float(total_cd)/self.interval

        if(prob>1):
            print("WRONG prob", self.myid, id2, prob, total_cd, len(self.LTW),self.interval)
            print(self.LTW)
        return prob


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


class FGProPacket(Packet):

    def __init__(self, pid, sta, des, born, deadline, size, path= []):
        self.pid = pid
        self.sta = sta
        self.des = des
        self.born = born
        self.deadline = deadline
        self.path = path
        self.size = size
        self.best_list = {}

    
