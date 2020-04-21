/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
#include "include/headers.p4"
#include "include/parsers.p4"


/* MACROS */
#define SKETCH_ROW_LENGTH 8160
#define SKETCH_CELL_BIT_WIDTH 32

#define SKETCH_INIT(num) register<bit<SKETCH_CELL_BIT_WIDTH>>(SKETCH_ROW_LENGTH) sketch##num
#define WINDOW_INIT(num) register<bit<SKETCH_CELL_BIT_WIDTH>>(SKETCH_ROW_LENGTH) window##num

#define SKETCH_INDEX(num, ip, seed) hash(meta.index_sketch##num, HashAlgorithm.crc32, (bit<32>)0, {ip, seed}, (bit<32>)SKETCH_ROW_LENGTH)
#define SKETCH_COUNT(num, ip, seed) SKETCH_INDEX(num, ip, seed); \
sketch##num.read(meta.value_sketch##num, meta.index_sketch##num);\
window##num.read(meta.window_sketch##num, meta.index_sketch##num); \
meta.value_sketch##num = (meta.value_sketch##num >> (bit<8>)(meta.mAbsWindowId-meta.window_sketch##num));\
meta.value_sketch##num = meta.value_sketch##num + 1;\
meta.window_sketch##num = meta.mAbsWindowId;\
sketch##num.write(meta.index_sketch##num, meta.value_sketch##num);\
window##num.write(meta.index_sketch##num, meta.window_sketch##num);

/* Initialize SkAge */
SKETCH_INIT(0);
WINDOW_INIT(0);
SKETCH_INIT(1);
WINDOW_INIT(1);
SKETCH_INIT(2);
WINDOW_INIT(2);

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

    action skage(){
        extract_flow_id();
        SKETCH_COUNT(0, meta.flowId, 104w11111111111111111111);
        SKETCH_COUNT(1, meta.flowId, 104w22222222222222222222);
        SKETCH_COUNT(2, meta.flowId, 104w33333333333333333333);

    }

    apply {
        skage();
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
