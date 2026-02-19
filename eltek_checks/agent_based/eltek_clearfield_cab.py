#!/usr/bin/env python3
from cmk.agent_based.v2 import SNMPSection, CheckPlugin, Service, Result, State, startswith, SNMPTree

def parse_eltek(string_table):
    result = {}
    result["clearfield_cab_tmp"] = string_table[0][0]
    return result

def discover_eltek(section):
    yield Service()

def check_eltek(section):
    error_status = False
    if int(section["clearfield_cab_tmp"]) >= 142:
        yield Result(state=State.WARN, summary="Clearfield Cabinet Temp is High >142f")
        error_status = True
    if int(section["clearfield_cab_tmp"]) >= 148:
        yield Result(state=State.CRIT, summary="Clearfield Cabinet Temp is High >148f")
        error_status = True
    if not error_status:
        yield Result(state=State.OK, summary="Clearfield Cabinet Temp is OK")

snmp_section_clearfield_cab_tmp_config = SNMPSection(
    name = "clearfield_cab_tmp_config",
    parse_function = parse_eltek,
    detect = startswith(".1.3.6.1.4.1.12148.10.11.2.1.3.1.7", "Cabinet Temp"),
    fetch = SNMPTree(
        base='.1.3.6.1.4.1.12148.10',
        oids=[
            '11.2.1.6.1.7',     # Temp Relay - Clearfield Cabs
        ]
    ),
)

check_plugin_clearfield_cab_tmp = CheckPlugin(
    name = "clearfield_cab_tmp",
    sections = ["clearfield_cab_tmp_config"],
    service_name = "ClearField Cabinet Temp",
    discovery_function = discover_eltek,
    check_function = check_eltek,
)
