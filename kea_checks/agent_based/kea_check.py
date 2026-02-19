#!/usr/bin/env python3

from cmk.agent_based.v2 import AgentSection, CheckPlugin, Service, Result, State

def parse_kea(string_table):
    parsed = {}
    return parsed

def discover_kea(section):
    yield Service()

def check_kea(section):
    yield Result(state=State.OK, summary="Everything is fine")

agent_section_kea = AgentSection(
    name = "kea_check",
    parse_function = parse_kea,
)

check_plugin_kea = CheckPlugin(
    name = "kea_check",
    service_name = "ISC KEA CheckMK Common",
    discovery_function = discover_kea,
    check_function = check_kea,
)
