import DTNgeneral
from DTNgeneral import *
from ProphetNode import *

class Prophet(General):


    def add_node_to_list(self, sta):
        #print("ProphetNode add")
        DTNgeneral.nodeid.append(sta)
        DTNgeneral.nodes.append(ProphetNode(sta, DTNgeneral.buffer_size, DTNgeneral.dump_policy))
        
    def check_forward(self, node1, node2, packet, con_start_time):

        #print("ProphetNode forward in")
        if(node2.problist.__contains__(packet.des)):
            if(not node1.problist.__contains__(packet.des) or  node2.problist[packet.des] > node1.problist[packet.des]):
                if((DTNgeneral.dump_policy == 'R' and node2.buffer+ packet.size <= node2.bufferSize) or DTNgeneral.dump_policy != 'R'):
                    DTNgeneral.dropped+= node2.add_packet(packet.pid, packet.sta, packet.des, packet.born, packet.deadline, packet.size, packet.path.copy())
                    #packet.copy+=1
                    DTNgeneral.transmission+=1
                    DTNgeneral.copies +=1

        
    
        
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
        f.write("Prophet\n")
        f.write("Database Cambridge Rep2:\n")
        f.write("File: "+file_name+"\n")
        f.write("Average delay: "+ str(average_time)+"\n")
        f.write("attack prob: "+str(attack_prob)+"\n")
        f.write("Memory limit: "+ str(memory_limit)+ " Memory buffer: "+ str(buffer_size)+ " Dump_policy: "+ dump_policy+"\n")
        f.write("Total number of packets: "+str(packetno)+"\n")
        f.write("Success: "+str(sucpacket)+ " Copies: "+ str(copies)+ " transmission: "+ str(transmission)+ " Drop: "+ str(dropped)+
                " Ratio: "+str(sucpercentage)+"\n")
        f.write("Overhead: "+ str(overhead)+"\n")
        f.write("\n")
        f.close()
