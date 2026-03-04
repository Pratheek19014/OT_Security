#!/usr/bin/env python3
"""
Profinet Protocol Helper Functions
"""

import struct

class ProfinetProtocol:
    """Constants and utilities for Profinet protocol"""
    
    # Ethernet Types
    ETHERTYPE_PROFINET_DCP = 0x8892
    ETHERTYPE_PROFINET_RT = 0x8892
    
    # DCP Service IDs
    DCP_GET = 0x03
    DCP_SET = 0x04
    DCP_IDENTIFY = 0x05
    DCP_HELLO = 0x06
    
    # DCP Options
    DCP_OPT_IP = 0x01
    DCP_OPT_DEVICE = 0x02
    DCP_OPT_DHCP = 0x03
    DCP_OPT_CONTROL = 0x05
    
    # DCP Suboptions
    DCP_SUBOPT_MAC = 0x01
    DCP_SUBOPT_IP_ADDRESS = 0x02
    DCP_SUBOPT_NAME_OF_STATION = 0x02
    
    @staticmethod
    def parse_dcp_packet(data):
        """Parse DCP packet"""
        if len(data) < 10:
            return None
        
        service_id = data[0]
        service_type = data[1]
        xid = struct.unpack('!I', data[2:6])[0]
        response_delay = struct.unpack('!H', data[6:8])[0]
        data_length = struct.unpack('!H', data[8:10])[0]
        
        return {
            'service_id': service_id,
            'service_type': service_type,
            'xid': xid,
            'response_delay': response_delay,
            'data_length': data_length,
            'data': data[10:10+data_length]
        }
    
    @staticmethod
    def build_dcp_header(service_id, service_type, xid, data_length):
        """Build DCP header"""
        return struct.pack('!BBIHH',
                          service_id,
                          service_type,
                          xid,
                          0,  # response delay
                          data_length)
