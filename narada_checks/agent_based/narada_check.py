#!/usr/bin/env python3

from cmk.agent_based.v2 import (
    SNMPSection, CheckPlugin, Service, Result, State, Metric, check_levels, startswith, SNMPTree
)

# ------------------------
# Rendering functions
# ------------------------

def render_fahrenheit(temp_c):
    try:
        temp_f = (float(temp_c) * 9 / 5) + 32
        return f"{temp_f:.1f} °F"
    except (TypeError, ValueError):
        return "N/A"

def _render_percent(val):
    try:
        return f"{float(val):.1f} %"
    except (TypeError, ValueError):
        return "N/A"

def _render_ahr(val):
    try:
        return f"{float(val):.1f} Ahr"
    except (TypeError, ValueError):
        return "N/A"

# ------------------------
# Parser: SNMP table for Narada metrics
# ------------------------

def parse_narada_battery_struct(string_table):
    flat_values = string_table[0]
    if len(flat_values) != 24:
        raise ValueError(f"Expected 24 SNMP values, got {len(flat_values)}")

    labels = flat_values[0:8]
    value_strs = flat_values[8:16]
    units = flat_values[16:24]

    result = []
    for i in range(8):
        label = labels[i]
        value_str = value_strs[i]
        unit = units[i]

        if ':' not in label:
            raise ValueError(f"Invalid label format: {label}")
        battery_id, metric = label.split(":", 1)

        try:
            value = int(value_str.decode() if isinstance(value_str, bytes) else value_str)
        except ValueError:
            value = None

        result.append({
            "battery": int(battery_id),
            "metric": metric,
            "raw_value": value,
            "unit": unit.decode() if isinstance(unit, bytes) else unit,
        })

    return result

# ------------------------
# Discovery
# ------------------------

def discover_narada_struct(section):
    seen = set()
    for entry in section:
        seen.add(entry["battery"])
    for b in seen:
        yield Service(item=f"{b}")

# ------------------------
# Main check logic with labels
# ------------------------

def check_narada_struct(item, section):
    battery_index = int(item)
    metrics = {e["metric"]: e for e in section if e["battery"] == battery_index}

    required = ["BattSOC", "BattTempInt", "BattTempAmb", "BattRemCap"]
    missing = [k for k in required if k not in metrics]
    if missing:
        yield Result(state=State.UNKNOWN, summary=f"[Battery {battery_index}] Missing metrics: {', '.join(missing)}")
        return

    soc = metrics["BattSOC"]["raw_value"] / 100
    temp_int_c = metrics["BattTempInt"]["raw_value"] / 10
    temp_amb_c = metrics["BattTempAmb"]["raw_value"] / 10
    remcap = metrics["BattRemCap"]["raw_value"] / 10

    temp_int_f = temp_int_c * 9 / 5 + 32

    if soc < 40:
        yield Result(state=State.WARN, summary=(
            f"[Battery {battery_index}] BattSOC={_render_percent(soc)} LOW"
        ))
    elif temp_int_f > 122:
        yield Result(state=State.WARN, summary=(
            f"[Battery {battery_index}] BattTempInt={render_fahrenheit(temp_int_c)} HIGH"
        ))
    else:
        yield Result(state=State.OK, summary=(
            f"[Battery {battery_index}] "
            f"BattSOC={_render_percent(soc)}, "
            f"BattTempInt={render_fahrenheit(temp_int_c)}, "
            f"BattRemCap={_render_ahr(remcap)}"
        ))

    yield Metric("state_of_charge", soc, boundaries=(0, 100))
    yield Metric("internal_temp", temp_int_c, boundaries=(0, 80), levels=(50, 60))
    yield Metric("ambient_temp", temp_amb_c, boundaries=(0, 80))
    yield Metric("remaining_capacity", remcap)

# ------------------------
# SNMP Section
# ------------------------

snmp_section_narada_battery_table = SNMPSection(
    name="narada_battery_table",
    parse_function=parse_narada_battery_struct,
    detect=startswith(".1.3.6.1.4.1.12148.10.13.24.1.2.1", "1:BattSOC"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.12148.10.13.24.1",
        oids=[
            "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8",  # Labels
            "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8",  # Values
            "4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "4.8",  # Units
        ]
    )
)

# ------------------------
# Plugin Registration
# ------------------------

check_plugin_narada_battery_table = CheckPlugin(
    name="narada_battery_table",
    service_name="Narada Battery %s",
    discovery_function=discover_narada_struct,
    check_function=check_narada_struct,
    sections=["narada_battery_table"],
)
