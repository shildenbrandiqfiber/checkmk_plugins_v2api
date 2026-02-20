#!/usr/bin/env python3

import struct
from datetime import datetime
from cmk.agent_based.v2 import SimpleSNMPSection, CheckPlugin, Service, Result, State, startswith, SNMPTree, OIDEnd

def decode_byte_string_to_datetime(byte_string):
    try:
        if len(byte_string) != 8:
            raise ValueError("Byte string must be exactly 8 bytes long")
        timestamp = struct.unpack('<Q', byte_string)[0]
        date_time_obj = datetime.fromtimestamp(timestamp)
        formatted_date_time = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date_time
    except (struct.error, ValueError, OverflowError):
        return 'Invalid Date'


def parse_edfa2(string_table):
    result = {}
    result["controller_type"] = string_table[0][0]
    return result

def discover_edfa2(section):
    yield Service()

def check_edfa2(section):
    error_status = False
    if not error_status:
        yield Result(state=State.OK, summary="Edfamux Environment - OK")

snmp_section_edfamux_base_config_env = SimpleSNMPSection(
    name = "edfamux_base_config_env",
    parse_function = parse_edfa2,
    detect = startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.55872"),
    fetch = SNMPTree(
        base='.1.3.6.1',
        oids=[
            '2.1.1.2.0', # Object ID
#            OIDEnd()
        ]
    ),
)

check_plugin_edfamux_env = CheckPlugin(
    name = "edfamux_env",
    sections = ["edfamux_base_config_env"],
    service_name = "Edfamux Env Health",
    discovery_function = discover_edfa2,
    check_function = check_edfa2,
)
