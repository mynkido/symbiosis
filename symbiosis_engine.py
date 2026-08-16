"""The canonical synthetic operating-state engine for Symbiosis.

The beta intentionally uses fictional scenario content. Time, time-zone, action,
and audit mechanics are real application behaviour. Every visible panel is
derived from the same event object returned here.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import math
import random
import re
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


def _bounded(value: float, minimum: int = 0, maximum: int = 100) -> int:
    """Round a synthetic score into a stable, display-safe range."""

    return max(minimum, min(maximum, int(round(value))))


def _display_value_to_dollars(value: str) -> float:
    """Read the fictional value-at-stake label for scenario projection only."""

    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([KMB]?)", value.replace(",", ""), re.IGNORECASE)
    if not match:
        return 1_000_000.0
    amount = float(match.group(1))
    multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(match.group(2).upper(), 1)
    return amount * multiplier


def decision_telemetry(
    event: dict[str, Any],
    regions: list[dict[str, Any]],
    now: datetime | None = None,
    points: int = 48,
) -> dict[str, Any]:
    """Derive one formal signal trace and scenario range from the event state.

    This is the authoritative bridge between the original formal Symbiosis
    board (Trust / Risk / Friction / projection) and the mobile decision
    cockpit. Values are deterministic synthetic simulation data; regional
    time and the supplied clock are factual application state.
    """

    now = now or utc_now()
    evidence = event["evidence"]
    verified = sum(item["state"] == "verified" for item in evidence)
    conflicting = sum(item["state"] == "conflicting" for item in evidence)
    missing = sum(item["state"] == "missing" for item in evidence)
    risk_base = {"low": 28, "moderate": 48, "elevated": 67, "critical": 86}.get(event["risk"].lower(), 50)
    operating_load = round(sum(int(region["network_load"]) for region in regions) / max(1, len(regions)))

    trust = _bounded(int(event["confidence"]) + (verified * 3) - (conflicting * 4) - (missing * 6), 8, 96)
    risk = _bounded(risk_base + (conflicting * 3) + (missing * 4) - (verified * 2), 8, 96)
    friction = _bounded(20 + (conflicting * 11) + (missing * 17) + max(0, 70 - int(event["confidence"])) * .22, 8, 94)
    latency_ms = int(86 + (friction * 1.7) + (risk * .85) + (operating_load * .35))

    metrics = {
        "trust": trust,
        "risk": risk,
        "friction": friction,
        "latency_ms": latency_ms,
        "operating_load": operating_load,
        "verified": verified,
        "conflicting": conflicting,
        "missing": missing,
    }

    # The trace is stable for a decision, then makes a small deterministic
    # minute-level adjustment. That produces live-looking movement without
    # inventing a second, view-only source of truth.
    phase = deterministic_int(f"{event['id']}:phase", 0, 20) + now.minute
    trace: list[dict[str, int]] = []
    trace_points = max(16, points)
    for index in range(trace_points):
        progress = index / max(1, trace_points - 1)
        wave = math.sin((index + phase) * .47) * 7 + math.cos((index + phase) * .18) * 4
        trust_noise = deterministic_int(f"{event['id']}:trace:trust:{index}", -6, 6)
        risk_noise = deterministic_int(f"{event['id']}:trace:risk:{index}", -7, 7)
        friction_noise = deterministic_int(f"{event['id']}:trace:friction:{index}", -6, 6)
        load_noise = deterministic_int(f"{event['id']}:trace:load:{index}", -10, 10)
        # Older points sit a little farther from the current score; the last
        # point resolves exactly to the current metric for clear inspection.
        trust_point = _bounded(trust + wave + trust_noise - ((1 - progress) * 5))
        risk_point = _bounded(risk - (wave * .72) + risk_noise + ((1 - progress) * 3))
        friction_point = _bounded(friction + (wave * .55) + friction_noise)
        load_point = _bounded(operating_load + (wave * .85) + load_noise)
        trace.append(
            {
                "trust": trust if index == trace_points - 1 else trust_point,
                "risk": risk if index == trace_points - 1 else risk_point,
                "friction": friction if index == trace_points - 1 else friction_point,
                "load": operating_load if index == trace_points - 1 else load_point,
            }
        )

    # A repeatable fat-tailed synthetic scenario range. This follows the
    # original board-risk idea while making its dependencies explicit here.
    base_value = _display_value_to_dollars(str(event["value"]))
    base_exposure = base_value * ((risk / 100) * .19 + (friction / 100) * .11)
    seed = int(hashlib.sha256(f"{event['id']}:projection".encode("utf-8")).hexdigest()[:16], 16)
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(360):
        multiplier = math.exp(rng.gauss(0.0, .42 + (risk / 700)))
        shock = 1.0 + (max(0.0, rng.gauss(.14, .11)) if risk >= 62 else 0.0)
        samples.append(base_exposure * multiplier * shock)
    samples.sort()

    def percentile(percent: int) -> float:
        index = int(round((percent / 100) * (len(samples) - 1)))
        return samples[max(0, min(len(samples) - 1, index))]

    low, high = samples[0], samples[-1]
    bucket_count = 18
    step = max(1.0, (high - low) / bucket_count)
    histogram = [0] * bucket_count
    for sample in samples:
        bucket = max(0, min(bucket_count - 1, int((sample - low) / step)))
        histogram[bucket] += 1

    return {
        "metrics": metrics,
        "trace": trace,
        "projection": {
            "base_exposure": base_exposure,
            "p50": percentile(50),
            "p90": percentile(90),
            "p99": percentile(99),
            "histogram": histogram,
            "minimum": low,
            "maximum": high,
        },
        "time_basis": now.strftime("%Y-%m-%d %H:%M UTC"),
    }


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
