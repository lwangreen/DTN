import DTNgeneral
from DTNgeneral import *
from SWNode import *

BINARY = False
MAX_COPY = 0
class SprayandWait(General):

    def add_node_to_list(self, sta):
        global BINARY
       
        DTNgeneral.nodeid.append(sta)
        DTNgeneral.nodes.append(SWNode(sta, DTNgeneral.buffer_size, DTNgeneral.dump_policy, BINARY))

    def add_packet(self, node, packetno, sta, des, born, deadline, size):
        global MAX_COPY
        dropped = node.add_packet( packetno, sta, des, born, deadline,size, MAX_COPY)
        return dropped
    
    def check_forward(self, node1, node2, packet, con_start_time):
        global BINARY
        global MAX_COPY

        #print("SWNode forward in")
        if((DTNgeneral.dump_policy == 'R' and node2.buffer+ packet.size <= node2.bufferSize) or DTNgeneral.dump_policy != 'R'):
            if(BINARY == False):
                if(packet.iscopy == False and packet.copy <= MAX_COPY):
                    DTNgeneral.dropped+=node2.add_packet(packet.pid, packet.sta, packet.des, packet.born,
                                        packet.deadline, packet.size, MAX_COPY, packet.path.copy(), True)
                    packet.copy+=1
                    DTNgeneral.copies+=1
            
                    DTNgeneral.transmission+=1
            else:
                
                if(packet.copy>1):
                    numcopy = (int)(packet.copy/2)
                    packet.copy -= numcopy
                    #if(numcopy>0):
                    DTNgeneral.dropped+=node2.add_packet(packet.pid, packet.sta, packet.des, packet.born,
                                            packet.deadline, packet.size, numcopy, packet.path.copy(), True)

                    DTNgeneral.copies+=1
            
                    DTNgeneral.transmission+=1


    def assign_global_variables(self, opts, args):
##        global memory_limit
##        global buffer_size
##        global dump_policy
##        global file_name
##        global output_file
##        global protocol
        global BINARY
        global MAX_COPY

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
        if args[2] == "binary":
            BINARY = True
        else:
            BINARY = False
        MAX_COPY = int(args[3])
      

        
    def result(self,output_file, nodes, file_name, memory_limit, buffer_size, dump_policy,copies, dropped, packetno,
               sucpacket, transmission, total_time, attack_prob):
        un = 0
        for i in nodes:
            un+=len(i.pac)
        print("not transmitted",un)
        dropped+=un
        average_time = 0
        sucpercentage = 0
        if sucpacket>0:
            sucpercentage = sucpacket/packetno 
            average_time= total_time/sucpacket
        overhead = transmission / packetno 
##        print("Epidemic")
##        print("Database Infocom:")
##        print("File: ", file_name)
##        print("Average delay: ", average_time)
##        print("Attack prob: ", attack_prob)
##        print("Memory limit", memory_limit, "Memory buffer:", buffer_size, "Dump_policy", dump_policy)
##        print("Total number of packets:",packetno)
##        print("Success:",sucpacket,  "Copies:", copies, "transmission", transmission, "Drop:", dropped,"Ratio:",sucpercentage)
##        print("Overhead:", overhead)

        f = open(output_file, 'a')
        f.write("Spray and Wait\n")
        f.write("Database Infocom:\n")
        f.write("File: "+file_name+"\n")
        f.write("Average delay: "+ str(average_time)+"\n")
        f.write("attack prob: "+str(attack_prob)+"\n")
        f.write("Binary: "+str(BINARY)+"\n")
        f.write("Max copy: "+str(MAX_COPY)+"\n")
        f.write("Memory limit: "+ str(memory_limit)+ " Memory buffer: "+ str(buffer_size)+ " Dump_policy: "+ dump_policy+"\n")
        f.write("Total number of packets: "+str(packetno)+"\n")
        f.write("Success: "+str(sucpacket)+ " Copies: "+ str(copies)+ " transmission: "+ str(transmission)+ " Drop: "+ str(dropped)+
                " Ratio: "+str(sucpercentage)+"\n")
        f.write("Overhead: "+ str(overhead)+"\n")
        f.write("\n")
        f.close()
