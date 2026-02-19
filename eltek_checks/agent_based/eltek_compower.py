#!/usr/bin/env python3
from cmk.agent_based.v2 import SNMPSection, CheckPlugin, Service, Result, State, startswith, SNMPTree

def parse_eltek(string_table):
    result = {}
    result["eltek_comp"] = string_table[0][0]
    return result

def discover_eltek(section):
    yield Service()

def check_eltek(section):
    error_status = False
    if section["eltek_comp"] != "1":
        yield Result(state=State.WARN, summary="Commerical Power Alarm!")
        error_status = True
    if not error_status:
        yield Result(state=State.OK, summary="Commerical Power is good.")

snmp_section_eltek_comp_config = SNMPSection(
    name = "eltek_comp_config",
    parse_function = parse_eltek,
    detect = startswith(".1.3.6.1.4.1.12148.10.11.2.1.3.1.8", "Commercial Power"),
    fetch = SNMPTree(
        base='.1.3.6.1.4.1.12148.10',
        oids=[
            '11.2.1.2.1.8',     #Commerical Power Monitor
        ]
    ),
)

check_plugin_eltek_comp = CheckPlugin(
    name = "eltek_comp",
    sections = ["eltek_comp_config"],
    service_name = "Commerical Power",
    discovery_function = discover_eltek,
    check_function = check_eltek,
)
