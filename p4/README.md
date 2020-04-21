# P4 implementation - HashAge, SkAge

## Description
The directory structure is adapted from the official P4 tutorials found at <https://github.com/p4lang/tutorials>. Simply navigate into the `HashAge` and `SkAge` directories under `src`, and execute the command `make run` to compile and run the source codes.

The topology consists of a single switch, `s1`, which is connected to two hosts, `h1` and `h2`. By default, packet forwarding is based on the `ingress_port` (i.e., packets coming in from port 1 will be directly forwarded out at port 2 and vice versa) in the ingress pipeline. You may modify the ingress pipeline with your desired forwarding behaviour.

You may find the `get_window_id` table, in the ingress pipeline as well. This corresponds to our solution to the wraparound problem mentioned in the paper.  Flow rules will be pre-populated into the table in which the `ingress_timestamp` will be matched against for each packet to get the global window ID. You may checkout `compute_window_ids.py` on how the window IDs are computed and also generate your own `window_id.p4`. You may replace [src/HashAge/include/window_id.p4](src/HashAge/include/window_id.p4) and [src/SkAge/include/window_id.p4](src/SkAge/include/window_id.p4) with your own generated `window_id.p4`. 

For `HashAge` and `SkAge`, they are implemented in the egress_pipeline for packet counting, right before the packet is forwarded out. To ease readability, C-style macros/ pre-processors are used extensively. 

<!-- The possible time span of the switch (e.g. 42-bits that advances every millisecond) will be logically divided into equally sized observation phases. Absolute window IDs will then be mapped to every observation phase. -->