#!/usr/bin/env python3
from cmk.agent_based.v2 import SimpleSNMPSection, CheckPlugin, Service, Result, State, startswith, SNMPTree

import datetime

BUSINESS_START = 8    # 08:00
BUSINESS_END = 17     # 17:00
BUSINESS_DAYS = {0, 1, 2, 3, 4}  # Mon-Fri (0=Mon)


def is_business_hours(now: datetime.datetime) -> bool:
    if now.weekday() not in BUSINESS_DAYS:
        return False
    return BUSINESS_START <= now.hour < BUSINESS_END


def parse_eltek(string_table):
    result = {}
    result["eltek_door"] = string_table[0][0]
    return result

def discover_eltek(section):
    yield Service()

def check_eltek(section):
    now = datetime.datetime.now()
    error_status = False
    #Check If and During Biz Hours
    if section["eltek_door"] != "1" and is_business_hours(now):
        yield Result(state=State.WARN, summary="Cabinet Door is Open")
        error_status = True
    #Check If and Not During Biz Hours
    elif section["eltek_door"] != "1" and not is_business_hours(now):
        yield Result(state=State.CRIT, summary="Cabinet Door is Open")
        error_status = True
    if not error_status:
        yield Result(state=State.OK, summary="Cabinet Door is Closed")


snmp_section_eltek_door_config = SimpleSNMPSection(
    name = "eltek_door_config",
    parse_function = parse_eltek,
    detect = startswith(".1.3.6.1.4.1.12148.10.13.8.2.1.2.1", "SmartPack S"),
    fetch = SNMPTree(
        base='.1.3.6.1.4.1.12148.10',
        oids=[
            '11.2.1.2.1.6',     # Cabinet Door Status
        ]
    ),
)

check_plugin_eltek_door = CheckPlugin(
    name = "eltek_door",
    sections = ["eltek_door_config"],
    service_name = "Cabinet Door",
    discovery_function = discover_eltek,
    check_function = check_eltek,
)
