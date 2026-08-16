"""The canonical synthetic operating-state engine for Symbiosis.

The beta intentionally uses fictional scenario content. Time, time-zone, action,
and audit mechanics are real application behaviour. Every visible panel is
derived from the same event object returned here.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import random
from typing import Any
from zoneinfo import ZoneInfo

from symbiosis_profiles import REGIONS, WORLD_PROFILES


def utc_now() -> datetime:
    """Return the single wall-clock reference used by the simulation."""

    return datetime.now(timezone.utc)


def deterministic_int(seed: str, minimum: int, maximum: int) -> int:
    """Produce stable synthetic values without relying on view-side randomness."""

    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    rng = random.Random(int(digest[:16], 16))
    return rng.randint(minimum, maximum)


def regional_state(world_id: str, now: datetime | None = None) -> list[dict[str, Any]]:
    """Build a time-zone-aware regional operating state.

    The regional time is real. Activity, queue load, and handoff conditions are
    fictional and deterministic for the current time window.
    """

    now = now or utc_now()
    is_digital = world_id == "axiom"
    results: list[dict[str, Any]] = []
    time_bucket = now.strftime("%Y-%m-%d-%H-%M")[:15]

    for region in REGIONS:
        local = now.astimezone(ZoneInfo(region["zone"]))
        hour = local.hour
        local_weekday = local.weekday() < 5
        in_business_hours = 7 <= hour < 20
        working = local_weekday and in_business_hours
        handoff_window = local_weekday and (5 <= hour < 7 or 20 <= hour < 22)
        night_watch = not working
        key = f"{world_id}:{region['code']}:{time_bucket}"
        network_load = deterministic_int(key, 24, 92)

        if working:
            local_operating_state = "regional_window"
            motion_mode = "fast"
            status = "Active" if network_load >= 38 else "Ready"
            posture = "Regional operating window"
            load = network_load
        elif handoff_window:
            local_operating_state = "handoff"
            motion_mode = "ambient"
            status = "Handoff"
            posture = "Pre-open / after-hours handoff"
            load = max(14, network_load - 16)
        elif not local_weekday:
            local_operating_state = "weekend"
            motion_mode = "still"
            status = "Network watch" if is_digital else "Weekend watch"
            posture = "Weekend oversight"
            load = max(6, network_load - 42)
        else:
            local_operating_state = "after_hours"
            motion_mode = "still"
            status = "Network watch" if is_digital else "Watch"
            posture = "After-hours monitoring"
            load = max(8, network_load - 35)

        results.append(
            {
                **region,
                "time": local.strftime("%H:%M"),
                "day": local.strftime("%a"),
                "status": status,
                "posture": posture,
                "load": load,
                "working": working,
                "night_watch": night_watch,
                # Local time/day is factual. The activity value and operating
                # route are deterministic synthetic simulation data.
                "local_weekday": local_weekday,
                "in_business_hours": in_business_hours,
                "local_operating_state": local_operating_state,
                "motion_mode": motion_mode,
                "simulation_active": motion_mode != "still",
                "network_active": is_digital,
                "activity_basis": "synthetic_24_7_network" if is_digital else "synthetic_regional_operating_window",
                "network_load": network_load,
            }
        )

    return results


def active_region_label(world_id: str, now: datetime | None = None) -> str:
    """Summarise the most active synthetic region for compact pulse labels."""

    states = regional_state(world_id, now)
    motion_rank = {"fast": 3, "ambient": 2, "still": 1}
    active = max(states, key=lambda region: (motion_rank[region["motion_mode"]], int(region["load"])))
    return f"{active['code']} {active['status'].upper()}"


def scenario_for(world_id: str, event_index: int) -> dict[str, Any]:
    """Return one authoritative event scenario from the selected fictional world."""

    profile = WORLD_PROFILES[world_id]
    templates = profile["templates"]
    template = templates[event_index % len(templates)]
    seed = f"{world_id}:{event_index}:{template['id']}"
    event = {**template}
    event["world_id"] = world_id
    event["world_name"] = profile["name"]
    event["event_number"] = event_index + 1
    event["id"] = f"{template['id']}-{event_index + 1:03d}"
    event["queue_position"] = deterministic_int(seed + ":queue", 1, 8)
    event["related_signals"] = deterministic_int(seed + ":signals", 6, 16)
    event["decision_age_seconds"] = deterministic_int(seed + ":age", 8, 52)
    event["policy"] = {
        "axiom": "AXM-Settlement-4.2",
        "northstar": "NSG-Payments-6.1",
        "asterion": "AST-Risk-3.7",
    }[world_id]
    return event


def outcome_for(event: dict[str, Any], action: str) -> dict[str, str]:
    """Create a simulated outcome from a human-authorized decision action."""

    recommended = event["recommendation_key"]
    option = next((option for option in event["options"] if option["key"] == action), None)
    if option is None:
        option = {
            "key": "escalate",
            "label": "Escalate",
            "protect": "Accountable executive review",
            "expose": "Decision-window delay",
            "conditions": ["Transfer complete evidence bundle", "Retain current policy controls"],
        }
    action_name = option["label"]
    world_id = event["world_id"]

    defaults = {
        "authorize": {
            "state": "Authorized",
            "headline": "Authorization recorded",
            "learning": "Fast action preserved the operating window while accepting the stated exposure.",
        },
        "condition": {
            "state": "Authorized with conditions",
            "headline": "Conditional authorization recorded",
            "learning": "The decision preserved value while making the unresolved assumption explicit and owned.",
        },
        "hold": {
            "state": "Held for review",
            "headline": "Hold and escalation recorded",
            "learning": "The decision protected the highest-control posture at the stated opportunity and timing cost.",
        },
        "escalate": {
            "state": "Escalated",
            "headline": "Executive escalation recorded",
            "learning": "The decision was transferred to the next accountable authority with its uncertainty intact.",
        },
    }
    result = defaults.get(action, defaults["hold"]).copy()
    result["action_name"] = action_name
    result["recommended"] = "Yes" if action == recommended else "No"
    result["value_note"] = option["protect"]
    result["exposure_note"] = option["expose"]
    result["conditions"] = ", ".join(option.get("conditions", [])) or "No additional conditions"
    result["counterfactual"] = next(
        (
            candidate["label"]
            for candidate in event["options"]
            if candidate["key"] != action
        ),
        "An alternate authorization path was not selected.",
    )
    result["world_note"] = {
        "axiom": "Enhanced monitoring remains active through the synthetic settlement window.",
        "northstar": "The fictional payment corridor is monitored through the simulated cutoff.",
        "asterion": "The fictional allocation remains under the simulated reassessment threshold.",
    }[world_id]
    return result


def audit_entry(
    event: dict[str, Any],
    action: str,
    authorizer: dict[str, str],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Create the canonical audit entry shown, exported, and replayed by the UI."""

    now = now or utc_now()
    local = now.astimezone(ZoneInfo(authorizer["zone"]))
    outcome = outcome_for(event, action)

    return {
        "id": f"audit-{event['id']}-{int(now.timestamp())}",
        "timestamp": local.isoformat(timespec="seconds"),
        "display_time": local.strftime("%H:%M:%S %Z"),
        "world": event["world_name"],
        "event_id": event["id"],
        "event": event["title"],
        "action": outcome["action_name"],
        "state": outcome["state"],
        "authorized_by": authorizer["name"],
        "role": authorizer["role"],
        "region": authorizer["city"],
        "policy": event["policy"],
        "confidence": event["confidence"],
        "risk": event["risk"],
        "value": event["value"],
        "outcome": outcome,
    }


def public_snapshot(
    world_id: str,
    event_index: int,
    audit_log: list[dict[str, Any]],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return the complete synthetic world snapshot used for a JSON export."""

    now = now or utc_now()
    profile = WORLD_PROFILES[world_id]
    return {
        "disclosure": "Synthetic institutions, people, events, assets, and outcomes. Time and time-zone logic are live.",
        "generated_at_utc": now.isoformat(timespec="seconds"),
        "world": {
            "name": profile["name"],
            "domain": profile["domain"],
            "profile_id": world_id,
        },
        "event": scenario_for(world_id, event_index),
        "regional_state": regional_state(world_id, now),
        "decision_record": audit_log,
    }
