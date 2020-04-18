#!/bin/bash

# Usage: ./extract.sh DATASET_DIR/

function get_files {
	FILES=`ls -d $1/* | grep \.pcap$ | sort --version-sort`
    for i in $FILES; do
        echo `realpath $i`
    done;
}

function extract_ipv4 {
    for i in $FILES; do
        echo $i
        tshark -r $i -T fields -t e -e _ws.col.Time -e ipv6.addr -e ip.addr -e ipv6.nxt -e ip.proto -e tcp.port -e udp.port | awk '$2' > $i.dataset
    done;
}

FILES=$(get_files $1)
extract_ipv4 $FILES

# timestamp srcIP,dstIP ipProto srcPort,dstPort
# command='tcpdump -ttnnr univ1_pt1 | grep IP |awk -F ' ' '{print $1" "$3" "$5}' | tr -d :'
# tshark -r $i -te -T fields -t e -e _ws.col.Time -e ip.addr -e ip.proto -e tcp.port -e udp.port | awk -F ' ' '{if ($2 && $3) print $1" "$2" "$3" "$4}' > $i.txt
# tshark -r $i -T fields -t e -e _ws.col.Time -e ip.addr -e ip.proto -e tcp.port -e udp.port | awk '$2' > $i.dataset

# IMC 2010 DC
# tshark -r $i -T fields -t e -e frame.time_epoch -e ipv6.addr -e ip.addr -e ipv6.nxt -e ip.proto -e tcp.port -e udp.port | awk '$2' > $i.dataset