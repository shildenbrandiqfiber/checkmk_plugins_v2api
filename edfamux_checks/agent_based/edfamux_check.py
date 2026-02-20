#!/usr/bin/env python3

import struct
from datetime import datetime
from cmk.agent_based.v2 import SimpleSNMPSection, CheckPlugin, Service, Result, State, startswith, SNMPTree, OIDEnd

def decode_byte_string_to_datetime(byte_string):
    try:
        # Ensure the byte string is exactly 8 bytes
        if len(byte_string) != 8:
            raise ValueError("Byte string must be exactly 8 bytes long")

        # Unpack the byte string into an integer, assuming little-endian format
        timestamp = struct.unpack('<Q', byte_string)[0]

        # Convert the integer timestamp to a datetime object
        date_time_obj = datetime.fromtimestamp(timestamp)

        # Format the datetime object into a string
        formatted_date_time = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_date_time
    except (struct.error, ValueError, OverflowError):
        return 'Invalid Date'


def parse_edfa1(string_table):
    result = {}
    result["controller_type"] = string_table[0][0]
    result["battery_fuse_status"] = string_table[0][1]
    result["battery_current"] = string_table[0][2]
    result["battery_health"] = string_table[0][3]
    result["battery_current_status"] = string_table[0][4]
    result["battery_temp"] = string_table[0][5]
    result["battery_status"] = string_table[0][6]
    result["mains_voltage"] = string_table[0][7]
    result["rectifier_1_status"] = string_table[0][8]
    result["rectifier_2_status"] = string_table[0][9]
    result["rectifier_capacity"] = string_table[0][10]
    result["rectifier_error_status"] = string_table[0][11]
    result["rectifier_status"] = string_table[0][12]
    result["rectifier_temp"] = string_table[0][13]
    result["last_battery_test_time"] = string_table[0][14]
    return result

def discover_edfa1(section):
    yield Service()

def check_edfa1(section):
    error_status = False
    if section["battery_fuse_status"] != "1":
        yield Result(state=State.CRIT, summary="Battery Fuse is Open")
        error_status = True
    if int(section["battery_current"]) >= 12:
        yield Result(state=State.WARN, summary="Battery Current is High")
        error_status = True
    if int(section["battery_health"]) < 100:
        yield Result(state=State.CRIT, summary="Battery Health is Degraded")
        error_status = True
    if section["battery_current_status"] != "1":
        yield Result(state=State.WARN, summary="Battery Current is Abnormal")
        error_status = True
    if section["battery_status"] != "1":
        yield Result(state=State.WARN, summary="Battery status is Abnormal")
        error_status = True
    if int(section["battery_temp"]) >= 104:
        yield Result(state=State.CRIT, summary="Battery Temp is High")
        error_status = True
    if int(section["mains_voltage"]) <= 200:
        yield Result(state=State.CRIT, summary="Mains Voltage is Critical")
        error_status = True
    if section["rectifier_1_status"] != "1":
        yield Result(state=State.CRIT, summary="Rectifier 1 is Faulty")
        error_status = True
    if section["rectifier_2_status"] != "1":
        yield Result(state=State.CRIT, summary="Rectifier 2 is Faulty")
        error_status = True
    if int(section["rectifier_capacity"]) >= 90:
        yield Result(state=State.CRIT, summary="Rectifier Capacity is Over 90%")
        error_status = True
    if section["rectifier_error_status"] != "1":
        yield Result(state=State.CRIT, summary="Rectifier Error")
        error_status = True
    if section["rectifier_status"] != "1":
        yield Result(state=State.CRIT, summary="Rectifier Status is Critical")
        error_status = True
    if int(section["rectifier_temp"]) >= 170:
        yield Result(state=State.WARN, summary="Rectifier Temp is High")
        error_status = True
    if not error_status:
        yield Result(state=State.OK, summary="edfa1 is OK")

    # BUG FIX: Removed broken Metric yield that referenced undefined battery_runtime variable

snmp_section_edfamux_base_config_check = SimpleSNMPSection(
    name = "edfamux_base_config_check",
    parse_function = parse_edfa1,
    detect = startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.55872"),
    fetch = SNMPTree(
        base='.1.3.6.1',
        oids=[
            '2.1.1.2.0', # Object ID
#            OIDEnd()
        ]
    ),
)

check_plugin_edfamux_check = CheckPlugin(
    name = "edfamux_check",
    sections = ["edfamux_base_config_check"],
    service_name = "Edfamux Health",
    discovery_function = discover_edfa1,
    check_function = check_edfa1,
)
