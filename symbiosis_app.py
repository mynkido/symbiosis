"""Symbiosis by Mynki See.

A mobile-first decision cockpit for consequential institutional events.

This beta is deliberately a live operating simulation: local device time,
regional time-zone logic, state transitions, human authorizations, and audit
records are real application behaviour. Institutions, people, assets, events,
and outcomes are synthetic.
"""

from __future__ import annotations

from datetime import datetime
import html
import importlib
import json
from typing import Any
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components

from symbiosis_engine import (
    active_region_label,
    audit_entry,
    public_snapshot,
    regional_state,
    scenario_for,
    utc_now,
)
from symbiosis_profiles import WORLD_PROFILES, world_options
import symbiosis_theme


st.set_page_config(
    page_title="Symbiosis · Mynki See",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "Symbiosis is a live operating simulation using synthetic scenario data."},
)


def esc(value: Any) -> str:
    """Escape all synthetic content passed into small HTML rendering helpers."""

    return html.escape(str(value), quote=True)


def private_value(value: str, private_mode: bool) -> str:
    """Mask sensitive synthetic figures and names in the private presentation mode."""

    return "••••••" if private_mode else value


def initialize_state() -> None:
    """Initialize the one canonical Streamlit session state."""

    defaults: dict[str, Any] = {
        "sym_started": False,
        "sym_world": "axiom",
        "sym_event_index": 0,
        "sym_audit": [],
        "sym_pending_action": None,
        "sym_last_outcome": None,
        "sym_last_outcome_event": None,
        "sym_private_mode": False,
        "sym_show_analyze": False,
        "sym_view": "glance",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_current_world(clear_audit: bool = False) -> None:
    """Reset the simulated event state while retaining deliberate user choices."""

    st.session_state.sym_event_index = 0
    st.session_state.sym_pending_action = None
    st.session_state.sym_last_outcome = None
    st.session_state.sym_last_outcome_event = None
    st.session_state.sym_view = "glance"
    if clear_audit:
        st.session_state.sym_audit = []


def handle_world_change(world_id: str) -> None:
    """Switch worlds and prevent a previous world's decision state leaking across."""

    if world_id != st.session_state.sym_world:
        st.session_state.sym_world = world_id
        reset_current_world(clear_audit=False)


def render_live_clock(world_name: str) -> None:
    """Render a client-side live clock so seconds advance without an app rerun."""

    safe_world = esc(world_name)
    components.html(
        """
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  html, body { margin: 0; background: transparent; overflow: hidden; }
  .clock-shell {
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 0 11px;
    border: 1px solid rgba(47,128,237,.18);
    border-radius: 14px;
    color: #142a43;
    background: linear-gradient(110deg, rgba(255,255,255,.92), rgba(243,250,255,.88));
    box-shadow: 0 9px 28px rgba(44, 91, 137, .09);
    font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }
  .left { min-width: 0; display: flex; align-items: center; gap: 8px; }
  .light { width: 7px; height: 7px; border-radius: 50%; background: #00b894; box-shadow: 0 0 0 4px rgba(0,184,148,.12); }
  .label { color: #527087; font-size: 10px; font-weight: 750; letter-spacing: .1em; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .time { color: #142a43; font-size: 12px; font-weight: 760; letter-spacing: .01em; text-align: right; white-space: nowrap; }
  .sub { color: #6f8799; font-size: 10px; font-weight: 600; }
  @media (max-width: 460px) { .label { max-width: 145px; } .sub { display: none; } }
</style>
<div class="clock-shell" role="status" aria-live="polite">
  <div class="left">
    <span class="light"></span>
    <span class="label">""" + safe_world + """ · Live operating simulation</span>
  </div>
  <div class="time">
    <span id="local-time">Loading…</span>
    <span class="sub" id="utc-time"></span>
  </div>
</div>
<script>
  const localNode = document.getElementById("local-time");
  const utcNode = document.getElementById("utc-time");
  function updateClock() {
    const now = new Date();
    const localTime = new Intl.DateTimeFormat(undefined, {
      weekday: "short", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false
    }).format(now);
    const utcTime = new Intl.DateTimeFormat("en-GB", {
      hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false, timeZone: "UTC", timeZoneName: "short"
    }).format(now);
    localNode.textContent = localTime;
    utcNode.textContent = " · " + utcTime;
  }
  updateClock();
  window.setInterval(updateClock, 1000);
</script>
        """,
        height=49,
        scrolling=False,
    )


def render_brand(profile: dict[str, Any]) -> None:
    """Render the product identity and quiet disclosure."""

    st.markdown(
        f"""
<div class="sym-brand">
  <div class="sym-logo" aria-hidden="true">S</div>
  <div>
    <div class="sym-kicker">Mynki See</div>
    <h1 class="sym-title">Symbiosis</h1>
  </div>
</div>
<p class="sym-subtitle">
  The decision cockpit for consequential institutional events. See evidence,
  uncertainty, consequence, and the strongest next action—before an accountable
  human authorizes it.
</p>
<div class="sym-disclosure">
  Live operating simulation · Synthetic institutions, people, events, assets, and outcomes ·
  Live device time and time-zone logic
</div>
        """,
        unsafe_allow_html=True,
    )
    render_live_clock(profile["name"])


def render_glance_header(profile: dict[str, Any]) -> None:
    """Render only the live identity needed before a mobile decision."""

    st.markdown(
        f"""
<div class="sym-compact-header">
  <div class="sym-compact-mark" aria-hidden="true">S</div>
  <div>
    <div class="sym-kicker">Mynki See · live decision</div>
    <div class="sym-compact-title">Symbiosis <span>/{esc(profile["short_name"])}</span></div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    render_live_clock(profile["short_name"])


def _short_signal(value: str) -> str:
    """Keep the first-decision instruction deliberately skimmable."""

    first_sentence = value.split(".", maxsplit=1)[0].strip()
    return first_sentence or value


def render_decision_pulse(
    event: dict[str, Any],
    profile: dict[str, Any],
    regions: list[dict[str, Any]],
    private_mode: bool,
) -> None:
    """Render the active decision as a visual pulse rather than a report."""

    evidence = event["evidence"]
    verified = sum(item["state"] == "verified" for item in evidence)
    conflicting = sum(item["state"] == "conflicting" for item in evidence)
    missing = sum(item["state"] == "missing" for item in evidence)
    blocker = next((item for item in evidence if item["state"] == "missing"), evidence[-1])
    active_region = max(regions, key=lambda region: int(region["load"]))
    route = "  →  ".join(region["code"] for region in regions[:3])
    ring_length = int(289 * int(event["confidence"]) / 100)
    motion_class = "sym-risk-elevated" if event["risk"].lower() == "elevated" else "sym-risk-steady"
    signal = esc(_short_signal(event["signal"]))
    title = esc(private_value(event["title"], private_mode))
    value = esc(private_value(event["value"], private_mode))
    metric_value = esc(private_value(profile["metric_value"], private_mode))
    ticker = (
        f"{profile['short_name']} · {route} · {active_region['code']} {active_region['status'].upper()} "
        f"· {profile['open_cases']} ACTIVE DECISIONS · {profile['review_cases']} HUMAN REVIEWS "
        f"· {metric_value} {profile['metric_label'].upper()} · POLICY {event['policy']}"
    )
    ticker_safe = esc(ticker)

    st.markdown(
        f"""
<section class="sym-glance" aria-label="Active decision">
  <div class="sym-glance-status">
    <span class="sym-status"><span class="sym-dot amber"></span> Action required</span>
    <span class="sym-glance-queue">Queue {event["queue_position"]} · {esc(event["window"])}</span>
  </div>

  <div class="sym-ticker" aria-label="Global simulation activity">
    <div class="sym-ticker-track"><span>{ticker_safe}</span><span aria-hidden="true">{ticker_safe}</span></div>
  </div>

  <div class="sym-live-scene {motion_class}">
    <div class="sym-scene-grid" aria-hidden="true"></div>
    <svg class="sym-flow-map" viewBox="0 0 600 280" preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id="sym-flow-gradient" x1="0" x2="1">
          <stop offset="0%" stop-color="#2f80ed" stop-opacity=".16" />
          <stop offset="50%" stop-color="#00d2ff" stop-opacity=".96" />
          <stop offset="100%" stop-color="#27ae89" stop-opacity=".24" />
        </linearGradient>
        <filter id="sym-glow"><feGaussianBlur stdDeviation="3" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
      </defs>
      <path class="sym-ambient-wave sym-ambient-wave-a" d="M-35,86 C72,24 117,174 218,104 S348,34 442,120 S555,184 650,84" />
      <path class="sym-ambient-wave sym-ambient-wave-b" d="M-30,185 C75,121 123,241 236,167 S379,102 479,190 S575,242 650,154" />
      <path class="sym-ambient-wave sym-ambient-wave-c" d="M-20,144 C78,192 146,66 250,144 S378,215 492,109 S573,35 650,114" />
      <path class="sym-flow-base" d="M-20,212 C96,226 93,58 227,107 S382,248 508,92 S630,80 650,46" />
      <path class="sym-flow-active" d="M-20,212 C96,226 93,58 227,107 S382,248 508,92 S630,80 650,46" />
      <circle class="sym-flow-node n-one" cx="112" cy="104" r="5" />
      <circle class="sym-flow-node n-two" cx="292" cy="173" r="5" />
      <circle class="sym-flow-node n-three" cx="508" cy="92" r="5" />
      <circle class="sym-flow-packet" r="5" filter="url(#sym-glow)"><animateMotion dur="4.8s" repeatCount="indefinite" path="M-20,212 C96,226 93,58 227,107 S382,248 508,92 S630,80 650,46" /></circle>
    </svg>
    <div class="sym-scene-node sym-scene-node-a"><span>LIVE</span><b>{esc(active_region["code"])}</b></div>
    <div class="sym-scene-node sym-scene-node-b"><span>SIGNALS</span><b>{event["related_signals"]}</b></div>
    <div class="sym-orbit sym-orbit-one" aria-hidden="true"><i></i><i></i><i></i></div>
    <div class="sym-orbit sym-orbit-two" aria-hidden="true"><i></i><i></i></div>
    <div class="sym-decision-orb" style="--ring-length:{ring_length}; --world-accent:{esc(profile['accent'])}">
      <div class="sym-orb-halo"></div>
      <svg class="sym-confidence-ring" viewBox="0 0 112 112" aria-hidden="true">
        <circle class="sym-ring-track" cx="56" cy="56" r="46" />
        <circle class="sym-ring-value" cx="56" cy="56" r="46" />
      </svg>
      <div class="sym-orb-core">
        <span>CONFIDENCE</span>
        <strong>{event["confidence"]}%</strong>
        <small>{esc(event["risk"])} exposure</small>
      </div>
    </div>
  </div>

  <div class="sym-glance-title-row">
    <div>
      <div class="sym-glance-type">{esc(event["type"])}</div>
      <h2>{title}</h2>
    </div>
    <div class="sym-glance-value"><span>AT STAKE</span><b>{value}</b></div>
  </div>

  <div class="sym-action-signal">
    <div class="sym-action-label">Strongest next action</div>
    <div class="sym-action-value">{esc(event["recommendation"])}</div>
    <p>{signal}</p>
  </div>

  <div class="sym-glance-metrics" aria-label="Decision signal summary">
    <div class="sym-glance-metric verified"><b>{verified}</b><span>verified</span><i></i></div>
    <div class="sym-glance-metric conflict"><b>{conflicting}</b><span>conflict</span><i></i></div>
    <div class="sym-glance-metric missing"><b>{missing}</b><span>blocker</span><i></i></div>
    <div class="sym-glance-metric value"><b>{value}</b><span>at stake</span><i></i></div>
  </div>

  <div class="sym-blocker-strip">
    <span class="sym-dot amber"></span>
    <strong>1 blocker</strong>
    <span>{esc(blocker["source"])} refresh required</span>
    <span class="sym-blocker-arrow" aria-hidden="true">↗</span>
  </div>

</section>
        """,
        unsafe_allow_html=True,
    )


def render_glance_futures(event: dict[str, Any], private_mode: bool) -> None:
    """Expose three outcomes as visual scan cards before their detailed rationale."""

    cards: list[str] = []
    short_labels = {"authorize": "NOW", "condition": "CONDITIONS", "hold": "HOLD"}
    for option in event["options"]:
        tone = "recommended" if option["tone"] == "recommended" else option["key"]
        card_value = esc(private_value(option["protect"], private_mode))
        cards.append(
            f"""
<article class="sym-future-scan {tone}">
  <div class="sym-future-scan-top"><span>{short_labels.get(option["key"], option["key"].upper())}</span>{'<em>BEST</em>' if option["tone"] == "recommended" else ''}</div>
  <b>{card_value}</b>
  <div class="sym-scan-bar"><i style="--scan:{option["confidence"]}%"></i></div>
  <small>{option["confidence"]}% confidence</small>
</article>
            """
        )
    st.markdown(
        f"""
<div class="sym-scan-head"><span>Three possible futures</span><small>Compare in review</small></div>
<div class="sym-future-scan-grid">{"".join(cards)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_glance_controls(event: dict[str, Any]) -> None:
    """Keep a decisive, thumb-reachable next step above all deep detail."""

    cta, hold = st.columns([1.35, .65], gap="small")
    with cta:
        if st.button(
            f"Review · {event['recommendation']}",
            key=f"{event['id']}-open-review",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.sym_view = "review"
            st.rerun()
    with hold:
        if st.button("Hold", key=f"{event['id']}-quick-hold", use_container_width=True):
            st.session_state.sym_pending_action = "hold"
            st.session_state.sym_view = "review"
            st.rerun()
    st.markdown(
        '<div class="sym-glance-footnote">AI recommends. An accountable human authorizes.</div>',
        unsafe_allow_html=True,
    )


def render_global_pulse(profile: dict[str, Any], private_mode: bool) -> list[dict[str, Any]]:
    """Render the global state that roots the entire simulation in present time."""

    now = utc_now()
    states = regional_state(profile["id"], now)
    active_label = active_region_label(profile["id"], now)
    st.markdown(
        f"""
<div class="sym-global">
  <div class="sym-global-world">
    <div class="sym-status"><span class="sym-dot green"></span> Global pulse</div>
    <strong>{esc(profile["name"])}</strong>
    <span>{esc(profile["subtitle"])} · {esc(active_label)} · Synthetic world state</span>
  </div>
  <div class="sym-global-metrics">
    <div class="sym-global-metric"><b>{profile["open_cases"]}</b>active decisions</div>
    <div class="sym-global-metric"><b>{profile["review_cases"]}</b>need human review</div>
    <div class="sym-global-metric"><b>{private_value(profile["metric_value"], private_mode)}</b>{esc(profile["metric_label"]).lower()}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    cards: list[str] = []
    for region in states:
        is_watch = region["status"] == "Watch"
        opacity = max(.22, int(region["load"]) / 100)
        cards.append(
            f"""
<div class="sym-region" style="--pulse-opacity:{opacity:.2f}">
  <div class="sym-region-head">{esc(region["city"])} · {esc(region["code"])}</div>
  <div class="sym-region-time">{esc(region["time"])}</div>
  <div class="sym-region-state {'watch' if is_watch else ''}">{esc(region["status"])} · {region["load"]}% load</div>
</div>
            """
        )

    st.markdown(f'<div class="sym-region-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    return states


def render_event_and_recommendation(
    event: dict[str, Any], profile: dict[str, Any], private_mode: bool
) -> None:
    """Render the first-screen decision moment."""

    event_col, recommendation_col = st.columns([1.38, .84], gap="medium")
    with event_col:
        st.markdown(
            f"""
<section class="sym-card">
  <div class="sym-card-inner">
    <div class="sym-card-header">
      <div class="sym-status"><span class="sym-dot amber"></span> Human authorization required</div>
      <span class="sym-badge">Queue {event["queue_position"]} · {event["type"]}</span>
    </div>
    <div class="sym-event-name">{esc(private_value(event["title"], private_mode))}</div>
    <div class="sym-event-context">
      {esc(private_value(event["origin"], private_mode))} → {esc(private_value(event["destination"], private_mode))}<br>
      {esc(private_value(event["notional"], private_mode))}
    </div>
    <div class="sym-value-grid">
      <div class="sym-value-cell">
        <div class="sym-value-label">Value at stake</div>
        <div class="sym-value">{esc(private_value(event["value"], private_mode))}</div>
      </div>
      <div class="sym-value-cell">
        <div class="sym-value-label">Decision window</div>
        <div class="sym-value">{esc(event["window"])}</div>
      </div>
      <div class="sym-value-cell">
        <div class="sym-value-label">Current exposure</div>
        <div class="sym-value">{esc(event["risk"])}</div>
      </div>
    </div>
  </div>
</section>
            """,
            unsafe_allow_html=True,
        )
    with recommendation_col:
        st.markdown(
            f"""
<section class="sym-recommendation">
  <div class="sym-recommendation-title">Strongest next action</div>
  <div class="sym-recommendation-action">{esc(event["recommendation"])}</div>
  <div class="sym-recommendation-copy">{esc(event["signal"])}</div>
  <div class="sym-confidence">
    <strong>{event["confidence"]}%</strong>
    <span>confidence<br>{esc(event["risk"])} exposure</span>
  </div>
</section>
            """,
            unsafe_allow_html=True,
        )


def render_evidence(event: dict[str, Any]) -> None:
    """Render evidence as a decision-facing constellation rather than a raw table."""

    st.markdown(
        """
<div class="sym-section-head">
  <div class="sym-section-title">Evidence state</div>
  <div class="sym-section-note">Verified, conflicting, and missing inputs remain visible</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    cards: list[str] = []
    for evidence in event["evidence"]:
        state = evidence["state"]
        cards.append(
            f"""
<article class="sym-evidence">
  <div class="sym-evidence-top">
    <div class="sym-evidence-source">{esc(evidence["source"])}</div>
    <span class="sym-evidence-state {esc(state)}">{esc(state)}</span>
  </div>
  <div class="sym-evidence-claim">{esc(evidence["claim"])}</div>
  <div class="sym-evidence-meta">
    <span>{esc(evidence["recency"])}</span>
    <span>{esc(evidence["reliability"])} reliability</span>
    <span>{esc(evidence["impact"])}</span>
  </div>
</article>
            """
        )
    st.markdown(f'<div class="sym-evidence-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="sym-challenge" style="margin-top:.68rem">
  <h3>What could make this decision wrong?</h3>
  <p>{esc(event["challenge"])}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_futures(event: dict[str, Any]) -> None:
    """Render mutually exclusive decision futures and their trade-offs."""

    st.markdown(
        """
<div class="sym-section-head">
  <div class="sym-section-title">Decision futures</div>
  <div class="sym-section-note">Compare what each action could cost, protect, expose, or unlock</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(len(event["options"]), gap="small")
    for column, option in zip(columns, event["options"]):
        classes = "sym-future"
        if option["tone"] == "recommended":
            classes += " recommended"
        elif option["tone"] == "risk":
            classes += " sym-future-risk"
        condition_text = ""
        if option.get("conditions"):
            condition_text = f'<div class="sym-future-v">{esc(option["conditions"][0])}</div>'
        with column:
            st.markdown(
                f"""
<article class="{classes}">
  <div class="sym-status"><span class="sym-dot {'green' if option["tone"] == "recommended" else 'amber' if option["tone"] == "neutral" else 'red'}"></span>
    {'Recommended' if option["tone"] == "recommended" else 'Available path'}
  </div>
  <div class="sym-future-label">{esc(option["label"])}</div>
  <div class="sym-future-summary">{esc(option["summary"])}</div>
  <div class="sym-future-row">
    <div><div class="sym-future-k">Could protect / unlock</div><div class="sym-future-v">{esc(option["protect"])}</div></div>
    <div><div class="sym-future-k">Could expose / cost</div><div class="sym-future-v">{esc(option["expose"])}</div></div>
    <div><div class="sym-future-k">Friction · confidence</div><div class="sym-future-v">{esc(option["friction"])} · {option["confidence"]}%</div></div>
    {f'<div><div class="sym-future-k">Primary condition</div>{condition_text}</div>' if condition_text else ''}
  </div>
</article>
                """,
                unsafe_allow_html=True,
            )


def render_action_controls(event: dict[str, Any], profile: dict[str, Any]) -> None:
    """Render a human authorization flow with an explicit confirmation stage."""

    st.markdown(
        '<div class="sym-section-head"><div class="sym-section-title">Human authorization</div><div class="sym-section-note">The machine recommends. The accountable person authorizes.</div></div>',
        unsafe_allow_html=True,
    )

    action_names = {
        "authorize": "Authorize",
        "condition": "With conditions",
        "hold": "Hold",
        "escalate": "Escalate",
    }
    pending = st.session_state.sym_pending_action
    if pending is None:
        st.markdown(
            '<div class="sym-action-caption">Select an action. Any selected action is confirmed with the evidence, policy, and accountable authority on record.</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(4, gap="small")
        for column, action in zip(cols, action_names):
            with column:
                clicked = st.button(
                    action_names[action],
                    key=f"{event['id']}-{action}",
                    type="primary" if action == event["recommendation_key"] else "secondary",
                    use_container_width=True,
                )
                if clicked:
                    st.session_state.sym_pending_action = action
                    st.rerun()
        return

    option = next((option for option in event["options"] if option["key"] == pending), None)
    conditions = option.get("conditions", []) if option else ["Transfer the complete evidence bundle", "Retain current policy controls"]
    action_title = action_names[pending]
    condition_items = "".join(f"<li>{esc(condition)}</li>" for condition in conditions)
    st.markdown(
        f"""
<div class="sym-confirm">
  <strong>You are preparing to {esc(action_title.lower())}</strong>
  <span>
    Accountable human: {esc(profile["current_user"]["name"])} · {esc(profile["current_user"]["role"])}<br>
    Policy: {esc(event["policy"])}
  </span>
  <span><ul style="margin:.4rem 0 0;padding-left:1.1rem">{condition_items}</ul></span>
</div>
        """,
        unsafe_allow_html=True,
    )
    confirm_col, cancel_col = st.columns([1.25, .75], gap="small")
    with confirm_col:
        confirm = st.button(
            f"Confirm {action_title.lower()}",
            key=f"{event['id']}-confirm-{pending}",
            type="primary",
            use_container_width=True,
        )
    with cancel_col:
        cancel = st.button(
            "Back",
            key=f"{event['id']}-cancel-{pending}",
            use_container_width=True,
        )
    if cancel:
        st.session_state.sym_pending_action = None
        st.rerun()
    if confirm:
        entry = audit_entry(event, pending, profile["current_user"])
        st.session_state.sym_audit.insert(0, entry)
        st.session_state.sym_last_outcome = entry["outcome"]
        st.session_state.sym_last_outcome_event = event["id"]
        st.session_state.sym_pending_action = None
        st.rerun()


def render_outcome(event: dict[str, Any], private_mode: bool) -> None:
    """Show the immediate simulated result only for the selected event."""

    outcome = st.session_state.sym_last_outcome
    if not outcome or st.session_state.sym_last_outcome_event != event["id"]:
        return

    st.markdown(
        f"""
<div class="sym-section-head">
  <div class="sym-section-title">Decision record created</div>
  <div class="sym-section-note">Synthetic outcome · accountable action preserved</div>
</div>
<section class="sym-card">
  <div class="sym-card-inner">
    <div class="sym-status"><span class="sym-dot green"></span> {esc(outcome["state"])}</div>
    <div class="sym-event-name" style="font-size:1.32rem">{esc(outcome["headline"])}</div>
    <div class="sym-event-context">{esc(outcome["learning"])}</div>
    <div class="sym-outcome-grid">
      <div class="sym-outcome-cell"><div class="sym-value-label">Value protected / unlocked</div><b>{esc(private_value(outcome["value_note"], private_mode))}</b></div>
      <div class="sym-outcome-cell"><div class="sym-value-label">Remaining exposure</div><b>{esc(outcome["exposure_note"])}</b></div>
      <div class="sym-outcome-cell"><div class="sym-value-label">Counterfactual not selected</div><b>{esc(outcome["counterfactual"])}</b></div>
    </div>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_timeline(audit_log: list[dict[str, Any]], private_mode: bool) -> None:
    """Render a human-readable audit timeline rather than a raw event table."""

    st.markdown(
        '<div class="sym-section-head"><div class="sym-section-title">Accountable decision record</div><div class="sym-section-note">What was authorized, by whom, and under which policy</div></div>',
        unsafe_allow_html=True,
    )
    if not audit_log:
        st.markdown(
            '<div class="sym-empty">No action has been authorized yet. The first confirmed decision will appear here with its evidence, policy, outcome, and accountable human.</div>',
            unsafe_allow_html=True,
        )
        return

    entries: list[str] = []
    for record in audit_log[:6]:
        identity = private_value(record["authorized_by"], private_mode)
        outcome = record["outcome"]
        entries.append(
            f"""
<div class="sym-timeline-entry">
  <div class="sym-timeline-time">{esc(record["display_time"])} · {esc(record["policy"])}</div>
  <div class="sym-timeline-action">{esc(identity)} {esc(record["action"].lower())} · {esc(record["event"])}</div>
  <div class="sym-timeline-copy">
    {esc(outcome["learning"])} Confidence {record["confidence"]}% · {esc(record["risk"])} exposure · {esc(private_value(record["value"], private_mode))}
  </div>
</div>
            """
        )
    st.markdown(f'<div class="sym-timeline">{"".join(entries)}</div>', unsafe_allow_html=True)


def render_analysis(event: dict[str, Any], profile: dict[str, Any], regions: list[dict[str, Any]]) -> None:
    """Render intentionally secondary decision-analysis views."""

    with st.expander("Analyze the decision system", expanded=False):
        st.markdown(
            """
<div class="sym-section-head" style="margin-top:.1rem">
  <div class="sym-section-title">Decision path</div>
  <div class="sym-section-note">One source of truth: event → evidence → challenge → authorization → record</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        stages = [
            ("Event", event["type"]),
            ("Evidence", f"{len(event['evidence'])} inputs"),
            ("Challenge", "Assumptions exposed"),
            ("Authority", profile["current_user"]["role"]),
            ("Record", event["policy"]),
        ]
        path_cards = "".join(
            f'<div class="sym-region" style="flex:1"><div class="sym-region-head">{esc(label)}</div><div class="sym-region-time" style="font-size:.82rem">{esc(value)}</div></div>'
            for label, value in stages
        )
        st.markdown(f'<div class="sym-region-grid" style="grid-template-columns:repeat(5,minmax(0,1fr))">{path_cards}</div>', unsafe_allow_html=True)

        left, right = st.columns(2, gap="medium")
        with left:
            st.markdown(
                f"""
<section class="sym-card"><div class="sym-card-inner">
  <div class="sym-status"><span class="sym-dot amber"></span> Uncertainty model</div>
  <div class="sym-event-name" style="font-size:1.12rem">{event["confidence"]}% confidence</div>
  <div class="sym-event-context">The simulation keeps conflicting and missing evidence visible. Confidence is not permission to hide uncertainty.</div>
</div></section>
                """,
                unsafe_allow_html=True,
            )
        with right:
            busiest = max(regions, key=lambda region: int(region["load"]))
            st.markdown(
                f"""
<section class="sym-card"><div class="sym-card-inner">
  <div class="sym-status"><span class="sym-dot green"></span> Global handoff</div>
  <div class="sym-event-name" style="font-size:1.12rem">{esc(busiest["city"])} · {busiest["load"]}% load</div>
  <div class="sym-event-context">Regional context is live and time-zone aware; operating activity is synthetic and tied to this world’s current scenario.</div>
</div></section>
                """,
                unsafe_allow_html=True,
            )


def render_landing(profile: dict[str, Any]) -> None:
    """Offer a deliberately short entry that previews motion, not a product essay."""

    st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
<section class="sym-entry">
  <div class="sym-entry-mark" aria-hidden="true"><span>S</span><i></i><i></i><i></i></div>
  <div class="sym-kicker">Mynki See</div>
  <h1>Symbiosis</h1>
  <p>The decision cockpit for consequential events.</p>
  <div class="sym-entry-signal"><span class="sym-dot green"></span> {esc(profile["short_name"])} ready · one decision waiting</div>
</section>
        """,
        unsafe_allow_html=True,
    )
    render_live_clock(profile["short_name"])
    if st.button("Enter live decision", type="primary", use_container_width=True):
        st.session_state.sym_started = True
        st.session_state.sym_view = "glance"
        st.rerun()
    st.markdown(
        '<div class="sym-entry-note">Live operating simulation · Scenario data is synthetic</div>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> dict[str, Any]:
    """Keep configuration discoverable without making it the product center."""

    world_labels = {world_id: WORLD_PROFILES[world_id]["name"] for world_id in world_options()}
    with st.sidebar:
        st.markdown('<div class="sym-kicker">Operating world</div>', unsafe_allow_html=True)
        chosen_world = st.radio(
            "Operating world",
            world_options(),
            index=world_options().index(st.session_state.sym_world),
            format_func=lambda world_id: world_labels[world_id],
            label_visibility="collapsed",
        )
        handle_world_change(chosen_world)
        profile = WORLD_PROFILES[st.session_state.sym_world]

        st.markdown("<div class='sym-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sym-kicker'>{esc(profile['domain'])}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='sym-disclosure' style='margin-top:.35rem'>{esc(profile['subtitle'])}</div>",
            unsafe_allow_html=True,
        )
        st.session_state.sym_private_mode = st.toggle(
            "Private view",
            value=st.session_state.sym_private_mode,
            help="Masks fictional names and values for a discreet presentation.",
        )

        st.markdown("<div class='sym-divider'></div>", unsafe_allow_html=True)
        if st.button("Inject next event", use_container_width=True):
            st.session_state.sym_event_index += 1
            st.session_state.sym_pending_action = None
            st.session_state.sym_last_outcome = None
            st.session_state.sym_last_outcome_event = None
            st.session_state.sym_view = "glance"
            st.rerun()
        if st.button("Replay this world", use_container_width=True):
            reset_current_world(clear_audit=True)
            st.rerun()
        if st.session_state.sym_started and st.button("Return to welcome", use_container_width=True):
            st.session_state.sym_started = False
            st.session_state.sym_view = "glance"
            st.rerun()

        st.markdown("<div class='sym-divider'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='sym-disclosure'>Mobile-first · Tablet-ready · Desktop command view<br><br>"
            "No live institutions, accounts, market feeds, wallets, or money movement are connected.</div>",
            unsafe_allow_html=True,
        )

    return WORLD_PROFILES[st.session_state.sym_world]


def render_export(profile: dict[str, Any]) -> None:
    """Provide a portable, plainly labelled decision-record export."""

    snapshot = public_snapshot(
        st.session_state.sym_world,
        st.session_state.sym_event_index,
        st.session_state.sym_audit,
    )
    payload = json.dumps(snapshot, indent=2)
    st.download_button(
        "Download synthetic decision record",
        data=payload,
        file_name="symbiosis_synthetic_decision_record.json",
        mime="application/json",
        use_container_width=True,
        help="Exports only synthetic scenario content and the actions recorded in this session.",
    )


def run() -> None:
    """Run the complete single-round Symbiosis beta experience."""

    initialize_state()
    # Streamlit re-runs the entry script frequently; reloading this lightweight
    # module keeps style changes synchronized with the active beta deployment.
    importlib.reload(symbiosis_theme).inject_theme()
    profile = render_sidebar()

    if not st.session_state.sym_started:
        render_landing(profile)
        return

    event = scenario_for(st.session_state.sym_world, st.session_state.sym_event_index)
    regions = regional_state(profile["id"], utc_now())

    if st.session_state.sym_view == "glance":
        render_glance_header(profile)
        render_decision_pulse(event, profile, regions, st.session_state.sym_private_mode)
        render_glance_controls(event)
        render_glance_futures(event, st.session_state.sym_private_mode)
        return

    detail_action, detail_live = st.columns([1.1, .9], gap="small")
    with detail_action:
        st.markdown('<div class="sym-detail-kicker">Decision detail · read only what changes the authorization</div>', unsafe_allow_html=True)
    with detail_live:
        if st.button("← Back to live view", key=f"{event['id']}-back-to-glance", use_container_width=True):
            st.session_state.sym_view = "glance"
            st.session_state.sym_pending_action = None
            st.rerun()

    render_brand(profile)
    regions = render_global_pulse(profile, st.session_state.sym_private_mode)
    render_event_and_recommendation(event, profile, st.session_state.sym_private_mode)
    render_evidence(event)
    render_futures(event)
    render_action_controls(event, profile)
    render_outcome(event, st.session_state.sym_private_mode)
    render_timeline(st.session_state.sym_audit, st.session_state.sym_private_mode)
    render_analysis(event, profile, regions)

    st.markdown("<div class='sym-divider'></div>", unsafe_allow_html=True)
    export_col, state_col = st.columns([.78, 1.22], gap="medium")
    with export_col:
        render_export(profile)
    with state_col:
        st.markdown(
            f"""
<div class="sym-empty">
  <strong style="color:#eaf2fa">Simulation state</strong><br>
  {esc(profile["name"])} · Event {event["event_number"]} · {event["related_signals"]} related synthetic signals ·
  Policy {esc(event["policy"])} · Live device time remains visible above.
</div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    run()
