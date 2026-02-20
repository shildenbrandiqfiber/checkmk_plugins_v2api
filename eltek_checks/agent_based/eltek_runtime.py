#!/usr/bin/env python3
from cmk.agent_based.v2 import SimpleSNMPSection, CheckPlugin, Service, Result, State, Metric, startswith, SNMPTree

def parse_eltek(string_table):
    result = {}
    result["battery_runtime"] = string_table[0][0]
    result["generator_field"] = string_table[0][1]
    return result

def discover_eltek(section):
    yield Service()

def check_eltek(section):
    battery_runtime = int(section["battery_runtime"])
    runtime_hours = battery_runtime // 60
    runtime_minutes = battery_runtime % 60
    field = section["generator_field"]

    error_status = False
    #if generator_field not null -> this is a core site that has a external generator, not controlled by eltek.
    if "generator" in section["generator_field"].lower():
        if int(section["battery_runtime"]) <= 60:
            yield Result(state=State.CRIT, summary=f"Core Site Battery Runtime < 1Hrs - {runtime_hours}h {runtime_minutes}m left - CHECK GENERATOR")
            error_status = True
    else:
    #if generator_Field is null -> this is a site that does not have a generator
        if int(section["battery_runtime"]) <= 240:
            yield Result(state=State.CRIT, summary=f"Battery Runtime < 4Hrs - {runtime_hours}h {runtime_minutes}m left - DEPLOY GENERATOR")
            error_status = True

    if not error_status:
        yield Result(state=State.OK,summary=f"Battery Runtime OK - {runtime_hours}h {runtime_minutes}m left")

    # Yield the metric for graphing
    yield Metric(
        name = "battery_runtime",
        value = battery_runtime,
        boundaries = (0, 3000),
        levels = (240,60),
    )

snmp_section_eltek_runtime_config = SimpleSNMPSection(
    name = "eltek_runtime_config",
    parse_function = parse_eltek,
    detect = startswith(".1.3.6.1.4.1.12148.10.13.8.2.1.2.1", "SmartPack S"),
    fetch = SNMPTree(
        base='.1.3.6.1.4.1.12148.10',
        oids=[
            '10.8.5.0',     # Battery Runtime
            '2.7.0',       # Eltek Serial Number field used as Generator Field
        ]
    ),
)

check_plugin_eltek_runtime = CheckPlugin(
    name = "eltek_runtime",
    sections = ["eltek_runtime_config"],
    service_name = "Battery Runtime",
    discovery_function = discover_eltek,
    check_function = check_eltek,
)
