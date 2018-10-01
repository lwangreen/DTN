class Node(object):
    
    ##  Constructor function
    def __init__(self, myid, bufferSize, dump_policy):
        self.myid = myid
        self.pac = []
        self.dump_policy = dump_policy
        self.buffer = 0
        self.receivedPac = []
        self.bufferSize = bufferSize


    ## Check whether this node contains specified packet
    def contain_packet(self, pid):
        if(self.receivedPac.__contains__(pid)):
            return True
        for i in self.pac:
            if(i.pid == pid):
                return True
        return False



 ## Store packet information
    def add_packet(self, pid, sta, des, born, deadline, size, path=[]):
        dropped=0
        if(self.myid != sta):
            path.append(self.myid)
        if(self.buffer > self.bufferSize-size):
            dropped = self.dump_packet(size)
        self.pac.append(Packet(pid, sta, des, born, deadline, size, path))     
        self.receivedPac.append(pid)
        self.buffer +=size
        
        return dropped

    
    def remove_packet(self, packet):
        self.buffer -= packet.size
        self.pac.remove(packet)
        
    def dump_packet(self,size):
        dropped = 0
        
        while(self.buffer > self.bufferSize-size):
            self.remove_packet(self.pac[0])
            dropped+=1
 
        return dropped
       
                            
   ## Update the time to live field of packets
    def check_expired(self, packet, time):
        if(packet.deadline<=time):
            self.remove_packet(packet)
            return True
        return False
                
         
           


    ## Destination receive packet
    def success_packet(self, packet):
##        path= str(packet.sta)+"-->"
##        for k in packet.path:
##            path += str(k)+"-->"
##        path += str(packet.des)
##        
        #print("Success to transmit message", self.myid, packet.sta, packet.des, packet.pid, path)
        if(not self.receivedPac.__contains__(packet.pid)):
            self.receivedPac.append(packet.pid)
            return 1
        else: return 0


    def node_attack(self):
        self.pac = []
        self.buffer = 0


class Packet(object):

    def __init__(self, pid, sta, des, born, deadline, size, path= []):
        self.pid = pid
        self.sta = sta
        self.des = des
        self.born = born
        self.deadline = deadline
        self.path = path
        self.size = size

    def to_string(self):
       return str(self.pid)+" "+str(self.sta)+" "+str(self.des)+" "+str(self.deadline)+" "+str(self.path)
