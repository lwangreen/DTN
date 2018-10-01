import DTNgeneral
import sys
from DTNgeneral import *
from FGDRNode import *

interval = 3600
m_jump=168
mupbound = 672#Matrix size: 672 according to the time indexes of 28 days
threshold = 0
mul_threshold = 0
dur=600
matrix_index = 0
class FGDR(General):

    def add_node_to_list(self, sta):
        DTNgeneral.nodeid.append(sta)
        DTNgeneral.nodes.append(FGDRNode(sta, DTNgeneral.buffer_size, DTNgeneral.dump_policy,
                                         mupbound, interval, m_jump))

    def add_packet(self, node, packetno, sta, des, born, deadline, size):
        global threshold
        global mul_threshold
        global matrix_index
        ttl = deadline - born
        prob = node.cal_direct_pro(des, matrix_index, ttl)
        dropped = node.add_packet(packetno, sta, des, born ,deadline, size, prob, threshold, mul_threshold)
        return dropped
        

    def forward(self, node1, node2, packet, prob2):
        
        DTNgeneral.dropped+= node2.add_packet(packet.pid, packet.sta, packet.des, packet.born,
                    packet.deadline, packet.size, prob2, packet.pred_prob, packet.fwd_threshold, packet.path_his.copy())
                                        
        node1.remove_packet(packet)
        DTNgeneral.transmission+=1
        

    def replicate(self, node1, node2, packet, prob2):
        DTNgeneral.dropped+= node2.add_packet(packet.pid, packet.sta, packet.des, packet.born,
                        packet.deadline, packet.size, prob2, prob2, packet.fwd_threshold, packet.path_his.copy())
        node1.update_prob(packet, node2.myid, prob2)
        
        DTNgeneral.transmission+=1
        DTNgeneral.copies +=1



    def check_forward(self, node1, node2, packet, con_start_time):
        global matrix_index
        ttl = packet.deadline - con_start_time #Current TTL
        
        prob1 = node1.cal_direct_pro(packet.des, matrix_index, ttl)
        prob2 = node2.cal_direct_pro(packet.des, matrix_index, ttl) #P(B,D)

        if(ttl <= interval):
            prob1 *= ttl/interval
            prob2 *= ttl/interval
        #packet.update_fwd_threshold(con_start_time)
        #print(matrix_index, ttl, prob2)
