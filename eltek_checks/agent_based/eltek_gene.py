#!/usr/bin/env python3
from cmk.agent_based.v2 import SNMPSection, CheckPlugin, Service, Result, State, startswith, SNMPTree

def parse_eltek(string_table):
    result = {}
    result["eltek_gene"] = string_table[0][0]
    return result

def discover_eltek(section):
    yield Service()

def check_eltek(section):
    error_status = False
    if section["eltek_gene"] != "1":
        yield Result(state=State.WARN, summary="Generator is running!")
        error_status = True
    if not error_status:
        yield Result(state=State.OK, summary="Generator is not running.")

snmp_section_eltek_gene_config = SNMPSection(
    name = "eltek_gene_config",
    parse_function = parse_eltek,
    detect = startswith(".1.3.6.1.4.1.12148.10.11.2.1.3.1.10", "Generator"),
    fetch = SNMPTree(
        base='.1.3.6.1.4.1.12148.10',
        oids=[
            '11.2.1.2.1.10',     # Generator Status
        ]
    ),
)

check_plugin_eltek_gene = CheckPlugin(
    name = "eltek_gene",
    sections = ["eltek_gene_config"],
    service_name = "Eltek Generator",
    discovery_function = discover_eltek,
    check_function = check_eltek,
)
