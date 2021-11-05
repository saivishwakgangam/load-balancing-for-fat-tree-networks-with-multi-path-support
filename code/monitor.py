from pox.lib.recoco import Timer
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
import pox.lib.packet as pkt
import networkx as nx
from pox.lib.util import dpid_to_str
log = core.getLogger()
class Component3(object):
    def __init__(self):
        self.time=0
        self.graph=nx.DiGraph()
        core.openflow.addListenerByName("PortStatsReceived",self._handle_port_stats)
        core.openflow_discovery.addListenerByName("LinkEvent",self._handle_link)
        core.host_tracker.addListenerByName("HostEvent",self._handle_Host)
        self.port_details={}
        self.port_stats={}
        self.stat_counter=0
        self.connected_hosts={}
        self.host_to_switch={}
        self.distances={}
        self.hosts=[]
        self.find_port={}
        self.mac_to_port={}
        self.flag=False
        self.shortest_path_lengths={}
        self.prev_path_lengths={}
        self.prev_path={}
        self.prev_cycle_stat={}
    
    def request_port_stats(self):
        print("requesting port stats")
        for con in core.openflow.connections.values():
            con.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
    def request_flow_stats(self,dpids):
        for dpid in dpids:
            con=core.openflow.getConnection(dpid)
            con.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
        
    
    def _handle_connection_up(self,event):
        dpid=event.dpid
        features=event.ofp
        #print(features.['ports'])



    def _handle_port_stats(self,event):
        #print("5 secs later")
        #switch dpid
        dpid=event.dpid
        self.stat_counter+=1
        stats=flow_stats_to_list(event.stats)
        for stat in stats[1:]:
            port=stat['port_no']
            #to ignore host connected ports
            if(port in self.port_details[dpid]):
                v=self.port_details[dpid][port]
                if(dpid==17):
                    print(stat['tx_bytes']*1e3)
                self.graph[dpid][v]['weight']=(1.25*1e6)/((1.25*1e6)-(stat['tx_bytes']*1e3-self.prev_cycle_stat[dpid][port])/10)
                #print((1.25*1e6)-(stat['tx_bytes']-self.prev_cycle_stat[dpid][port])/10)
                self.prev_cycle_stat[dpid][port]=stat['tx_bytes']*1e3
            
        
        if(self.stat_counter==20):
            print("All Stats Received")
            self.stat_counter=0
            switches=list(self.connected_hosts.keys())
            for i in range(len(switches)):
                for j in range(i+1,len(switches)):
                    path=nx.shortest_path(self.graph,switches[i],switches[j],'weight')
                    
                    cur_length=nx.shortest_path_length(self.graph,switches[i],switches[j],'weight')
                    prev_path=self.prev_path[(switches[i],switches[j])]
                    prev_length=0
                    for k in range(0,len(prev_path)-1):
                        prev_length+=self.graph[path[k]][path[k+1]]['weight']
                    change=(prev_length-cur_length)/prev_length
                    if(change>0):
                        print(change)
                    if((prev_length-cur_length)/prev_length > 0.3):
                        #path modified
                        self.prev_path[(switch[i],switch[j])]=path #updating path
                        hosts1=self.connected_hosts[switch[i]]
                        hosts2=self.connected_hosts[switch[j]]
                        for k in range(1,len(path)-1):
                            con=core.openflow.getConnection(path[k])
                            for host_addr in hosts2:
                                msg=of.ofp_flow_mod()
                                match=of.ofp_match()
                                match.in_port=self.find_port[path[k]][path[k-1]]
                                match.dl_dst=host_addr
                                msg.match=match
                                action=of.ofp_action_output(port=self.find_port[path[k]][path[k+1]])
                                msg.actions.append(action)
                                msg.command=OFPFC_MODIFY
                                con.send(msg)
                                print("flow modified %i"%(path[k]))
                        for k in range(len(path)-2,0,-1):
                            con=core.openflow.getConnection(path[k])
                            for host_addr in hosts1:
                                msg=of.ofp_flow_mod()
                                match=of.ofp_match()
                                match.in_port=self.find_port[path[k]][path[k+1]]
                                match.dl_dst=host_addr
                                msg.match=match
                                action=of.ofp_action_output(port=self.find_port[path[k]][path[k-1]])
                                msg.actions.append(action)
                                msg.command=OFPFC_MODIFY
                                con.send(msg)
                                print("flow modified %i"%(path[k]))
                        con=core.openflow.getConnection(path[0])
                        outport=self.find_port[path[0]][path[1]]
                        for host_addr in hosts1:
                            for addr in hosts2:
                                msg=of.ofp_flow_mod()
                                match=of.ofp_match()
                                match.dl_src=host_addr
                                match.dl_dst=addr
                                msg.match=match
                                action=of.ofp_action_output(port=outport)
                                msg.actions.append(action)
                                msg.command=OFPFC_MODIFY
                                con.send(msg)
                                print("flow modified %i"%(path[0]))
                        con=core.openflow.getConnection(path[-1])
                        outport=self.find_port[path[-1][path[-2]]]
                        for host_addr in hosts2:
                            for addr in hosts1:
                                msg=of.ofp_flow_mod()
                                match=of.ofp_match()
                                match.dl_src=host_addr
                                match.dl_dst=addr
                                msg.match=match
                                action=of.ofp_action_output(port=outport)
                                msg.actions.append(action)
                                msg.command=OFPFC_MODIFY
                                con.send(msg)
                                print("flow modified %i"%(path[-1]))
                                


                                
        
    def _handle_link(self,event):
        #dpid is unique identifier given by controller to switch
        dpid1=event.link.dpid1
        dpid2=event.link.dpid2
        #print(dpid1,dpid2,event.link.port1)
        port1=event.link.port1
        port2=event.link.port2
        if dpid1 in self.port_details:
            self.port_details[dpid1][port1]=dpid2
            self.prev_cycle_stat[dpid1][port1]=0
        else:
            self.port_details[dpid1]={}
            self.port_details[dpid1][port1]=dpid2
            self.prev_cycle_stat[dpid1]={}
            self.prev_cycle_stat[dpid1][port1]=0
        
        # Update flow table
        if dpid2 in self.find_port:
            self.find_port[dpid2][dpid1]=port2
        else:
            self.find_port[dpid2]={}
            self.find_port[dpid2][dpid1]=port2
        self.graph.add_edge(dpid1,dpid2,weight=1)
        
    def _handle_Host(self,event):
        
        #h1 mac address
        macAddr=event.entry.macaddr
        #edge switch dpid
        dpid=event.entry.dpid
        #switch port number to host
        port=event.entry.port
        self.host_to_switch[macAddr]=dpid
        if dpid in self.connected_hosts:
            self.connected_hosts[dpid].add(macAddr)
        else:
            self.connected_hosts[dpid]=set()
            self.connected_hosts[dpid].add(macAddr)

        #edge switch to host flow rule(sibling host)
        if(not self.flag):
            msg=of.ofp_flow_mod()
            match=of.ofp_match()
            match.dl_dst=macAddr
            action=of.ofp_action_output(port=port)
            msg.actions.append(action)
            msg.match=match
            msg.priority+=1
            con=core.openflow.getConnection(dpid)
            con.send(msg)
            print("installed a dest flow for %i->%s"%(dpid,macAddr.toStr()))
        if(len(self.host_to_switch)==16 and not self.flag):
            print(self.find_port)
            self.flag=True
            #edge switches
            switches=list(self.connected_hosts.keys())
            #check=set()
            for i in range(len(switches)):
                for j in range(i+1,len(switches)):
                    path=nx.shortest_path(self.graph,switches[i],switches[j],'weight')
                    print(switches[i],switches[j],path)
                    path_length=nx.shortest_path_length(self.graph,switches[i],switches[j],'weight')
                    self.prev_path_lengths[(switches[i],switches[j])]=path_length
                    self.prev_path[(switches[i],switches[j])]=path
                    #if(switches[j]==20):
                        #check.update(path)
                    hosts1=self.connected_hosts[switches[i]]
                    hosts2=self.connected_hosts[switches[j]]
                    for k in range(1,len(path)-1):
                        con=core.openflow.getConnection(path[k])
                        for host_addr in hosts2:
                            msg=of.ofp_flow_mod()
                            match=of.ofp_match()
                            match.in_port=self.find_port[path[k]][path[k-1]]
                            match.dl_dst=host_addr
                            msg.match=match
                            outport=self.find_port[path[k]][path[k+1]]
                            action=of.ofp_action_output(port=outport)
                            msg.actions.append(action)
                            con.send(msg)
                            #if(switches[i]==17 and switches[j]==20):
                                #print("installed flow for (%i,%i)->%i->(%i,%i)"%(path[k-1],match.in_port,path[k],path[k+1],outport))
                    for k in range(len(path)-2,0,-1):
                        con=core.openflow.getConnection(path[k])
                        for host_addr in hosts1:
                            msg=of.ofp_flow_mod()
                            match=of.ofp_match()
                            match.in_port=self.find_port[path[k]][path[k+1]]
                            match.dl_dst=host_addr
                            msg.match=match
                            outport=self.find_port[path[k]][path[k-1]]
                            action=of.ofp_action_output(port=outport)
                            msg.actions.append(action)
                            con.send(msg)
                            #if(switches[i]==17 and switches[j]==20):
                                #print("installed flow for (%i,%i)->%i->(%i,%i)"%(path[k+1],match.in_port,path[k],path[k-1],outport))
                    con=core.openflow.getConnection(path[0])
                    outport=self.find_port[path[0]][path[1]]
                    for host_addr in hosts1:
                        for host_addr2 in hosts2:
                            msg=of.ofp_flow_mod()
                            match=of.ofp_match()
                            match.dl_src=host_addr
                            match.dl_dst=host_addr2
                            action=of.ofp_action_output(port=outport)
                            msg.actions.append(action)
                            msg.match=match
                            con.send(msg)
                            if(path[0]==17 and path[-1]==20):
                                print("installed src flow for %s->%i->%i"%(host_addr.toStr(),path[0],path[1]))
                    con=core.openflow.getConnection(path[-1])
                    outport=self.find_port[path[-1]][path[-2]]
                    for host_addr in hosts2:
                        for host_addr2 in hosts1:
                            msg=of.ofp_flow_mod()
                            match=of.ofp_match()
                            match.dl_src=host_addr
                            match.dl_dst=host_addr2
                            action=of.ofp_action_output(port=outport)
                            msg.actions.append(action)
                            msg.match=match
                            con.send(msg)
                            if(path[0]==17 and path[-1]==20):
                                print("installed src flow for %s->%i->%i"%(host_addr.toStr(),path[-1],path[-2]))
            #self.request_flow_stats(check)
            self._t=Timer(10,self.request_port_stats,recurring=True)


                    
            

    
def launch():
    core.registerNew(Component3)




