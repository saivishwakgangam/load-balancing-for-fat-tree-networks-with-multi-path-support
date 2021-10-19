from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel,info
from mininet.node import RemoteController
from mininet.cli import CLI
import sys


class Mytopo(Topo):
    def __init__(self,k,**opts):
        super(Mytopo,self).__init__(**opts)
        pods=k
        self.core_switches=(k//2)**2
        self.aggr_switches=pods*(k//2)
        self.edge_switches=pods*(k//2)
        self.hosts_count=self.edge_switches*(k//2)
        self.k=k
        self.host_names=[]
        self.edge_names=[]
        self.aggr_names=[]
        self.core_names=[]
        self.create_hosts()
        self.create_edge_switches()
        self.link_host_edge()
        self.create_aggr_switches()
        self.link_edge_aggr()
        self.create_core_switches()
        self.link_aggr_core()
        
   
    def __macaddr_helper(self,n):
        temp=format(n,"012X")
        mac_address=""
        for i in range(0,10,2):

            mac_address+=temp[i:i+2]+":"
        mac_address+=temp[10:]
        return mac_address

    def create_hosts(self):
        for i in range(1,self.hosts_count+1):
            mac_address=self.__macaddr_helper(i)    
            #print(i,mac_address)
            h=self.addHost('H'+str(i),mac=mac_address)
            #print(h,end=" ")
            self.host_names.append(h)
    
    def create_edge_switches(self):
        start=self.hosts_count+1
        end=start+self.edge_switches
        for i in range(start,end):
            #macaddress=self.__macaddr_helper(self.hosts_count+i)
            e=self.addSwitch('E'+str(i))
            #print(e,end=" ")
            self.edge_names.append(e)
    
    def link_host_edge(self):
        for i,edge_switch in enumerate(self.edge_names):
            corr_hosts=self.host_names[i*(self.k//2):(i+1)*(self.k//2)]
            for host in corr_hosts:
                self.addLink(host,edge_switch)
    def create_aggr_switches(self):
        start=self.hosts_count+self.edge_switches+1
        end=start+self.aggr_switches
        for i in range(start,end):
            #macaddress=self.__macaddr_helper(self.hosts_count+self.edge_switches+i)
            a=self.addSwitch('A'+str(i))
            self.aggr_names.append(a)

    def link_edge_aggr(self):
        for i in range(0,self.aggr_switches,(self.k//2)):
            aggrs=self.aggr_names[i:i+(self.k//2)]
            edges=self.edge_names[i:i+(self.k//2)]
            for a in aggrs:
                for e in edges:
                    self.addLink(e,a)
    def create_core_switches(self):
        start=self.hosts_count+self.edge_switches+self.aggr_switches+1
        end=start+self.core_switches
        for i in range(start,end):
            #macaddress=self.__macaddr_helper(self.hosts_count+self.edge_switches+self.aggr_switches+i)
            c=self.addSwitch('C'+str(i))
            self.core_names.append(c)
        
    def link_aggr_core(self):
        for c in self.core_names:
            for a in self.aggr_names:
                self.addLink(a,c)



def run(k):
    c=RemoteController('c0','0.0.0.0',6633)
    net=Mininet(topo=Mytopo(k),host=CPULimitedHost,controller=None)
    net.addController(c)
    net.start()
    CLI(net)
    net.stop()
    
if __name__=='__main__':
    setLogLevel('info')
    k=int(sys.argv[1])
    run(k)