import DTNgeneral
from DTNgeneral import *
from ThreeRNode import *
import datetime as dt

datestart = dt.datetime(2005,1,1,14,0,0)
class ThreeR(General):

    def add_node_to_list(self, sta):
        DTNgeneral.nodeid.append(sta)
        DTNgeneral.nodes.append(ThreeRNode(sta, DTNgeneral.buffer_size, DTNgeneral.dump_policy, datestart))

    def check_forward(self, node1, node2, packet, con_start_time):
        
        if(node2.conthis.__contains__(packet.des)):
            pacborn =packet.born
            pacdeadline =packet.deadline
            node1.remove_conthis(con_start_time)
            node2.remove_conthis(con_start_time)
            prob1 = node1.cal_prob(packet.des, pacborn, pacdeadline)
            prob2 = node2.cal_prob(packet.des, pacborn, pacdeadline)
            
            if(prob1<prob2 or (prob1== prob2 and len(node2.conthis) > len(node1.conthis))):
                if((dump_policy == 'R' and node2.buffer+ packet.size <= node2.bufferSize) or dump_policy != 'R'):
                    
                    DTNgeneral.dropped+=node2.add_packet(packet.pid, packet.sta, packet.des, packet.born, packet.deadline, packet.size, packet.path.copy())
                    node1.remove_packet(packet)
                    DTNgeneral.transmission+=1

                            
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
        f.write("3R\n")
        f.write("Database Infocom:\n")
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
