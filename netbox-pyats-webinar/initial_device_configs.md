# Initial Lab Device Configs

Initial configuration applied to the lab devices in addition to the basic config applied by Containerlab. This configures the interface connecting the devices, plus a loopback interface, then adds a simple OSPF configuration.  

## CSR1 
```
conf t
int gigabitEthernet 2
ip address 192.168.1.1 255.255.255.252
description Connection to CSR2
no shut
int lo0 
ip address 1.1.1.1 255.255.255.255 
lldp run
router ospf 1
router-id 1.1.1.1
log-adjacency-changes
network 192.168.1.1 0.0.0.3 area 0
network 1.1.1.1 0.0.0.0 area 0
exit
exit
wr
```

## CSR2 
```
conf t
int gigabitEthernet 2
ip address 192.168.1.2 255.255.255.252
description Connection to CSR1
no shut
int lo0 
ip address 2.2.2.2 255.255.255.255 
lldp run
router ospf 1
router-id 2.2.2.2
log-adjacency-changes
network 192.168.1.0 0.0.0.3 area 0
network 2.2.2.2 0.0.0.0 area 0
exit
exit
wr
```