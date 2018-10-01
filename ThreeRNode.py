from Node import *
import DTNgeneral
import datetime as dt

class ThreeRNode(Node):

    ##  Constructor function
    def __init__(self, myid, bufferSize, dump_policy, datestart):
        self.myid = myid
        self.dump_policy = dump_policy
        self.buffer = 0
        self.datestart = datestart
        self.bufferSize = bufferSize 
        self.pac = []
        self.receivedPac = []
        self.lastupdatetime={}
        self.conthis = {} #[index, time of contacts]

    def update_history(self, node2, time, constime, conetime):
        #print("update history")
        is_weekday = True
        curdt = self.datestart+dt.timedelta(seconds=time)
        if(curdt.date().weekday() > 4):
            is_weekday = False
        index = curdt.hour
        id2 = node2.myid
        if(not self.conthis.__contains__(id2)):
            temp = [[0]*24, [0]*24]
            self.conthis.update({id2:temp})
        temp = self.conthis[id2]
        times = self.cal_uptime(constime, conetime, time-DTNgeneral.dur, time)
        
        if(times ==0):
            times=1
            
        if(is_weekday):
            temp[0][index] +=times
        else:
            temp[1][index]+=times
        self.conthis.update({id2:temp})
        #print(self.conthis)
        self.lastupdatetime.update({id2:conetime})

    def remove_conthis(self, curtime):
        remove = []
        for i in self.lastupdatetime:
            if(not remove.__contains__(i)):
                if (curtime - self.lastupdatetime[i]>2592000):
                    remove.append(i)
        for i in remove:
            del self.lastupdatetime[i]
            del self.conthis[i]
        
        
    def cal_uptime(self, cst, cet, inttimes, inttimee):
        if(cet<=inttimee):
            if(cst>= inttimes):
                return int((cet-cst)/60)
            elif(cst< inttimes):
                return int((cet-inttimes)/60)
        elif(cet>inttimee):
            if(cst>= inttimes):
                return int((inttimee - cst)/60)
            elif(cst< inttimes):
                return int((inttimee - inttimes)/60)


    def cal_prob(self, id2, pacborn, pacdeadline):
    
        count = 0
        is_weekday = True
        checklength = int((pacdeadline - pacborn)/3600)+1
        problist = []
        packetborn = self.datestart + dt.timedelta(seconds= pacborn)
        j = packetborn.hour
        if(packetborn.date().weekday()>4):
            is_weekday= False

        while(count <= checklength):
            total = 0
            id2times = 0
           
            for i in self.conthis:
                if(is_weekday == True):
                    if(i == id2):
                        id2times+= self.conthis[i][0][j]
                    total += self.conthis[i][0][j]
                else:
                    if(i == id2):
                        id2times+= self.conthis[i][1][j]
                    total += self.conthis[i][1][j]     
            j+=1
            count+=1
            if(j>23):
                j=0
                if((packetborn + dt.timedelta(hours= count)).date().weekday()>4):
                    is_weekday = False
                else:
                    is_weekday = True
            if(total !=0):
                prob = id2times/total
                problist.append(prob)
        if(problist != []):
           
            p=1
            for i in range(len(problist)):
                p *=(1-problist[i])
            p = 1-p
          
            return p
        return 0
        
