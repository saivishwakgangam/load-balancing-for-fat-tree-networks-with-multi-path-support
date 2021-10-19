from pox.lib.recoco import Timer
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
import pox.lib.packet as pkt
class Component3(object):
    def __init__(self):
        self.time=0
        self._t=Timer(5,self.request_port_stats,recurring=True)
        core.openflow.addListenerByName("PortStatsReceived",self._handle_port_stats)
        core.openflow.addListenerByName("PacketIn",self._handle_packet_in)
        self.port_stats={}
    def request_port_stats(self):
        self.time+=5
        for con in core.openflow.connections.values():
            con.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
    def _handle_port_stats(self,event):
        dpid=event.dpid
        stats=flow_stats_to_list(event.stats)
        for stat in stats:
            self.port_stats[(dpid,stat['port_no'])]=stat['tx_bytes']
        #print(stats)
    def _handle_packet_in(self,event):
        packet=event.parsed
        packet_in=event.ofp
        
    
def launch():
    core.registerNew(Component3)

