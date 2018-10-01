import mysql.connector
from Node import *

dur = 900       #Time flows by 600 secs a time
time=0
end = 0
sucpacket=0
packetno = 0
nodeid = []
nodes = []
copies = 0
dropped= 0
transmission = 0
total_time= 0
attack_prob = 0

buffer_size = 0
memory_limit = True
buffer_size = 0
dump_policy = ''
file_name = ''
output_file = ''
protocol = ''
datatrace = ''


class General(object):

    ## retrieve contact record of current time
    ## return:
    ## d the list of records, in the order of id1, id2, start time, end time
    def retrieve_data(self, cur, time):
        cur.execute("select id1,id2, start_time, end_time from contactsrep2 where \
        (end_time<'%s' and end_time>='%s') or (start_time<'%s' and end_time>'%s') order by start_time;"
                    % (time, time-dur, time,time))

        d = cur.fetchall()
        return d

    def add_node_to_list(self, sta):
        global nodeid
        global nodes
        
        nodeid.append(sta)
        nodes.append(Node(sta, buffer_size, dump_policy))

    def read_packet(self, file_name):
        
        f = open(file_name, 'r')

        a = f.read().split("\n")
        pac = []
        for i in range(len(a)-1):
            
            a[i] = a[i].split(' ')
            b = []
            for k in a[i]:
                b.append(k)
            pac.append(b)
        
        return pac

    def get_node(self, nid):
        for i in nodes:
            if(i.myid == nid):
                return i

    def select_attackers(self, cur):
        cur.execute("select distinct id1 from contactsrep2")
        n1 = cur.fetchall()
        cur.execute("select distinct id2 from contactsrep2")
        n2 = cur.fetchall()
        nodes = n1+n2

        count = 0
        attackers = []
        while count<len(nodes)*attack_prob:
            temp = random.randint(0, len(nodes)-1)
            a = nodes[temp][0]
            if a not in attackers:
                attackers.append(a)
                count+=1
        return attackers

    def add_packet(self, node, packetno, sta, des, born, deadline, size):
        dropped = node.add_packet( packetno, sta, des, born, deadline,size)
        return dropped
    
    def get_packets(self, pred_packets):
        global packetno
        global dropped
        global memory_limit
        global buffer_size
        global time
        
        
        for packet in pred_packets:
            if(len(packet)>0):
                born=float(packet[0])
                if(born<time and born>=time-dur):
                    sta = int(packet[1])
                    des = int(packet[2])
                    ttl = int(packet[3])
                    if(memory_limit == True):
                        size = int(packet[4])
                    else:
                        size = 0
                     
                    deadline = born + ttl
                    if(not nodeid.__contains__(sta)):
                        self.add_node_to_list(sta)
                    packetno+=1
                    stanode = self.get_node(sta)
                    if((dump_policy == 'R' and stanode.buffer+ size <= stanode.bufferSize) or dump_policy != 'R'):
                        dropped += self.add_packet(stanode, packetno, sta, des, born, deadline,size)
                        #print(stanode.myid, stanode.pac)
                    else:
                        dropped +=1
                    
                elif(born > time):
                    break

                
    def get_contact_time(self, con_data):
        global time
        global dur
        con_start_time = 0
        con_end_time= 0
        start_time = 0
        end_time = 0
       
        if(con_data[2]<con_data[3]):
            con_start_time = con_data[2]
            con_end_time = con_data[3]
        else:
            con_start_time = con_data[3]
            con_end_time = con_data[2]
            
        if(con_start_time<time-dur):
            start_time = time-dur
            if(con_end_time>=time):   
                end_time = time
            else:
                end_time = con_end_time
        else:
            start_time = con_start_time
            if(con_end_time>=time):
                end_time = time
            else:
                end_time = con_end_time

        return start_time, end_time

    
    def check_forward(self, node1, node2, packet, empty):
        global copies
        global transmission
        global dropped
        
        if((dump_policy == 'R' and node2.buffer+ packet.size <= node2.bufferSize) or dump_policy != 'R'):
            dropped+=node2.add_packet( packet.pid, packet.sta, packet.des, packet.born,
                                        packet.deadline, packet.size, packet.path.copy())
            copies+=1
            transmission+=1

    def update_delay_time(self, packet, con_start_time):
        global total_time
        global shortest
        existtime = con_start_time-packet.born
        if(existtime>0):
            total_time +=existtime
            

            
    def success(self, node1, node2, packet, con_start_time):
        global sucpacket
        global dropped
        global transmission
        
        isSuccessed = node2.success_packet(packet)
        node1.remove_packet(packet)
        if(isSuccessed):
            
            self.update_delay_time(packet, con_start_time)
                
            sucpacket+= isSuccessed
            transmission+=1
        else:
            dropped+=1
            
    def routing(self, node1, node2, time, con_start_time, con_end_time):
        #print(node1.myid, node1.pac, con_start_time)
        global dropped
        for packet in node1.pac:
            
            if(node1.check_expired(packet, time-dur)):
                dropped+=1
            else:
                if(packet.deadline > con_start_time and packet.born < con_end_time):
                    if(node2.myid == packet.des):
                        self.success(node1, node2, packet, con_start_time)  
                        
                    else:
                       
                        if(not node2.contain_packet(packet.pid)):
                            self.check_forward(node1, node2, packet, con_start_time)

    def get_end_time(self, cur):
        global end
        cur.execute("select end_time from contactsrep2 order by end_time desc limit 1;")
        d = cur.fetchall()
        end = d[0][0]
        

    def processing(self, pred_packets, cur):
        global time
        excuted = []
        self.get_packets(pred_packets)
        data = self.retrieve_data(cur, time)
        #print(data, time)
        #i in format of ID1, ID2, start_time, end_time
        for i in data:
            #print(i)
            if([int(i[0]), int(i[1])] not in excuted and [int(i[1]), int(i[0])] not in excuted ):
            ## Add new users dynamically
                if(not nodeid.__contains__(int(i[0]))):
                    self.add_node_to_list(int(i[0]))
                if(not nodeid.__contains__(int(i[1]))):
                    self.add_node_to_list(int(i[1]))
              
                node1 = self.get_node(int(i[0]))
                node2 = self.get_node(int(i[1]))
                con_sta_time, con_end_time = self.get_contact_time(i)
