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


def parse_edfa4(string_table):
    result = {}
    result["controller_type"] = string_table[0][0]
    return result

def discover_edfa4(section):
    yield Service()

def check_edfa4(section):
    error_status = False
    if not error_status:
        yield Result(state=State.OK, summary="Edfamux Power Supplies - OK")

snmp_section_edfamux_base_config_psu = SimpleSNMPSection(
    name = "edfamux_base_config_psu",
    parse_function = parse_edfa4,
    detect = startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.55872"),
    fetch = SNMPTree(
        base='.1.3.6.1',
        oids=[
            '2.1.1.2.0', # Object ID
#            OIDEnd()
        ]
    ),
)

check_plugin_edfamux_psu = CheckPlugin(
    name = "edfamux_psu",
    sections = ["edfamux_base_config_psu"],
    service_name = "Edfamux Power",
    discovery_function = discover_edfa4,
    check_function = check_edfa4,
)
