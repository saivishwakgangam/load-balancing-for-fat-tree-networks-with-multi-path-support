# load-balancing-for-fat-tree-networks-with-multi-path-support
### run following commands in mininet vm
- cp code/start.py ~/mininet/custom/`
- cp code/monitor.py pox/ext/
### start controller
- cd pox
- ./pox.py openflow.discovery host_tracker monitor --k=4 --method=dynamic
- In the above command change --method=static for creating static flows without load balancing.
### start mininet with custom topology(K fat tree)
- cd ~
- sudo -E python mininet/custom/start.py 4
- The above commands initialzies a 4-fat tree
- observe the results of iperf
### sample topology
![4 fat tree](/topo.png)