##                if(node1.myid==6 and node2.myid==7):
##                    print(con_sta_time, con_end_time)
                try:
                    
                    node1.update_history(node2, time, con_sta_time, con_end_time)  
                    node2.update_history(node1, time, con_sta_time, con_end_time)
                   
                except:
                    #print("ERROR, update history")
                    pass
                
                self.routing(node1, node2, time, con_sta_time, con_end_time)
                self.routing(node2, node1, time, con_sta_time, con_end_time)

                excuted.append([int(i[0]), int(i[1])])
                excuted.append([int(i[1]), int(i[0])])
        
    def running(self):
        global time
       
        cnx = mysql.connector.connect(user='root', database='cambridge')
        cur = cnx.cursor(buffered=True)
        self.get_end_time(cur)
        pred_packets = self.read_packet(file_name)
        #attackers = self.select_attackers(cur)
        

        while(time<=end):
            self.processing(pred_packets, cur)
            time+=dur

            try:
                if(self.is_update_time_index()):
                    self.update_info()
            except:
                pass
           

        self.result(output_file, nodes, file_name, memory_limit, buffer_size, dump_policy, copies, dropped, packetno,
                    sucpacket, transmission,total_time, attack_prob)

        cnx.close()
    def assign_global_variables(self, opts, args):
        global memory_limit
        global buffer_size
        global dump_policy
        global file_name
        global output_file
        global protocol
        global datatrace

        for opt, arg in opts:
          
            if opt in ("-i", "--ifile"):
                
                file_name = arg
            elif opt in ("-o", "--ofile"):
                output_file = arg
        
            elif opt in ("-p", "--protocol"):
                protocol = arg

            elif opt in ("-d", "--datatrace"):
                datatrace = arg
        
        if args[0].isdigit():
            memory_limit = True
            buffer_size = int(args[0])
        else:
            
            memory_limit = False
        dump_policy = args[1]
  
