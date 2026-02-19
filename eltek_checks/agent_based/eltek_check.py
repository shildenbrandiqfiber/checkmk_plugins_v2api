#!/usr/bin/env python3

import struct
from datetime import datetime
from cmk.agent_based.v2 import SNMPSection, CheckPlugin, Service, Result, State, Metric, check_levels, startswith, SNMPTree

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

def _render_temp_with_unit(temp_c):
    try:
        temp_f = (float(temp_c) * 9 / 5) + 32
        return f"{temp_f:.1f} °F"
    except (TypeError, ValueError):
        return "N/A"

temp_unitsym = {
    "c": "°C",
    "f": "°F",
    "k": "K",
}

def parse_eltek(string_table):
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
    result["battery_runtime"] = string_table[0][14]
    result["last_battery_test_time"] = string_table[0][15]
    result["clearfield_cab_temp"] = string_table[0][16]
    return result

def discover_eltek(section):
    yield Service()

def check_eltek(section):
    battery_runtime = int(section["battery_runtime"])
    runtime_hours = battery_runtime // 60
    runtime_minutes = battery_runtime % 60
    error_status = False
    mains_down = False
    battery_temp = int(section["battery_temp"])
    clearfield_cab_temp = int(section["clearfield_cab_temp"])

    if int(section["mains_voltage"]) <= 100:
        yield Result(state=State.WARN, summary=f"Power Outage - Running on Batt - {runtime_hours}h {runtime_minutes}m left")
        error_status = True
        mains_down = True

    if not mains_down:
        if section["battery_fuse_status"] != "1":
            yield Result(state=State.WARN, summary="Battery Fuse is Open")
            error_status = True
        if int(section["battery_current"]) >= 20:
            yield Result(state=State.WARN, summary="Battery Charging")
            error_status = True
        if int(section["battery_health"]) < 90:
            yield Result(state=State.WARN, summary="Battery Health Less than 100%")
            error_status = True
        if section["battery_current_status"] != "1":
            yield Result(state=State.WARN, summary="Battery Current is Abnormal")
            error_status = True
        if section["battery_status"] != "1":
            yield Result(state=State.WARN, summary="Battery status is Abnormal")
            error_status = True
        #if section["rectifier_1_status"] != "1":
        #    yield Result(state=State.CRIT, summary="Rectifier 1 is Faulty")
        #    error_status = True
        #if section["rectifier_2_status"] != "1":
        #    yield Result(state=State.CRIT, summary="Rectifier 2 is Faulty")
        #    error_status = True
        if int(section["rectifier_capacity"]) > 50:
            yield Result(state=State.WARN, summary="Rectifier Capacity is Over 50%")
            error_status = True
        if section["rectifier_error_status"] != "1":
            yield Result(state=State.WARN, summary="Rectifier Error")
            error_status = True
        if section["rectifier_status"] != "1":
            yield Result(state=State.WARN, summary="Rectifier Status is Critical")
            error_status = True

    if int(section["rectifier_temp"]) >= 170:
        yield Result(state=State.WARN, summary="Rectifier Temp is High")
        error_status = True
    if int(section["battery_temp"]) >= 125:
        yield Result(state=State.WARN, summary="Battery Temp is High")
        error_status = True
    if not error_status:
        yield Result(state=State.OK, summary="Eltek Check Ok")

    # BATTERY
    yield from check_levels(
        value=battery_temp,
        levels_upper=(125, 140),
        metric_name="battery_temp",
        label="Battery Temperature",
        boundaries=(0, 150),
    )
    # CLEARFIELD CAB TEMP
    yield from check_levels(
        value=clearfield_cab_temp,
        levels_upper=(125,140),
        metric_name="clearfield_cab_temp",
        label="Cab Temp",
        boundaries = (0, 200),
    )

snmp_section_eltek_base_config = SNMPSection(
    name = "eltek_base_config",
    parse_function = parse_eltek,
    detect = startswith(".1.3.6.1.4.1.12148.10.13.8.2.1.2.1", "SmartPack S"),
    fetch = SNMPTree(
        base='.1.3.6.1.4.1.12148.10',
        oids=[
            '13.8.2.1.2.1',     # SmartPack S
            '10.4.0',           # Battery Fuse Status
            '10.6.5.0',         # Battery Current
            '10.12.5.0',        # Battery Health Value
            '10.6.1.0',         # Battery Current Status
            '10.7.5.0',         # Battery Temp
            '10.1.0',           # Battery Status
            '3.4.1.6.1',        # Mains Voltage
            '5.6.1.2.1',        # Rectifier 1 Status
            '5.6.1.2.2',        # Rectifier 2 Status
            '5.3.5.0',          # Rectifier Capacity (%)
            '5.4.1.0',          # Rectifier Error Status
            '5.1.0',            # Rectifier Status
            '5.18.5.0',         # Rectifier Temp
            '10.8.5.0',         # Battery Runtime
            '10.16.4.1.2.1',    # Last Battery Test Time
            '11.2.1.6.1.7',     # Temp Relay - Clearfield Cabs
        ]
    ),
)

check_plugin_eltek_check = CheckPlugin(
    name = "eltek_check",
    sections = ["eltek_base_config"],
    service_name = "Eltek Health",
    discovery_function = discover_eltek,
    check_function = check_eltek,
)
