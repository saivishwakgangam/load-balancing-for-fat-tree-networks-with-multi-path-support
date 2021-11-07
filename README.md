# load-balancing-for-fat-tree-networks-with-multi-path-support
### run following commands in mininet vm
- cp code/start.py ~/mininet/custom/
- cp code/monitor.py pox/ext/
### start controller
- cd pox
- ./pox.py openflow.discovery host_tracker monitor --k=4 --method=dynamic
- In the above command change --method=static for creating static flows without load balancing.
### start mininet with custom topology(K fat tree)
- cd ~
- sudo -E python mininet/custom/start.py 4
- The above commands initializes a 4-fat tree
- observe the results of iperf for both static and dynamic modes
### sample topology
![4 fat tree](/topo.png)
## RESULTS
### STATIC MODE BANDWIDTH
![static](/results/static_mode.png)
### DYNAMIC MODE BANDWIDTH
![dynamic](/results/dynamic_mode.png)
### FLOW ENTRY MODIFICATION
- INITIAL
![initial](/results/initial_flow_entry.png)
- MODIFIED
![modified](/results/changed_flow_entry.png)
### PATH MODIFICATION
![path](/results/path_modified.png)

### REFERENCE
[paper](https://users.cs.fiu.edu/~pand/publications/13icc-yu.pdf)