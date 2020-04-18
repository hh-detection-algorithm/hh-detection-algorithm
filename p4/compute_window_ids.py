import sys
import math

# length in seconds
window_length = int(sys.argv[1])

def convert_s_to_us(s):
    us = s * math.pow(10,6)
    return us

# psa -> 42-bit timestamp, advancing 1 per nanosecond will wrap around at 1.22 hours
# v1model -> 48 bit
ns = math.pow(2, 48)-1
s = int(ns / math.pow(10,9))

window = 0
# for i in range(0, s, window_length): # for simplicity, we only generate for the first 100 seconds instead of the whole 48bit range
for i in range(0, 100, window_length): 
    start = (hex(int(convert_s_to_us(i))))
    end = (hex(int(convert_s_to_us(i+window_length)-1)))
    window = window + 1
    window = window % 10
    print('48w{} .. 48w{} : get_absolute_window_id(32w{});'.format(start, end, window))