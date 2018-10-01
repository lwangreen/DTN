import DTNgeneral
from DTNgeneral import *
from FGProphetNode import *
import sys

interval = 0
windowSize = 0
no_of_best = 0

class FGProphet(General):

    def add_node_to_list(self, sta):
        #print("ProphetNode add")
        DTNgeneral.nodeid.append(sta)
        DTNgeneral.nodes.append(FGProphetNode(sta, DTNgeneral.buffer_size, DTNgeneral.dump_policy, interval, windowSize, no_of_best))

    def is_update_time_index(self):
        global interval
        # Check time index              
        if(DTNgeneral.time%interval == 0):
            return True
        return False


    def check_forward(self, node1, node2, packet, con_start_time):

        node1.update_best_list(packet)
        if(node2.myid in packet.best_list):
            if((DTNgeneral.dump_policy == 'R' and node2.buffer+ packet.size <= node2.bufferSize) or DTNgeneral.dump_policy != 'R'):
                DTNgeneral.dropped+= node2.add_packet(packet.pid, packet.sta, packet.des, packet.born, packet.deadline, packet.size, packet.path.copy())
                #packet.copy+=1
                DTNgeneral.transmission+=1
                DTNgeneral.copies +=1

                    
    def update_info(self):
        for i in DTNgeneral.nodes:
            i.LTW_append()
            

    def assign_global_variables(self, opts, args):
        global interval
        global windowSize
        global no_of_best
        
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
        interval = int(args[2])
        windowSize = int(args[3])
        no_of_best = int(args[4])
        

    def storage_memory(self, nodes):
        max_st = 0
        avg_st = 0
        max_lenst = 0
        avg_lenst = 0
        un = 0
        for i in nodes:
            un+=len(i.pac)
            avg_st += sys.getsizeof(i.forwarder_list)
            avg_lenst += len(i.forwarder_list)
            if(max_st<sys.getsizeof(i.forwarder_list)):
                max_st = sys.getsizeof(i.forwarder_list)
            if(max_lenst < len(i.forwarder_list)):
                max_lenst = len(i.forwarder_list)
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
        f.write("FGPRoPHET\n")
        f.write("Database Cambridge Rep2:\n")
        f.write("File: "+file_name+"\n")
        f.write("Average delay: "+ str(average_time)+"\n")
        f.write("attack prob: "+str(attack_prob)+"\n")
        f.write("Best of: "+str(no_of_best)+"\n")
        f.write("Window size: "+str(windowSize)+"\n")
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