##        if(prob2>packet.fwd_threshold):
##            
##            if(packet.cur_prob < packet.pred_prob): #Pm(k) < Exm
##                
##                if(prob2 < packet.pred_prob): #If P(B,D) < Exm: send a replica
##                    if((DTNgeneral.dump_policy == 'R' and node2.buffer+ packet.size <= node2.bufferSize) or DTNgeneral.dump_policy != 'R'):
##                        self.replicate(node1, node2, packet, prob2)
##
##                        
##                else:  #If P(B,D) >= Exm: Forward m to B
##                    if((DTNgeneral.dump_policy == 'R' and node2.buffer+ packet.size <= node2.bufferSize) or DTNgeneral.dump_policy != 'R'):
##                        self.forward(node1, node2, packet, prob2)
##
##                    
##            else:# Pm(k) >= Exm. Exm is fulfilled
##                
##                if(packet.problist[0] < prob2): #If P(A,D) < P(B,D): Forward m to B
##                    if((DTNgeneral.dump_policy == 'R' and node2.buffer+ packet.size <= node2.bufferSize) or DTNgeneral.dump_policy != 'R'):
##                        self.forward(node1, node2, packet, prob2)
        if(prob1<=prob2):
            if((DTNgeneral.dump_policy == 'R' and node2.buffer+ packet.size <= node2.bufferSize) or DTNgeneral.dump_policy != 'R'):
                self.replicate(node1, node2, packet, prob2)
        
    ## Check the direct probability for next time unit
    def update_direct_prob(self, time, matrix_index):
        for node in DTNgeneral.nodes:
            for packet in node.pac:
                ttl = packet.deadline - time
                prob = node.cal_direct_pro(packet.des, matrix_index, ttl)
                if(prob != packet.problist[0]):
                    packet.problist[0] = prob
                    packet.cur_prob = node.cal_pro(packet.problist)
                    #print(packet.cur_prob, packet.pred_prob)


    def is_update_time_index(self):
        global interval
        # Check time index              
        if(DTNgeneral.time%interval == 0):
            return True
        return False

    def update_info(self):
        global matrix_index
        matrix_index+=1
        matrix_index = matrix_index % mupbound
        for i in DTNgeneral.nodes:
            #print(i.myid)
            i.update_matrix(matrix_index-1)
        self.update_direct_prob(DTNgeneral.time, matrix_index)


    def assign_global_variables(self, opts, args):
        global threshold
        global mul_threshold
        global interval
        global m_jump
        global mupbound
        
        for opt, arg in opts:
          
            if opt in ("-i", "--ifile"):
                
                DTNgeneral.file_name = arg
            elif opt in ("-o", "--ofile"):
                DTNgeneral.output_file = arg
        
            elif opt in ("-p", "--protocol"):
                DTNgeneral.protocol = arg
        
        
        if args[0].isdigit():
            DTNgeneral.memory_limit = True
            DTNgeneral.buffer_size = int(args[0])
        else:
            
            DTNgeneral.memory_limit = False
        DTNgeneral.dump_policy = args[1]
        threshold = float(args[2])
        mul_threshold = float(args[3])
        interval = int(args[4])
        m_jump = int(args[5])
        mupbound = int(args[6])
        

    def storage_memory(self, nodes):
        max_st = 0
        avg_st = 0
        max_lenst = 0
        avg_lenst = 0
        un = 0
        for i in nodes:
            un+=len(i.pac)
            avg_st += sys.getsizeof(i.bitmatrix.matrix)
            avg_lenst += len(i.bitmatrix.matrix)
            if(max_st<sys.getsizeof(i.bitmatrix.matrix)):
                max_st = sys.getsizeof(i.bitmatrix.matrix)
            if(max_lenst < len(i.bitmatrix.matrix)):
                max_lenst = len(i.bitmatrix.matrix)
        avg_st /= len(nodes)
        avg_lenst /= len(nodes)
        return max_st, avg_st, max_lenst, avg_lenst, un
        
    def result(self,output_file, nodes, file_name, memory_limit, buffer_size, dump_policy,copies, dropped, packetno,
               sucpacket, transmission, total_time, attack_prob):
        un = 0
        max_st, avg_st, max_lenst, avg_lenst, un = self.storage_memory(nodes)
        print("not transmitted",un)
        dropped+=un
        average_time = 0
        sucpercentage = 0
        if sucpacket>0:
            sucpercentage = sucpacket/packetno 
            average_time= total_time/sucpacket
        overhead = 0

        f = open(output_file, 'a')
        f.write("FGDR\n")
        f.write("Database Cambridge Rep2:\n")
        f.write("File: "+file_name+"\n")
        f.write("Average delay: "+ str(average_time)+"\n")
        f.write("attack prob: "+str(attack_prob)+"\n")
        f.write("Exp: "+str(threshold)+"\n")
        f.write("Forward threshold: "+str(mul_threshold)+"\n")
        f.write("Time slot length: "+str(interval)+"\n")
        f.write("Matrix length: "+str(mupbound)+"\n")
        f.write("Single period cycle: "+str(m_jump)+"\n")
        f.write("Memory limit: "+ str(memory_limit)+ " Memory buffer: "+ str(buffer_size)+ " Dump_policy: "+ dump_policy+"\n")
        f.write("Total number of packets: "+str(packetno)+"\n")
        f.write("Success: "+str(sucpacket)+ " Copies: "+ str(copies)+ " transmission: "+ str(transmission)+ " Drop: "+ str(dropped)+
                " Ratio: "+str(sucpercentage)+"\n")
        f.write("Overhead: "+ str(overhead)+"\n")
        f.write("Max storage: "+str(max_st)+"\n")
        f.write("Average storage: "+str(avg_st)+"\n")
        f.write("Max storage length: "+str(max_lenst)+"\n")
        f.write("Average storage length: "+str(avg_lenst)+"\n")
        
        f.write("\n")
        f.close()

