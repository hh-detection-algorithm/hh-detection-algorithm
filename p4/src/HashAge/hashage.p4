/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
#include "include/headers.p4"
#include "include/parsers.p4"


/* MACROS */
#define ENTRIES_PER_TABLE 2040
#define ENTRY_WIDTH 168

#define HA_INIT(num) register<bit<ENTRY_WIDTH>>(ENTRIES_PER_TABLE) ha##num

#define GET_ENTRY(num, seed) \
hash(meta.currentIndex, HashAlgorithm.crc32, (bit<32>)0, {meta.flowId, seed}, (bit<32>)ENTRIES_PER_TABLE);\
ha##num.read(meta.currentEntry, meta.currentIndex);

#define WRITE_ENTRY(num, entry) ha##num.write(meta.currentIndex, entry)

#define STAGE_N(num, seed) {\
meta.flowId = meta.carriedKey;\
GET_ENTRY(num, seed);\
meta.currentKey = meta.currentEntry[167:64];\
meta.currentCount = meta.currentEntry[63:32];\
meta.currentWin = meta.currentEntry[31:0];\
meta.currentCount =  (meta.currentCount >> (bit<8>)(meta.mAbsWindowId-meta.currentWin));\
meta.currentWin = meta.mAbsWindowId;\
if (meta.currentKey - meta.carriedKey == 0) {\
    meta.toWriteKey = meta.currentKey;\
    meta.toWriteCount = meta.currentCount + meta.carriedCount;\
    meta.toWriteWin = meta.carriedWin;\
    meta.carriedKey = 0;\
    meta.carriedCount = 0;\
    meta.carriedWin = 0;\
} else {\
    if (meta.carriedCount > meta.currentCount) {\
        meta.toWriteKey = meta.carriedKey;\
        meta.toWriteCount = meta.carriedCount;\
        meta.toWriteWin = meta.carriedWin;\
\
        meta.carriedKey = meta.currentKey;\
        meta.carriedCount = meta.currentCount;\
        meta.carriedWin = meta.carriedWin;\
    } else {\
        meta.toWriteKey = meta.currentKey;\
        meta.toWriteCount = meta.currentCount;\
        meta.toWriteWin = meta.carriedWin;\
    }\
}\
bit<168> temp = meta.toWriteKey ++ meta.toWriteCount ++ meta.toWriteWin;\
WRITE_ENTRY(num, temp);\
}

/* Initialize HA*/
HA_INIT(0);
HA_INIT(1);
HA_INIT(2);
HA_INIT(3);
HA_INIT(4);
HA_INIT(5);

/* Wrap around */
const bit<32> WINDOWS_PER_PHASE = 10; // # of entries in the TCAM
register <bit<32>> (1) GLOBAL_WINDOW_ID;
register <bit<32>> (1) WRAP_AROUND_CONSTANT;


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
    }

    action get_absolute_window_id(bit<32> absWinId){
        bit<32> wrapAroundConstant;
        WRAP_AROUND_CONSTANT.read(wrapAroundConstant, 0);

        bit<32> globalWinId;
        GLOBAL_WINDOW_ID.read(globalWinId, 0);

        bit <32> tempWinId;
        tempWinId = absWinId + wrapAroundConstant;

        if (tempWinId < globalWinId) {
            wrapAroundConstant = wrapAroundConstant + WINDOWS_PER_PHASE;
        }

        tempWinId = absWinId + wrapAroundConstant;

        globalWinId = tempWinId;
        meta.mAbsWindowId = globalWinId;
        GLOBAL_WINDOW_ID.write(0, globalWinId);
        WRAP_AROUND_CONSTANT.write(0, wrapAroundConstant);
    }
    
    table ip_forward {
        key = {
            standard_metadata.ingress_port : exact;
        }
        actions = {
            drop;
            forward;
        }
        default_action = drop;
        const entries = {
            1 : forward(2);
            2 : forward(1);
        }
    }

    // ingress_global_timestamp is 48 bits, reference: https://github.com/p4lang/p4c/blob/master/p4include/v1model.p4#L55
    // how to match against range? : https://github.com/p4lang/behavioral-model/blob/master/docs/simple_switch.md
    table get_window_id {
        key = {     
            standard_metadata.ingress_global_timestamp : range;
        }
        actions = {
            get_absolute_window_id;
            NoAction;
        }
        const entries = {
            #include "include/window_id.p4"
        }
        default_action = NoAction();
    }

    table debug {
        key = {
            meta.mAbsWindowId : exact;
        }
        actions = {
            NoAction;
        }
        default_action = NoAction();
    }
    
    apply {
        get_window_id.apply();
        if (hdr.ipv4.isValid()) {    
            ip_forward.apply();
            debug.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    
    action extract_flow_id () {
        meta.flowId[103:72] = hdr.ipv4.srcAddr;
        meta.flowId[71:40] = hdr.ipv4.dstAddr;
        meta.flowId[39:32] = hdr.ipv4.protocol;
        
        if(hdr.tcp.isValid()) {
            meta.flowId[31:16] = hdr.tcp.srcPort;
            meta.flowId[15:0] = hdr.tcp.dstPort;
        } else if(hdr.udp.isValid()) {
            meta.flowId[31:16] = hdr.udp.srcPort;
            meta.flowId[15:0] = hdr.udp.dstPort;
        } else {
            meta.flowId[31:16] = 0;
            meta.flowId[15:0] = 0;
        }
    }

    action stage1 () {
        meta.carriedKey = meta.flowId;
        meta.carriedCount = 0;
        meta.carriedWin = meta.mAbsWindowId;

        GET_ENTRY(0, 104w00000000000000000000);

        meta.currentKey = meta.currentEntry[167:64];
        meta.currentCount = meta.currentEntry[63:32];
        meta.currentWin = meta.currentEntry[31:0];
        meta.currentCount =  (meta.currentCount >> (bit<8>)(meta.mAbsWindowId-meta.currentWin));
        meta.currentWin = meta.mAbsWindowId;

        // If the flowIds are the same
        if (meta.currentKey - meta.carriedKey == 0) {
            meta.toWriteKey = meta.currentKey;
            meta.toWriteCount = meta.currentCount + 1;
            meta.toWriteWin = meta.carriedWin;

            meta.carriedKey = 0;
            meta.carriedCount = 0;
            meta.carriedWin = 0;
        } else {
            meta.toWriteKey = meta.carriedKey;
            meta.toWriteCount = 1;
            meta.toWriteWin = meta.carriedWin;

            meta.carriedKey = meta.currentKey;
            meta.carriedCount = meta.currentCount;
            meta.carriedWin = meta.currentWin;
        }

        bit<168> temp = meta.toWriteKey ++ meta.toWriteCount ++ meta.toWriteWin;
        WRITE_ENTRY(0, temp);
    }

    action hashage() {
        extract_flow_id();
        stage1();
        STAGE_N(1, 104w11111111111111111111);
        STAGE_N(2, 104w22222222222222222222);
        STAGE_N(3, 104w33333333333333333333);
        STAGE_N(4, 104w44444444444444444444);
        STAGE_N(5, 104w55555555555555555555);
    }

    apply {
        hashage();
    }

}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
        packet.emit(hdr.udp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
