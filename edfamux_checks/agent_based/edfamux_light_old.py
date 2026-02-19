#!/usr/bin/env python3
### works with Edfamux Software of at least; 2.08.8
import struct
from ctypes import pointer, c_int, cast, POINTER, c_float
from cmk.agent_based.v2 import SNMPSection, CheckPlugin, Service, Result, State, Metric, startswith, SNMPTree

def is_hex(s):
    hex_digits = set("0123456789abcdef")
    for char in s:
        if not (char in hex_digits):
            return False
    return True

def convert(s):
    s.strip()                        # remove whitespace
    i = int(s, 16)                   # convert from hex to a Python int
    cp = pointer(c_int(i))           # make this into a c integer
    fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
    return fp.contents.value         # dereference the pointer, get the float

def parse_edfamux_old(string_table):
    result = {}
    result["muxgain"] = string_table[0][0]
    result["muxpowerin"] = string_table[0][1]
    result["muxpowerout"] = string_table[0][2]
    result["muxtemp"] = string_table[0][3]
    result["demuxgain"] = string_table[0][4]
    result["demuxpowerin"] = string_table[0][5]
    result["demuxpowerout"] = string_table[0][6]
    result["demuxtemp"] = string_table[0][7]
    return result

def discover_edfamux_old(section):
    yield Service()

def check_edfamux_old(section):
    error_status = False
    muxgain = float(section["muxgain"].rstrip('\x00'))
    muxpowerin = float(section["muxpowerin"].rstrip('\x00'))
    muxpowerout = float(section["muxpowerout"].rstrip('\x00'))
    muxtemp = float(section["muxtemp"].rstrip('\x00'))
    demuxgain = float(section["demuxgain"].rstrip('\x00'))
    demuxpowerin = float(section["demuxpowerin"].rstrip('\x00'))
    demuxpowerout = float(section["demuxpowerout"].rstrip('\x00'))
    demuxtemp = float(section["demuxtemp"].rstrip('\x00'))

    if not error_status:
        yield Result(state=State.OK, summary="Edfamux common levels normal, values collected!")

    # Yield the metric for graphing
    yield Metric(
        name = "MUX-Gain",
        value = muxgain,
        boundaries = (-10, 10),
        levels = (20,30)
    )
    yield Metric(
        name = "MUX-Pre(input)",
        value = muxpowerin,
        boundaries = (-40, 40),
        levels = (-10,-20)
    )
    yield Metric(
        name = "MUX-Post(output)",
        value = muxpowerout,
        boundaries = (-40, 40),
        levels = (20,30)
    )
    yield Metric(
        name = "MUX-Temp(c)",
        value = muxtemp,
        boundaries = (-40, 40),
        levels = (40,50)
    )
    yield Metric(
        name = "DEMUX-Gain",
        value = demuxgain,
        boundaries = (-10, 10),
        levels = (20,30)
    )
    yield Metric(
        name = "DEMUX-Power-In-(OSP)",
        value = demuxpowerin,
        boundaries = (-40, 40),
        levels = (-10,-20)
    )
    yield Metric(
        name = "DEMUX-Post(output)",
        value = demuxpowerout,
        boundaries = (-40, 40),
        levels = (20,30)
    )
    yield Metric(
        name = "DEMUX-Temp(c)",
        value = demuxtemp,
        boundaries = (-40, 40),
        levels = (40,50)
    )

snmp_section_edfamux_base_config_v2 = SNMPSection(
    name = "edfamux_base_config_v2",
    parse_function = parse_edfamux_old,
    detect = startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.51628"),
    fetch = SNMPTree(
        base='.1.3.6.1.4.1.51628.1',
        oids=[
            '2.2.0', #0 MUXGAIN
            '2.3.0', #1 MUXPOWERIN
            '2.4.0', #2 MUXPOWEROUT
            '2.5.0', #3 MUXTemp
            '3.2.0', #4 DEMUXGAIN
            '3.3.0', #5 DEMUXPowerIN
            '3.4.0', #6 DEMUXPowerOUT
            '3.5.0'  #7 DEMUXTemp
        ]
    ),
)

check_plugin_edfamux_check_v2 = CheckPlugin(
    name = "edfamux_check_v2",
    sections = ["edfamux_base_config_v2"],
    service_name = "edfamux Health v2",
    discovery_function = discover_edfamux_old,
    check_function = check_edfamux_old,
)
