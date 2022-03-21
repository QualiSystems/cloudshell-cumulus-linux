# Configuring VLAN via editing /etc/network/interface
After editing the file execute command `ifreload -a`
# 1. without QinQ
## default bridge
```
auto br_default
iface br_default
    bridge-vlan-aware yes
```
## add access VLAN
- ### add access VLAN *12* to swp2
```
+auto swp2
+iface swp2
+    bridge-access 12

auto br_default
iface br_default
+    bridge-vids 12
+    bridge-ports swp2
    bridge-vlan-aware yes
```
- ### add access VLAN *14* to swp3
```
auto swp2
iface swp2
    bridge-access 12

+auto swp3
+iface swp3
+    bridge-access 14

auto br_default
iface br_default
+    bridge-vids 12 14
-    bridge-vids 12
+    bridge-ports swp2 swp3
-    bridge-ports swp2
    bridge-vlan-aware yes
```
## remove access VLAN
- ### remove access VLAN *14* from spw3
```
auto swp2
iface swp2
    bridge-access 12

auto swp3
iface swp3
-    bridge-access 14

auto br_default
iface br_default
-    bridge-vids 12 14
+    bridge-vids 12
-    bridge-ports swp2 swp3
+    bridge-ports swp2
    bridge-vlan-aware yes
```
- ### remove access VLAN *12* from swp2
```
auto swp2
iface swp2
-    bridge-access 12

auto swp3
iface swp3

auto br_default
iface br_default
-    bridge-vids 12
-    bridge-ports swp2
    bridge-vlan-aware yes
```
## add trunk VLAN
- ### add trunk VLAN *21* to swp1
```
auto swp1
iface swp1
+    bridge-vids 21

auto br_default
iface br_default
+    bridge-vids 21
+    bridge-ports swp1
    bridge-vlan-aware yes
```
- ### add trunk VLAN *21-24* to swp2
```
auto swp1
iface swp1
    bridge-vids 21

auto swp2
iface swp2
+    bridge-vids 21 22 23 24

auto br_default
iface br_default
-    bridge-vids 21
+    bridge-vids 21 22 23 24
-    bridge-ports swp1
+    bridge-ports swp1 swp2
    bridge-vlan-aware yes
```
## remove trunk VLAN
- ### remove trunk VLAN *21-24* from swp2
```
auto swp1
iface swp1
    bridge-vids 21

auto swp2
iface swp2
-    bridge-vids 21 22 23 24

auto br_default
iface br_default
+    bridge-vids 21
-    bridge-vids 21 22 23 24
+    bridge-ports swp2
-    bridge-ports swp2 swp3
    bridge-vlan-aware yes
```
- ### remove trunk VLAN *21* from swp1
```
auto swp1
iface swp1
-    bridge-vids 21

auto swp2
iface swp2

auto br_default
iface br_default
-    bridge-vids 21
-    bridge-ports swp2
    bridge-vlan-aware yes
```
# 2. with QinQ
## QinQ bridge
*not default bridge*
```
auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
```
## add access VLAN
- ### add access VLAN *12* to swp2
```
+auto vni-12
+iface vni-12
+    bridge-access 12
+    vxlan-id 12
 
+auto swp2
+iface swp2
+    bridge-access 12

auto br_qinq
iface br_qinq
+    bridge-vids 12
+    bridge-ports swp2 vni-12
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
```
- ### add access VLAN *14* to swp3
```
auto vni-12
iface vni-12
    bridge-access 12
    vxlan-id 12

+auto vni-14
+iface vni-14
+    bridge-access 14
+    vxlan-id 14
 
auto swp2
iface swp2
    bridge-access 12

+auto swp3
+iface swp3
+    bridge-access 14

auto br_qinq
iface br_qinq
-    bridge-vids 12
+    bridge-vids 12 14
-    bridge-ports swp2 vni-12
+    bridge-ports swp2 vni-12 swp3 vni-14
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
```
## remove access VLAN
- ### remove access VLAN *14* from spw3
```
auto vni-12
iface vni-12
    bridge-access 12
    vxlan-id 12

-auto vni-14
-iface vni-14
-    bridge-access 14
-    vxlan-id 14
 
auto swp2
iface swp2
    bridge-access 12

auto swp3
iface swp3
-    bridge-access 14

auto br_qinq
iface br_qinq
+    bridge-vids 12
-    bridge-vids 12 14
+    bridge-ports swp2 vni-12
-    bridge-ports swp2 vni-12 swp3 vni-14
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
```
- ### remove access VLAN *12* from swp2
```
-auto vni-12
-iface vni-12
-    bridge-access 12
-    vxlan-id 12

auto swp2
iface swp2
-    bridge-access 12

auto swp3
iface swp3

auto br_qinq
iface br_qinq
-    bridge-vids 12
-    bridge-ports swp2 vni-12 swp3 vni-14
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
```
## add trunk VLAN
- ### add trunk VLAN *21* to swp1
```
+auto vni-21
+iface vni-21
+    bridge-access 21
+    vxlan-id 21

auto swp1
iface swp1
+    bridge-vids 21

auto br_qinq
iface br_qinq
+    bridge-vids 21
+    bridge-ports swp1 vni-21
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
```
- ### add trunk VLAN *22* to swp2
```
auto vni-21
iface vni-21
    bridge-access 21
    vxlan-id 21

auto swp1
iface swp1
    bridge-vids 21

+auto vni-22
+iface vni-22
+    bridge-access 21
+    vxlan-id 22

auto swp2
iface swp2
+    bridge-vids 22

auto br_qinq
iface br_qinq
-    bridge-vids 21
+    bridge-vids 21 22
-    bridge-ports swp1 vni-21
+    bridge-ports swp1 vni-21 swp2 vni-22
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
```
## remove trunk VLAN
- ### remove trunk VLAN *22* from swp2
```
auto vni-21
iface vni-21
    bridge-access 21
    vxlan-id 21

auto swp1
iface swp1
    bridge-vids 21

-auto vni-22
-iface vni-22
-    bridge-access 22
-    vxlan-id 22

auto swp2
iface swp2
-    bridge-vids 22

auto br_qinq
iface br_qinq
+    bridge-vids 21
-    bridge-vids 21 22
+    bridge-ports swp1 vni-21
-    bridge-ports swp1 vni-21 swp2 vni-22
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
```
- ### remove trunk VLAN *21* from swp1
```
-auto vni-21
-iface vni-21
-    bridge-access 21
-    vxlan-id 21

auto swp1
iface swp1
-    bridge-vids 21

auto br_qinq
iface br_qinq
-    bridge-vids 21
-    bridge-ports swp1 vni-21
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
```
