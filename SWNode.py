from Node import *

class SWNode(Node):
    ## Store packet information
    def __init__(self, myid, bufferSize, dump_policy, binary):
        self.myid = myid
        self.pac = []
        self.dump_policy = dump_policy
        self.buffer = 0
        self.receivedPac = []
        self.bufferSize = bufferSize
        self.binary = binary
        
    def add_packet(self, pid, sta, des, born, deadline, size, copy, path=[], iscopy=False):
        dropped=0
        if(self.myid != sta):
            path.append(self.myid)
        if(self.buffer > self.bufferSize-size):
            
            dropped = self.dump_packet(size)
        if(self.binary == False):
            self.pac.append(SWPacket(pid, sta, des, born, deadline, size, path, iscopy))
        else:
            self.pac.append(BinarySWPacket(pid, sta, des, born, deadline, size, copy, path))
            
        self.receivedPac.append(pid)
        
        self.buffer +=size
        
        return dropped


class SWPacket(Packet):

    def __init__(self, pid, sta, des, born, deadline, size, path= [], iscopy = False):
        self.pid = pid
        self.sta = sta
        self.des = des
        self.born = born
        self.deadline = deadline
        self.path = path
        self.copy = 0
        self.iscopy = iscopy
        self.size = size
        
class BinarySWPacket(Packet):

    def __init__(self, pid, sta, des, born, deadline, size, copy, path= []):
        self.pid = pid
        self.sta = sta
        self.des = des
        self.born = born
        self.deadline = deadline
        self.path = path
        self.copy = copy
        self.size = size
