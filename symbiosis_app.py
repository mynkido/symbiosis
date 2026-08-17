"""Symbiosis by Mynki AI.

A mobile-first decision cockpit for consequential institutional events.

This beta is deliberately a live operating simulation: local device time,
regional time-zone logic, state transitions, human authorizations, and audit
records are real application behaviour. Institutions, people, assets, events,
and outcomes are synthetic.
"""

from __future__ import annotations

from base64 import b64encode
from datetime import datetime
import html
import importlib
import json
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components

import symbiosis_engine

# Cloud reruns can refresh the entry module while retaining an earlier sibling
# module in memory. The simulation engine is pure and safe to reload; doing so
# keeps the live view and its canonical runtime on the same deployed revision.
importlib.reload(symbiosis_engine)

from symbiosis_engine import (
    SIMULATION_PRESETS,
    active_region_label,
    audit_entry,
    decision_telemetry,
    public_snapshot,
    regional_state,
    scenario_for,
    utc_now,
)
from symbiosis_profiles import WORLD_PROFILES, world_options
import symbiosis_theme


st.set_page_config(
    page_title="Symbiosis · Mynki AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "Symbiosis is a live operating simulation using synthetic scenario data."},
)


def esc(value: Any) -> str:
    """Escape all synthetic content passed into small HTML rendering helpers."""

    return html.escape(str(value), quote=True)


@st.cache_data(show_spinner=False)
def mynki_logo_data_uri() -> str:
    """Embed the supplied Mynki AI mark so it is reliable in deployment."""

    logo_path = Path(__file__).parent / "assets" / "mynki-ai-logo.jpg"
    encoded = b64encode(logo_path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


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
        "sym_sim_preset": "balanced",
        "sym_stream_speed": 1,
        "sym_risk_bias": 0,
        "sym_friction_bias": 0,
        "sym_latency_threshold": 280,
        "sym_show_tuning": False,
        "sym_controls_schema": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    # The tuning widgets were introduced after early beta sessions existed.
    # Normalize that migration once so existing visitors enter on a balanced,
    # intelligible posture rather than inheriting a widget-library minimum.
    if st.session_state.get("sym_controls_schema") != 3:
        st.session_state.sym_sim_preset = "balanced"
        st.session_state.sym_stream_speed = 1
        st.session_state.sym_risk_bias = 0
        st.session_state.sym_friction_bias = 0
        st.session_state.sym_latency_threshold = 280
        st.session_state.sym_controls_schema = 3


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


def apply_simulation_preset() -> None:
    """Apply a named posture as a real set of shared simulation parameters."""

    preset = st.session_state.sym_sim_preset
    if preset == "custom":
        return
    values = SIMULATION_PRESETS.get(preset, SIMULATION_PRESETS["balanced"])
    st.session_state.sym_risk_bias = int(values["risk_bias"])
    st.session_state.sym_friction_bias = int(values["friction_bias"])
    st.session_state.sym_latency_threshold = int(values["latency_threshold"])


def mark_simulation_custom() -> None:
    """Keep audit labels honest when an operator refines a named posture."""

    st.session_state.sym_sim_preset = "custom"


def simulation_controls_from_state() -> dict[str, int | str]:
    """Return the operator choices that are allowed to affect the simulation."""

    return {
        "preset": st.session_state.sym_sim_preset,
        "speed": st.session_state.sym_stream_speed,
        "risk_bias": st.session_state.sym_risk_bias,
        "friction_bias": st.session_state.sym_friction_bias,
        "latency_threshold": st.session_state.sym_latency_threshold,
    }


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

    logo = mynki_logo_data_uri()
    st.markdown(
        f"""
<div class="sym-brand">
  <div class="sym-brand-mark" aria-hidden="true"><img src="{logo}" alt=""></div>
  <div>
    <h1 class="sym-title">Symbiosis</h1>
  </div>
</div>
<div class="sym-disclosure">
  Live decision review · Synthetic scenario · Human authorization required
</div>
        """,
        unsafe_allow_html=True,
    )
    render_live_clock(profile["name"])


def render_glance_header(profile: dict[str, Any]) -> None:
    """Render only the live identity needed before a mobile decision."""

    logo = mynki_logo_data_uri()
    st.markdown(
        f"""
<div class="sym-compact-header">
  <div class="sym-compact-mark" aria-hidden="true"><img src="{logo}" alt=""></div>
  <div>
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


def render_live_simulation_canvas(
    event: dict[str, Any],
    profile: dict[str, Any],
    regions: list[dict[str, Any]],
    telemetry: dict[str, Any],
    private_mode: bool,
) -> None:
    """Render the review-stage decision topology from canonical frame history.

    The browser only interpolates and draws precomputed frames. It does not
    fabricate state: sectors, automation copy, regional posture, route, and
    fallback status all originate in the shared simulation engine.
    """

    sunburst = telemetry["sunburst"]
    root = {**sunburst["root"], "value": private_value(sunburst["root"]["value"], private_mode)}
    payload = {
        "event_id": event["id"],
        "world": profile["short_name"],
        "root": root,
        "branches": sunburst["branches"],
        "frames": sunburst["frames"],
        "halos": sunburst["halos"],
        "focus": sunburst["focus"],
        "media_lookup": sunburst["media_lookup"],
        "routing": telemetry["routing"],
        "controls": telemetry["controls"],
        "challenge": event["challenge"],
        "recommendation": event["recommendation"],
    }
    serialized_payload = json.dumps(payload).replace("</", "<\\/")

    components.html(
        """
<style>
  :root { color-scheme:light; }
  * { box-sizing:border-box; }
  html,body { margin:0; overflow:hidden; background:transparent; font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
  button,a { font:inherit; }
  .topology-shell { position:relative; overflow:hidden; min-height:457px; border:1px solid rgba(38,87,150,.23); border-radius:19px; color:#173854; background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(245,250,253,.96)); box-shadow:0 16px 36px rgba(46,84,122,.13),inset 0 1px 0 rgba(255,255,255,.95); }
  .topology-shell:before { content:""; position:absolute; inset:0; pointer-events:none; opacity:.62; background-image:linear-gradient(rgba(45,99,160,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(45,99,160,.06) 1px,transparent 1px); background-size:22px 22px; }
  .topology-head { position:relative; z-index:3; display:flex; align-items:flex-start; justify-content:space-between; gap:9px; padding:11px 12px 8px; }
  .topology-eyebrow { color:#366689; font-size:7.6px; font-weight:850; letter-spacing:.1em; text-transform:uppercase; }
  .topology-title { margin:2px 0 0; color:#173854; font-size:13px; font-weight:850; letter-spacing:-.02em; }.topology-title span { color:#6690aa; font-weight:690; }
  .route-badge { display:inline-flex; align-items:center; gap:6px; margin-top:1px; padding:5px 7px; border:1px solid rgba(31,105,147,.15); border-radius:999px; background:rgba(255,255,255,.8); color:#247a66; font-size:7.5px; font-weight:850; letter-spacing:.075em; text-transform:uppercase; white-space:nowrap; }.route-badge i { width:6px; height:6px; border-radius:50%; background:#19a878; box-shadow:0 0 0 3px rgba(25,168,120,.12); }.route-badge.fallback { color:#bd4550; }.route-badge.fallback i { background:#d85762; box-shadow:0 0 0 3px rgba(216,87,98,.15); animation:warning-pulse 1.15s ease-in-out infinite; }
  .sunburst-stage { position:relative; z-index:1; height:276px; overflow:hidden; border-top:1px solid rgba(43,94,155,.09); border-bottom:1px solid rgba(43,94,155,.1); background:radial-gradient(circle at 50% 46%,rgba(187,224,247,.25),rgba(248,252,254,.18) 47%,rgba(233,244,252,.45)); }
  .sunburst-stage:before { content:""; position:absolute; inset:-20% -10%; pointer-events:none; opacity:.65; background:radial-gradient(ellipse at 18% 70%,rgba(28,168,120,.12),transparent 37%),radial-gradient(ellipse at 82% 28%,rgba(69,137,238,.16),transparent 38%); animation:ambient-orbit 7s ease-in-out infinite alternate; }
  #decision-sunburst { position:relative; z-index:1; display:block; width:100%; height:100%; outline:none; touch-action:manipulation; cursor:crosshair; }
  #decision-sunburst:focus-visible { box-shadow:inset 0 0 0 2px rgba(47,128,237,.6); }
  .touch-hint { position:absolute; z-index:2; right:9px; bottom:8px; display:inline-flex; align-items:center; gap:4px; color:#52768d; font-size:7.1px; font-weight:830; letter-spacing:.07em; text-transform:uppercase; pointer-events:none; }.touch-hint i { width:6px; height:6px; border-radius:50%; background:#36aee2; box-shadow:0 0 0 3px rgba(54,174,226,.1); animation:hint-breathe 2.1s ease-in-out infinite; }
  .topology-flyout { position:absolute; z-index:3; left:10px; bottom:9px; width:min(220px,calc(100% - 74px)); padding:8px 9px; border:1px solid rgba(47,128,237,.24); border-radius:11px; color:#173954; background:rgba(255,255,255,.91); box-shadow:0 10px 26px rgba(31,77,119,.16); backdrop-filter:blur(11px); opacity:0; transform:translateY(7px) scale(.98); transition:opacity .16s ease,transform .16s ease,border-color .16s ease; pointer-events:none; }.topology-flyout.show { opacity:1; transform:translateY(0) scale(1); }.flyout-overline { display:block; color:#337497; font-size:6.5px; font-weight:850; letter-spacing:.09em; text-transform:uppercase; }.flyout-title { display:block; margin-top:2px; color:#173954; font-size:9px; line-height:1.18; }.flyout-copy { display:block; margin-top:2px; color:#58768d; font-size:7.4px; line-height:1.3; }
  .playback { position:relative; z-index:3; display:grid; grid-template-columns:34px 48px 34px minmax(0,1fr) 42px; align-items:center; gap:5px; padding:7px 10px; border-bottom:1px solid rgba(43,94,155,.1); background:rgba(255,255,255,.61); }.frame-button { min-height:27px; border:1px solid rgba(38,87,150,.16); border-radius:8px; color:#2b6198; background:rgba(255,255,255,.9); font-size:11px; font-weight:850; cursor:pointer; }.frame-button:active { transform:scale(.96); }.frame-button.live { color:#17806a; font-size:7px; letter-spacing:.06em; text-transform:uppercase; }.frame-button:focus-visible { outline:2px solid rgba(47,128,237,.5); outline-offset:1px; }.frame-readout { min-width:0; color:#56758c; font-size:7.6px; font-weight:780; letter-spacing:.045em; text-align:center; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }.frame-readout b { color:#204f7c; }.frame-readout .past { color:#a67532; }
  .automation { position:relative; z-index:2; min-height:71px; padding:9px 11px 10px; background:linear-gradient(90deg,rgba(239,249,253,.9),rgba(255,255,255,.82)); }.automation-top { display:flex; align-items:center; justify-content:space-between; gap:9px; }.automation-stage { display:inline-flex; align-items:center; gap:5px; color:#377294; font-size:7.4px; font-weight:850; letter-spacing:.09em; text-transform:uppercase; }.automation-stage i { width:6px; height:6px; border-radius:50%; background:#36aee2; box-shadow:0 0 0 3px rgba(54,174,226,.1); }.automation-stage.alert { color:#bd4550; }.automation-stage.alert i { background:#d85762; box-shadow:0 0 0 3px rgba(216,87,98,.12); animation:warning-pulse 1.15s ease-in-out infinite; }.automation-state { color:#69869b; font-size:7.2px; font-weight:760; letter-spacing:.06em; text-transform:uppercase; }.automation-copy { display:block; margin-top:4px; color:#244a68; font-size:10px; line-height:1.33; font-weight:690; }
  .sector-inspector { position:relative; z-index:2; margin:0 9px 9px; padding:8px 9px; border:1px solid rgba(43,94,155,.14); border-radius:11px; background:rgba(255,255,255,.92); box-shadow:0 7px 18px rgba(48,86,119,.08); }.inspector-top { display:flex; align-items:center; justify-content:space-between; gap:8px; }.inspector-kind { color:#53768e; font-size:7px; font-weight:850; letter-spacing:.085em; text-transform:uppercase; }.inspector-score { color:#2d6194; font-size:8px; font-weight:820; }.sector-inspector h3 { margin:2px 0 1px; color:#173954; font-size:11px; letter-spacing:-.014em; }.sector-inspector p { margin:0; color:#51728a; font-size:8.4px; line-height:1.35; }.inspector-action { display:block; margin-top:4px; color:#287463; font-size:7.8px; font-weight:760; }.media-status { display:block; margin-top:5px; color:#758ca0; font-size:7.2px; line-height:1.3; }.media-link { display:none; margin-top:5px; color:#2f80ed; font-size:7.4px; font-weight:830; text-decoration:none; }.media-link.show { display:inline-flex; align-items:center; gap:3px; }
  .topology-shell.paused .route-badge i,.topology-shell.paused .touch-hint i,.topology-shell.paused .automation-stage i,.topology-shell.paused .sunburst-stage:before { animation-play-state:paused; }.topology-shell.paused .topology-flyout { border-color:rgba(0,180,222,.5); }
  @keyframes warning-pulse { 0%,100% { opacity:.58; transform:scale(.82); } 48% { opacity:1; transform:scale(1.35); } } @keyframes ambient-orbit { from { transform:translate3d(-2%,1%,0) scale(1); } to { transform:translate3d(2%,-2%,0) scale(1.05); } } @keyframes hint-breathe { 0%,100% { opacity:.52; transform:scale(.82); } 50% { opacity:1; transform:scale(1.24); } }
  @media (max-width:460px) { .topology-shell { min-height:441px; border-radius:16px; }.topology-head { padding:9px 10px 7px; }.topology-title { font-size:12px; }.route-badge { padding:4px 6px; font-size:6.8px; }.sunburst-stage { height:262px; }.topology-flyout { left:8px; bottom:8px; max-width:204px; padding:7px 8px; }.playback { padding:6px 8px; grid-template-columns:31px 44px 31px minmax(0,1fr) 39px; gap:4px; }.frame-button { min-height:26px; }.automation { min-height:66px; padding:8px 10px; }.automation-copy { font-size:9px; }.sector-inspector { margin:0 8px 8px; }.sector-inspector h3 { font-size:10px; } }
  @media (prefers-reduced-motion:reduce) { *,*:before,*:after { animation:none !important; transition:none !important; } }
</style>
<main class="topology-shell" id="topology-shell" aria-label="Interactive decision topology">
  <header class="topology-head"><div><div class="topology-eyebrow">Review mode · decision intelligence</div><div class="topology-title">Decision Topology <span>· tap to inspect</span></div></div><div class="route-badge" id="route-badge"><i></i><span id="route-label"></span></div></header>
  <section class="sunburst-stage" id="sunburst-stage"><canvas id="decision-sunburst" tabindex="0" role="button" aria-label="Animated decision topology. Hover for information or tap anywhere to pause and inspect the current frame."></canvas><div class="touch-hint"><i></i><span id="touch-hint">Hover or tap to freeze</span></div><aside class="topology-flyout" id="topology-flyout" aria-live="polite"><span class="flyout-overline" id="flyout-overline"></span><strong class="flyout-title" id="flyout-title"></strong><span class="flyout-copy" id="flyout-copy"></span></aside></section>
  <nav class="playback" aria-label="Simulation frame playback"><button class="frame-button" id="frame-back" type="button" aria-label="Previous frame">‹</button><button class="frame-button" id="frame-play" type="button" aria-label="Play or pause frame playback">Pause</button><button class="frame-button" id="frame-next" type="button" aria-label="Next frame">›</button><div class="frame-readout" id="frame-readout"></div><button class="frame-button live" id="frame-live" type="button">Live</button></nav>
  <section class="automation" aria-live="polite"><div class="automation-top"><div class="automation-stage" id="automation-stage"><i></i><span id="automation-stage-label"></span></div><span class="automation-state" id="automation-state"></span></div><strong class="automation-copy" id="automation-copy"></strong></section>
  <section class="sector-inspector" id="sector-inspector"><div class="inspector-top"><span class="inspector-kind" id="inspector-kind"></span><span class="inspector-score" id="inspector-score"></span></div><h3 id="inspector-title"></h3><p id="inspector-detail"></p><p id="inspector-meta"></p><small class="inspector-action" id="inspector-action"></small><small class="media-status" id="media-status"></small><a class="media-link" id="media-link" target="_blank" rel="noopener noreferrer"></a></section>
</main>
<script>
  const model = """ + serialized_payload + """;
  const topologyShell = document.getElementById('topology-shell');
  const topologyCanvas = document.getElementById('decision-sunburst');
  const topologyContext = topologyCanvas.getContext('2d');
  const topologyStage = document.getElementById('sunburst-stage');
  const frameBack = document.getElementById('frame-back'); const framePlay = document.getElementById('frame-play'); const frameNext = document.getElementById('frame-next'); const frameLive = document.getElementById('frame-live');
  const frameReadout = document.getElementById('frame-readout'); const routeBadge = document.getElementById('route-badge'); const routeLabel = document.getElementById('route-label'); const touchHint = document.getElementById('touch-hint');
  const autoStage = document.getElementById('automation-stage'); const autoStageLabel = document.getElementById('automation-stage-label'); const autoState = document.getElementById('automation-state'); const autoCopy = document.getElementById('automation-copy');
  const inspectorKind = document.getElementById('inspector-kind'); const inspectorScore = document.getElementById('inspector-score'); const inspectorTitle = document.getElementById('inspector-title'); const inspectorDetail = document.getElementById('inspector-detail'); const inspectorMeta = document.getElementById('inspector-meta'); const inspectorAction = document.getElementById('inspector-action'); const mediaStatus = document.getElementById('media-status'); const mediaLink = document.getElementById('media-link'); const topologyFlyout = document.getElementById('topology-flyout'); const flyoutOverline = document.getElementById('flyout-overline'); const flyoutTitle = document.getElementById('flyout-title'); const flyoutCopy = document.getElementById('flyout-copy');
  const frames = model.frames || []; const branches = model.branches || []; const reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const storageKey = 'symbiosis-topology:' + model.event_id;
  let canvasWidth = 1, canvasHeight = 1, ratio = 1, geometry = [], frameClock = 0, lastDraw = 0, lastClockSecond = -1, animationId = null, playing = !reducedMotion;
  let cursor = Math.max(0, frames.length - 7); let selectedId = null; let hoveredId = null; let displayed = {};
  try { const stored = JSON.parse(sessionStorage.getItem(storageKey) || '{}'); if (Number.isInteger(stored.offsetFromLatest)) cursor = Math.max(0, Math.min(frames.length - 1, frames.length - 1 + stored.offsetFromLatest)); if (typeof stored.selectedId === 'string') selectedId = stored.selectedId; if (stored.paused === true) playing = false; } catch (error) { /* Storage is optional inside embedded views. */ }
  function currentFrame() { return frames[Math.max(0, Math.min(frames.length - 1, cursor))] || { metrics:{trust:0,risk:0,friction:0,operating_load:0,latency_ms:0}, route:'primary', fallback:false, narrative:{stage:'Monitoring',copy:'Simulation is preparing.'}, offset_seconds:0 }; }
  function normaliseAngle(angle) { const full = Math.PI * 2; return ((angle % full) + full) % full; }
  function angleInside(angle, start, end) { const value = normaliseAngle(angle); const begin = normaliseAngle(start); const finish = normaliseAngle(end); return begin <= finish ? value >= begin && value <= finish : value >= begin || value <= finish; }
  function stateColour(item) { if (item.kind === 'evidence') return item.tone === 'verified' ? '#18a878' : item.tone === 'conflicting' ? '#d85762' : '#e0a23a'; if (item.kind === 'region') return item.tone === 'fast' ? '#36aee2' : item.tone === 'ambient' ? '#4389d7' : '#8aa6bd'; if (item.kind === 'option') return item.tone === 'recommended' ? '#356de0' : item.tone === 'risk' ? '#d85762' : '#d49a37'; return item.color || '#2f80ed'; }
  function allItems() { const items = [{id:'hub',kind:'hub',label:'Decision hub',headline:model.root.approval,detail:model.challenge,meta:model.root.value + ' at stake · ' + model.root.route + ' route',action:'The topology recommends and explains. It does not execute action.'}]; branches.forEach(branch => { items.push(branch); branch.children.forEach(child => items.push(child)); }); model.halos.forEach(halo => items.push({id:'metric-' + halo.id,kind:'metric',label:halo.label,headline:halo.label + ' signal',detail:'Current canonical simulation score.',meta:'',action:'This halo follows the current saved simulation frame.',metric:halo.id,color:halo.color})); return items; }
  const itemMap = Object.fromEntries(allItems().map(item => [item.id,item]));
  if (!selectedId || !itemMap[selectedId]) { const missing = branches.flatMap(branch => branch.children).find(item => item.kind === 'evidence' && item.tone === 'missing'); selectedId = missing ? missing.id : branches[0].id; }
  function saveState() { try { sessionStorage.setItem(storageKey, JSON.stringify({offsetFromLatest:cursor - (frames.length - 1),selectedId:selectedId,paused:!playing})); } catch (error) { /* Storage is optional. */ } }
  function sectorPath(cx, cy, inner, outer, start, end) { topologyContext.beginPath(); topologyContext.arc(cx,cy,outer,start,end); topologyContext.arc(cx,cy,inner,end,start,true); topologyContext.closePath(); }
  function drawGrid() { topologyContext.save(); topologyContext.strokeStyle = 'rgba(45,99,160,.075)'; topologyContext.lineWidth = 1; const gap = 21; for (let x=0;x<=canvasWidth;x+=gap) { topologyContext.beginPath(); topologyContext.moveTo(x,0); topologyContext.lineTo(x,canvasHeight); topologyContext.stroke(); } for (let y=0;y<=canvasHeight;y+=gap) { topologyContext.beginPath(); topologyContext.moveTo(0,y); topologyContext.lineTo(canvasWidth,y); topologyContext.stroke(); } topologyContext.restore(); }
  function buildGeometry(cx, cy, sizes) { const entries = []; const branchGap = .024; const startBase = -Math.PI / 2; const branchSpan = (Math.PI * 2) / Math.max(1, branches.length); branches.forEach((branch, branchIndex) => { const start = startBase + branchIndex * branchSpan + branchGap; const end = startBase + (branchIndex + 1) * branchSpan - branchGap; entries.push({id:branch.id,item:branch,start:start,end:end,inner:sizes.branchInner,outer:sizes.branchOuter}); const total = branch.children.reduce((sum,child) => sum + Number(child.weight || 1),0); let childStart = start + .012; branch.children.forEach(child => { const childSpan = (end - start - .024) * Number(child.weight || 1) / total; const childEnd = childStart + childSpan - .009; entries.push({id:child.id,item:child,start:childStart,end:childEnd,inner:sizes.childInner,outer:sizes.childOuter}); childStart += childSpan; }); }); model.halos.forEach((halo, index) => { const span = (Math.PI * 2) / model.halos.length; entries.push({id:'metric-' + halo.id,item:itemMap['metric-' + halo.id],start:startBase + index * span + .025,end:startBase + (index + 1) * span - .025,inner:sizes.haloInner,outer:sizes.haloOuter,halo:true,haloData:halo}); }); return entries; }
  function drawAmbient(cx, cy, radius, now, fallback) { topologyContext.save(); topologyContext.lineWidth = 1; topologyContext.setLineDash([2,6]); topologyContext.strokeStyle = fallback ? 'rgba(216,87,98,.42)' : 'rgba(54,174,226,.34)'; const arcStart = now / 5000; topologyContext.beginPath(); topologyContext.arc(cx,cy,radius + 8,arcStart,arcStart + 1.25); topologyContext.stroke(); topologyContext.setLineDash([]); for (let index=0;index<8;index+=1) { const angle = arcStart * (index % 2 ? -1 : 1) + index * .78; const distance = radius + 11 + (index % 3) * 4; const opacity = .18 + .1 * (Math.sin(now/700 + index)+1); topologyContext.fillStyle = fallback ? 'rgba(216,87,98,' + opacity + ')' : 'rgba(54,174,226,' + opacity + ')'; topologyContext.beginPath(); topologyContext.arc(cx + Math.cos(angle)*distance,cy + Math.sin(angle)*distance,1.5 + (index % 2),0,Math.PI*2); topologyContext.fill(); } topologyContext.restore(); }
  function drawEnergyOrbit(cx, cy, radius, now, fallback) { const colours = fallback ? ['#d85762','#e0a23a','#36aee2'] : ['#00b9e6','#2f80ed','#18a878']; const direction = fallback ? -1 : 1; const phase = now / (fallback ? 620 : 920); topologyContext.save(); topologyContext.lineCap='round'; colours.forEach((colour,index) => { const start=phase*direction + index*2.14; const span=.36 + index*.11; const ring=radius + 9 + index*5; topologyContext.strokeStyle=colour; topologyContext.globalAlpha=.58; topologyContext.shadowColor=colour; topologyContext.shadowBlur=10; topologyContext.lineWidth=2.15 + (index===1 ? .55 : 0); topologyContext.beginPath(); topologyContext.arc(cx,cy,ring,start,start+span); topologyContext.stroke(); const dotAngle=start+span; topologyContext.fillStyle=colour; topologyContext.globalAlpha=.9; topologyContext.beginPath(); topologyContext.arc(cx+Math.cos(dotAngle)*ring,cy+Math.sin(dotAngle)*ring,2.1+(index%2)*.5,0,Math.PI*2); topologyContext.fill(); }); topologyContext.restore(); }
  function drawStreamParticles(cx, cy, radius, now, fallback) { const colours=fallback ? ['#d85762','#e0a23a','#f5b84b'] : ['#36aee2','#2f80ed','#18a878']; topologyContext.save(); for (let index=0;index<15;index+=1) { const speed=(fallback ? -.00195 : .00155)+(index%3)*.00015; const angle=now*speed + index*1.39; const distance=radius+17+(index%4)*5; const size=1.05+(index%3)*.54; const pulse=.42+.28*((Math.sin(now/260+index*1.7)+1)/2); topologyContext.fillStyle=colours[index%colours.length]; topologyContext.globalAlpha=pulse; topologyContext.shadowColor=colours[index%colours.length]; topologyContext.shadowBlur=5; topologyContext.beginPath(); topologyContext.arc(cx+Math.cos(angle)*distance,cy+Math.sin(angle)*distance,size,0,Math.PI*2); topologyContext.fill(); } topologyContext.restore(); }
  function drawSignalSweep(cx, cy, inner, outer, now, fallback) { const angle=now/(fallback ? 660 : 1050); const colour=fallback ? 'rgba(216,87,98,.13)' : 'rgba(54,174,226,.11)'; topologyContext.save(); topologyContext.fillStyle=colour; topologyContext.shadowColor=fallback ? '#d85762' : '#36aee2'; topologyContext.shadowBlur=12; sectorPath(cx,cy,inner,outer,angle-.1,angle+.15); topologyContext.fill(); topologyContext.globalAlpha=.7; topologyContext.strokeStyle=fallback ? '#d85762' : '#36aee2'; topologyContext.lineWidth=1.2; topologyContext.beginPath(); topologyContext.arc(cx,cy,outer,angle-.1,angle+.15); topologyContext.stroke(); topologyContext.restore(); }
  function drawCorePulse(cx, cy, radius, now, fallback) { const pulse=reducedMotion ? .35 : .35+.65*((Math.sin(now/(fallback ? 145 : 285))+1)/2); const colour=fallback ? '#d85762' : '#2f80ed'; topologyContext.save(); topologyContext.strokeStyle=colour; topologyContext.globalAlpha=.13+.13*pulse; topologyContext.lineWidth=1.2; topologyContext.shadowColor=colour; topologyContext.shadowBlur=9+8*pulse; topologyContext.beginPath(); topologyContext.arc(cx,cy,radius+4+pulse*4,0,Math.PI*2); topologyContext.stroke(); topologyContext.restore(); }
  function drawCanvas(now) {
    if (!frames.length) return; topologyContext.clearRect(0,0,canvasWidth,canvasHeight); const frame = currentFrame(); const shortest = Math.min(canvasWidth,canvasHeight); const cx = canvasWidth / 2; const cy = canvasHeight * .49; const sizes = {root:Math.max(34,shortest*.14),branchInner:Math.max(38,shortest*.155),branchOuter:Math.max(65,shortest*.27),childInner:Math.max(69,shortest*.285),childOuter:Math.max(101,shortest*.405),haloInner:Math.max(106,shortest*.43),haloOuter:Math.max(113,shortest*.46)}; geometry = buildGeometry(cx,cy,sizes); drawGrid(); drawAmbient(cx,cy,sizes.haloOuter,now,frame.fallback); if (!reducedMotion) { drawEnergyOrbit(cx,cy,sizes.haloOuter,now,frame.fallback); drawStreamParticles(cx,cy,sizes.haloOuter,now,frame.fallback); }
    geometry.filter(entry => !entry.halo).forEach((entry,index) => { const selected = selectedId === entry.id || hoveredId === entry.id; const colour = stateColour(entry.item); const breath = playing && !reducedMotion ? .035+.085*((Math.sin(now/420+index*1.71)+1)/2) : 0; const radialLift=entry.item.kind === 'branch' ? breath*1.6 : breath*3.3; topologyContext.save(); sectorPath(cx,cy,entry.inner,entry.outer+radialLift,entry.start,entry.end); topologyContext.fillStyle = colour; topologyContext.globalAlpha = (entry.item.kind === 'branch' ? .42 : .84) + breath; topologyContext.shadowColor=colour; topologyContext.shadowBlur=selected ? 17+breath*30 : 2+breath*12; if (selected) topologyContext.globalAlpha=1; topologyContext.fill(); topologyContext.globalAlpha = selected ? .94 : .44+breath*.35; topologyContext.strokeStyle = '#ffffff'; topologyContext.lineWidth = selected ? 2.3 : 1.15; topologyContext.stroke(); topologyContext.restore(); });
    if (!reducedMotion) drawSignalSweep(cx,cy,sizes.branchInner,sizes.childOuter,now,frame.fallback);
    geometry.filter(entry => entry.halo).forEach((entry,index) => { const halo = entry.haloData; const target = Number(frame.metrics[halo.id] || 0); const shown = Number(displayed[halo.id] ?? target); const filled = entry.start + (entry.end-entry.start) * Math.max(.06,Math.min(1,shown/100)); const breath=playing && !reducedMotion ? .5+.5*((Math.sin(now/310+index*1.32)+1)/2) : 0; topologyContext.save(); topologyContext.lineCap='round'; topologyContext.lineWidth=4.7+breath*1.25; topologyContext.strokeStyle='rgba(104,142,176,.15)'; topologyContext.beginPath(); topologyContext.arc(cx,cy,(entry.inner+entry.outer)/2,entry.start,entry.end); topologyContext.stroke(); topologyContext.strokeStyle=halo.color; topologyContext.shadowColor=halo.color; topologyContext.shadowBlur=(selectedId === entry.id || hoveredId === entry.id ? 11 : 4)+breath*8; topologyContext.beginPath(); topologyContext.arc(cx,cy,(entry.inner+entry.outer)/2,entry.start,filled); topologyContext.stroke(); topologyContext.restore(); });
    if (frame.fallback) { const pulse = reducedMotion ? .8 : .5 + (Math.sin(now/220)+1)*.18; topologyContext.save(); topologyContext.strokeStyle='rgba(216,87,98,'+pulse+')'; topologyContext.lineWidth=2; topologyContext.setLineDash([3,5]); topologyContext.beginPath(); topologyContext.arc(cx,cy,sizes.haloOuter+5,0,Math.PI*2); topologyContext.stroke(); topologyContext.restore(); }
    drawCorePulse(cx,cy,sizes.root,now,frame.fallback); topologyContext.save(); const centerGradient = topologyContext.createRadialGradient(cx-8,cy-10,2,cx,cy,sizes.root); centerGradient.addColorStop(0,'#ffffff'); centerGradient.addColorStop(1,'#e8f2fa'); topologyContext.fillStyle=centerGradient; topologyContext.shadowColor='rgba(27,75,119,.18)'; topologyContext.shadowBlur=16; topologyContext.beginPath(); topologyContext.arc(cx,cy,sizes.root,0,Math.PI*2); topologyContext.fill(); topologyContext.shadowBlur=0; topologyContext.strokeStyle=frame.fallback ? '#d85762' : '#2f80ed'; topologyContext.lineWidth=1.4; topologyContext.stroke(); topologyContext.textAlign='center'; topologyContext.fillStyle='#5d7b93'; topologyContext.font='800 6.5px Inter, sans-serif'; topologyContext.fillText('AT STAKE',cx,cy-8); topologyContext.fillStyle='#183d5d'; topologyContext.font='850 16px Inter, sans-serif'; topologyContext.fillText(model.root.value,cx,cy+7); topologyContext.fillStyle='#628096'; topologyContext.font='780 6.4px Inter, sans-serif'; topologyContext.fillText('HUMAN APPROVAL',cx,cy+18); topologyContext.restore();
    branches.forEach((branch,index) => { const angle = -Math.PI/2 + (index+.5)*(Math.PI*2/branches.length); const distance = sizes.haloOuter + 20; const labelX = cx + Math.cos(angle)*distance; const labelY = cy + Math.sin(angle)*distance + 2; topologyContext.save(); topologyContext.fillStyle=branch.color; topologyContext.font='820 7px Inter, sans-serif'; topologyContext.textAlign='center'; topologyContext.fillText(branch.label.toUpperCase(),labelX,labelY); topologyContext.restore(); });
  }
  function resizeCanvas() { const bounds=topologyCanvas.getBoundingClientRect(); ratio=Math.max(1,Math.min(2,window.devicePixelRatio || 1)); canvasWidth=Math.max(1,Math.floor(bounds.width)); canvasHeight=Math.max(1,Math.floor(bounds.height)); topologyCanvas.width=Math.floor(canvasWidth*ratio); topologyCanvas.height=Math.floor(canvasHeight*ratio); topologyContext.setTransform(ratio,0,0,ratio,0,0); drawCanvas(performance.now()); }
  function formatFocusTime() { try { const parts = new Intl.DateTimeFormat('en-GB',{weekday:'short',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23',timeZone:model.focus.zone}).formatToParts(new Date()); const part = type => (parts.find(item => item.type === type) || {}).value || ''; return model.focus.code + ' ' + part('weekday').toUpperCase() + ' ' + part('hour') + ':' + part('minute') + ':' + part('second'); } catch (error) { return model.focus.code + ' live clock'; } }
  function updateInspector() { const frame=currentFrame(); const item=itemMap[hoveredId || selectedId] || itemMap.hub; inspectorKind.textContent=(hoveredId ? 'LIVE · ' : '') + (item.kind || 'signal').toUpperCase(); inspectorTitle.textContent=item.label || 'Decision hub'; inspectorDetail.textContent=item.detail || model.challenge; inspectorMeta.textContent=item.meta || ''; inspectorAction.textContent=item.action || ''; if (item.kind === 'metric') { const score=Math.round(Number(frame.metrics[item.metric] || 0)); inspectorScore.textContent=score + ' / 100'; inspectorMeta.textContent=(item.label || 'Signal') + ' · ' + frame.route.toUpperCase() + ' route · ' + frame.metrics.latency_ms + 'ms'; } else if (item.id === 'hub') { inspectorScore.textContent=frame.route.toUpperCase() + ' · ' + frame.metrics.latency_ms + 'ms'; } else { inspectorScore.textContent=frame.fallback && item.id === 'operations' ? 'FALLBACK' : ''; }
    const showFlyout=Boolean(hoveredId)||!playing; topologyFlyout.classList.toggle('show',showFlyout); flyoutOverline.textContent=hoveredId ? 'LIVE LOOKUP' : 'FROZEN FRAME'; flyoutTitle.textContent=item.label || 'Decision hub'; if (item.kind === 'metric') { flyoutCopy.textContent=Math.round(Number(frame.metrics[item.metric] || 0)) + ' / 100 · ' + frame.route.toUpperCase() + ' · ' + frame.metrics.latency_ms + 'ms'; } else if (item.id === 'hub') { flyoutCopy.textContent=(frame.fallback ? 'Fallback' : 'Primary') + ' route · ' + frame.metrics.latency_ms + 'ms · human approval pending'; } else { flyoutCopy.textContent=item.headline || item.detail || model.challenge; }
    const report=model.media_lookup.external_report; if (report && report.url && report.publisher) { mediaStatus.textContent=report.publisher + ' · ' + (report.language || 'language not supplied') + ' · ' + (report.translation_status || 'original language'); mediaLink.href=report.url; mediaLink.textContent='Open verified report ↗'; mediaLink.classList.add('show'); } else { mediaStatus.textContent=model.media_lookup.status + ' A real publisher link appears only after verified source metadata is attached.'; mediaLink.classList.remove('show'); mediaLink.removeAttribute('href'); }
  }
  function updateUi() { const frame=currentFrame(); const offset=Number(frame.offset_seconds || 0); frameReadout.innerHTML='<b>Frame '+(cursor+1)+' / '+frames.length+'</b> · <span class="'+(offset<0?'past':'')+'">'+(offset<0?'T'+offset+'s':'LIVE')+'</span>'; const fallback=Boolean(frame.fallback); routeBadge.classList.toggle('fallback',fallback); routeLabel.textContent=fallback ? 'Fallback route' : 'Primary route'; autoStage.classList.toggle('alert',fallback); autoStageLabel.textContent=frame.narrative.stage; autoState.textContent=formatFocusTime(); autoCopy.textContent=frame.narrative.copy; topologyShell.classList.toggle('paused',!playing); touchHint.textContent=playing ? 'Hover for detail · tap to freeze' : 'Frozen · tap again to resume'; framePlay.textContent=playing ? 'Pause' : cursor < frames.length-1 ? 'Play' : 'Live'; framePlay.disabled=!playing && cursor >= frames.length-1; frameBack.disabled=cursor<=0; frameNext.disabled=cursor>=frames.length-1; updateInspector(); }
  function setCursor(next, pause) { const wasPlaying=playing; cursor=Math.max(0,Math.min(frames.length-1,next)); if (pause !== undefined) playing=!pause; saveState(); updateUi(); drawCanvas(performance.now()); if (playing && !wasPlaying && !reducedMotion && animationId===null) { lastDraw=performance.now(); animationId=requestAnimationFrame(advance); } }
  function hitTest(clientX,clientY) { const rect=topologyCanvas.getBoundingClientRect(); const x=clientX-rect.left; const y=clientY-rect.top; const shortest=Math.min(canvasWidth,canvasHeight); const cx=canvasWidth/2,cy=canvasHeight*.49; const radius=Math.hypot(x-cx,y-cy); const angle=Math.atan2(y-cy,x-cx); if (radius <= Math.max(34,shortest*.14)) return itemMap.hub; for (let index=geometry.length-1;index>=0;index-=1) { const entry=geometry[index]; if (radius>=entry.inner && radius<=entry.outer && angleInside(angle,entry.start,entry.end)) return entry.item; } return null; }
  function advance(now) { animationId=null; if (!playing || reducedMotion) return; const frame=currentFrame(); const target=frame.metrics; ['trust','risk','friction','operating_load'].forEach(key => { const current=Number(displayed[key] ?? target[key] ?? 0); displayed[key]=current+(Number(target[key] ?? 0)-current)*.11; }); const second=Math.floor(now/1000); if (second !== lastClockSecond) { lastClockSecond=second; autoState.textContent=formatFocusTime(); } if (!lastDraw) lastDraw=now; const elapsed=Math.min(64,now-lastDraw); lastDraw=now; if (cursor < frames.length-1) { frameClock+=elapsed; const dwell=Math.max(520,1250/Math.max(1,Number(model.controls.speed || 1))); if (frameClock>=dwell) { frameClock=0; cursor+=1; saveState(); updateUi(); } } drawCanvas(now); if (playing) animationId=requestAnimationFrame(advance); }
  topologyCanvas.addEventListener('pointerdown', event => { event.preventDefault(); const item=hitTest(event.clientX,event.clientY) || itemMap.hub; const resume=!playing && selectedId===item.id; selectedId=item.id; hoveredId=null; setCursor(cursor,resume ? false : true); });
  topologyCanvas.addEventListener('pointermove', event => { if (event.pointerType === 'touch' || !playing) return; const item=hitTest(event.clientX,event.clientY) || itemMap.hub; const nextId=item.id; if (nextId !== hoveredId) { hoveredId=nextId; updateInspector(); drawCanvas(performance.now()); } });
  topologyCanvas.addEventListener('pointerleave', () => { if (hoveredId !== null) { hoveredId=null; updateInspector(); drawCanvas(performance.now()); } });
  topologyCanvas.addEventListener('keydown', event => { if (event.key==='Enter' || event.key===' ') { event.preventDefault(); setCursor(cursor,playing); } });
  frameBack.addEventListener('click', () => setCursor(cursor-1,true)); frameNext.addEventListener('click', () => setCursor(cursor+1,true)); frameLive.addEventListener('click', () => setCursor(frames.length-1,false)); framePlay.addEventListener('click', () => { if (cursor<frames.length-1) setCursor(cursor,playing); });
  new ResizeObserver(resizeCanvas).observe(topologyStage); displayed={...currentFrame().metrics}; updateUi(); resizeCanvas(); if (!reducedMotion) animationId=requestAnimationFrame(advance); else drawCanvas(performance.now());
</script>
        """,
        height=458,
        scrolling=False,
    )


@st.fragment(run_every="12s")
def render_live_signals(
    event: dict[str, Any],
    profile: dict[str, Any],
    private_mode: bool,
    controls: dict[str, int | str],
) -> None:
    """Refresh the canonical live ticker without restarting the wider app.

    The canvas owns only smooth presentation. Every twelve seconds this small
    fragment asks the shared engine for a new synthetic operating frame using
    the real wall clock. The ticker keeps animation view-only: the chart is
    precomputed by the shared simulation, while hover and tap inspect it.
    """

    live_now = utc_now()
    live_regions = regional_state(profile["id"], live_now)
    live_telemetry = decision_telemetry(event, live_regions, live_now, controls=controls)
    render_live_signal_ticker_canvas(event, profile, live_regions, live_telemetry, private_mode)


@st.fragment(run_every="12s")
def render_review_topology(
    event: dict[str, Any],
    profile: dict[str, Any],
    private_mode: bool,
    controls: dict[str, int | str],
) -> None:
    """Make review feel like a distinct, living decision-investigation scene."""

    live_now = utc_now()
    live_regions = regional_state(profile["id"], live_now)
    live_telemetry = decision_telemetry(event, live_regions, live_now, controls=controls)
    render_live_simulation_canvas(event, profile, live_regions, live_telemetry, private_mode)


def render_live_signal_ticker_canvas(
    event: dict[str, Any],
    profile: dict[str, Any],
    regions: list[dict[str, Any]],
    telemetry: dict[str, Any],
    private_mode: bool,
) -> None:
    """Render the original formal signal ticker as the live mobile surface.

    Canvas movement is deliberately view-only: every plotted sample, threshold,
    and routing state is precomputed by ``decision_telemetry``. The browser
    smoothly moves those canonical synthetic samples rather than creating an
    unrelated random animation.
    """

    focus = max(
        regions,
        key=lambda region: ({"fast": 3, "ambient": 2, "still": 1}[region["motion_mode"]], int(region["load"])),
    )
    routing = telemetry["routing"]
    controls = telemetry["controls"]
    payload = {
        "world": profile["short_name"],
        "event": {
            "value": private_value(event["value"], private_mode),
            "blocker": next((item["source"] for item in event["evidence"] if item["state"] == "missing"), "evidence"),
            "reviews": profile["review_cases"],
        },
        "metrics": telemetry["metrics"],
        "stream": telemetry["ticker_trace"],
        "routing": routing,
        "controls": controls,
        "focus": {key: focus[key] for key in ("code", "city", "zone", "load", "motion_mode", "local_operating_state")},
    }
    serialized_payload = json.dumps(payload).replace("</", "<\\/")

    components.html(
        """
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  html, body { margin:0; overflow:hidden; background:transparent; font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
  button { font:inherit; }
  .signal-ticker-shell {
    --cobalt:#1e4fa3; --electric:#4d86ed; --pale:#8fb4ff; --risk:#d85762; --ink:#15304b;
    position:relative; overflow:hidden; min-height:356px; border:1px solid rgba(34,81,147,.23); border-radius:18px;
    color:var(--ink); background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(247,250,252,.96));
    box-shadow:0 13px 31px rgba(42,83,122,.12),inset 0 1px 0 rgba(255,255,255,.95); user-select:none;
  }
  .signal-ticker-shell:before {
    content:""; position:absolute; inset:0; pointer-events:none; opacity:.52;
    background-image:linear-gradient(rgba(46,100,163,.065) 1px,transparent 1px),linear-gradient(90deg,rgba(46,100,163,.065) 1px,transparent 1px);
    background-size:22px 22px; mask-image:linear-gradient(to bottom,rgba(0,0,0,.8),rgba(0,0,0,.26));
  }
  .signal-head { position:relative; z-index:3; display:flex; align-items:flex-start; justify-content:space-between; gap:9px; padding:12px 12px 9px; }
  .signal-kicker { color:#183552; font-size:13px; font-weight:850; letter-spacing:-.015em; }
  .signal-sub { margin:3px 0 0; color:#60798d; font-size:9.5px; line-height:1.28; font-weight:640; }
  .signal-head-action { flex:0 0 auto; display:inline-flex; align-items:center; gap:6px; padding:5px 7px; border:1px solid rgba(35,83,154,.15); border-radius:999px; color:#285d9c; background:rgba(255,255,255,.78); font-size:8px; font-weight:830; letter-spacing:.075em; text-transform:uppercase; }
  .signal-orbit { position:relative; display:block; width:10px; height:10px; border:1px solid rgba(47,128,237,.68); border-radius:50%; }
  .signal-orbit:before,.signal-orbit:after { content:""; position:absolute; border-radius:inherit; }
  .signal-orbit:before { inset:-4px; border:1px dashed rgba(0,180,222,.5); animation:mini-orbit 4s linear infinite; }
  .signal-orbit:after { width:3px; height:3px; right:-3px; top:0; background:#00b4df; box-shadow:0 0 0 3px rgba(0,180,222,.12); animation:mini-pulse 1.8s ease-in-out infinite; }
  .signal-tape { position:relative; z-index:3; height:28px; overflow:hidden; border-top:1px solid rgba(34,81,147,.1); border-bottom:1px solid rgba(34,81,147,.11); background:linear-gradient(90deg,rgba(202,226,250,.42),rgba(255,255,255,.55),rgba(222,233,248,.45)); }
  .signal-tape:before,.signal-tape:after { content:""; position:absolute; z-index:2; top:0; bottom:0; width:19px; pointer-events:none; }
  .signal-tape:before { left:0; background:linear-gradient(90deg,rgba(248,251,253,.98),transparent); }.signal-tape:after { right:0; background:linear-gradient(-90deg,rgba(248,251,253,.98),transparent); }
  .signal-tape-track { display:flex; align-items:center; width:max-content; min-width:200%; height:100%; animation:signal-tape-slide var(--tape-duration,26s) linear infinite; }
  .signal-tape-track span { padding-right:38px; color:#376688; font-size:8.2px; font-weight:830; letter-spacing:.083em; white-space:nowrap; text-transform:uppercase; }
  .chart-shell { position:relative; z-index:1; height:231px; overflow:hidden; background:linear-gradient(180deg,rgba(248,252,255,.5),rgba(239,247,253,.76)); }
  .chart-shell:before { content:""; position:absolute; inset:-35% -10%; pointer-events:none; background:radial-gradient(ellipse at 70% 35%,rgba(112,181,255,.11),transparent 42%),radial-gradient(ellipse at 18% 82%,rgba(0,192,229,.07),transparent 40%); animation:ambient-wash 13s ease-in-out infinite alternate; }
  .chart-shell:after { content:""; position:absolute; left:0; right:0; bottom:0; height:52%; pointer-events:none; opacity:.32; background:linear-gradient(105deg,transparent 0 21%,rgba(90,171,234,.15) 28%,transparent 36% 61%,rgba(97,169,235,.12) 70%,transparent 77%); background-size:180% 100%; animation:ambient-data-stream 15s linear infinite; }
  #signal-ticker-canvas { position:relative; z-index:1; display:block; width:100%; height:100%; outline:none; touch-action:manipulation; cursor:crosshair; }
  #signal-ticker-canvas:focus-visible { box-shadow:inset 0 0 0 2px rgba(47,128,237,.55); }
  .chart-legend { position:absolute; z-index:3; left:30px; bottom:8px; display:flex; align-items:center; gap:6px; pointer-events:none; }
  .chart-legend span { display:inline-flex; align-items:center; gap:3px; color:#547187; font-size:7px; font-weight:820; letter-spacing:.055em; text-transform:uppercase; }
  .chart-legend i { width:10px; height:2px; border-radius:2px; background:currentColor; }.chart-legend .risk { color:#d85762; }.chart-legend .friction { color:#1e4fa3; }.chart-legend .trust { color:#8fb4ff; }.chart-legend .load { color:#55aee0; }
  .chart-readout { position:absolute; z-index:5; min-width:138px; padding:7px 8px; border:1px solid rgba(31,81,148,.2); border-radius:10px; color:#365c79; background:rgba(255,255,255,.95); box-shadow:0 9px 19px rgba(35,74,111,.17); opacity:0; pointer-events:none; transform:translate(-50%,-4px); transition:opacity .14s ease,transform .14s ease; }
  .chart-readout.show { opacity:1; transform:translate(-50%,0); }.chart-readout strong { display:block; color:#173a5a; font-size:8px; letter-spacing:.08em; }.chart-readout p { margin:3px 0 0; font-size:8px; font-weight:690; line-height:1.34; }.chart-readout em { color:#c94450; font-style:normal; font-weight:850; }
  .chart-live-label { position:absolute; z-index:4; right:10px; bottom:8px; display:inline-flex; align-items:center; gap:5px; color:#49728f; font-size:7.5px; font-weight:840; letter-spacing:.075em; text-transform:uppercase; pointer-events:none; }.chart-live-label i { width:6px; height:6px; border-radius:50%; background:#12a575; box-shadow:0 0 0 3px rgba(18,165,117,.11); animation:status-blink 2s ease-in-out infinite; }.chart-live-label.fallback { color:#bc3744; }.chart-live-label.fallback i { background:#d85762; box-shadow:0 0 0 3px rgba(216,87,98,.13); }
  .signal-footer { position:relative; z-index:3; display:flex; align-items:center; justify-content:space-between; gap:8px; min-height:38px; padding:8px 12px; border-top:1px solid rgba(34,81,147,.11); color:#59748a; font-size:8.5px; font-weight:700; }.signal-footer b { color:#204a78; font-weight:850; }.route-state { display:inline-flex; align-items:center; gap:5px; white-space:nowrap; color:#1d7f68; font-size:8px; font-weight:850; letter-spacing:.075em; text-transform:uppercase; }.route-state i { width:6px; height:6px; border-radius:50%; background:#12a575; box-shadow:0 0 0 3px rgba(18,165,117,.11); }.route-state.fallback { color:#bc3744; }.route-state.fallback i { background:#d85762; box-shadow:0 0 0 3px rgba(216,87,98,.13); animation:status-blink 1.1s ease-in-out infinite; }
  .signal-ticker-shell.paused .signal-tape-track,.signal-ticker-shell.paused .signal-orbit:before,.signal-ticker-shell.paused .signal-orbit:after,.signal-ticker-shell.paused .chart-shell:before,.signal-ticker-shell.paused .chart-shell:after,.signal-ticker-shell.paused .chart-live-label i { animation-play-state:paused; }
  @keyframes signal-tape-slide { to { transform:translateX(-50%); } } @keyframes mini-orbit { to { transform:rotate(360deg); } } @keyframes mini-pulse { 0%,100% { transform:scale(.72); opacity:.55; } 48% { transform:scale(1.35); opacity:1; } } @keyframes ambient-wash { from { transform:translate3d(-2%,0,0) scale(1); } to { transform:translate3d(3%,-2%,0) scale(1.06); } } @keyframes ambient-data-stream { from { background-position:100% 0; } to { background-position:-80% 0; } } @keyframes status-blink { 0%,100% { opacity:.55; transform:scale(.85); } 50% { opacity:1; transform:scale(1.2); } }
  @media (max-width:460px) { .signal-ticker-shell { min-height:344px; border-radius:16px; }.signal-head { padding:10px 10px 8px; }.signal-kicker { font-size:12px; }.signal-sub { max-width:250px; font-size:8.8px; }.signal-head-action { padding:5px 6px; font-size:7px; }.chart-shell { height:221px; }.signal-footer { padding:7px 10px; font-size:7.7px; }.signal-footer b { max-width:190px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }.chart-legend { gap:4px; left:27px; }.chart-legend span { font-size:6.3px; } }
  @media (prefers-reduced-motion:reduce) { *,*:before,*:after { animation:none !important; transition:none !important; } }
</style>
<main class="signal-ticker-shell" id="signal-ticker-shell" aria-label="Live Signals ticker view">
  <div class="signal-head">
    <div><div class="signal-kicker">Live Signals (Ticker View)</div><p class="signal-sub">Trust / Risk / Friction drift in real time. Latency spikes trigger fallback routing.</p></div>
    <div class="signal-head-action"><span class="signal-orbit" aria-hidden="true"></span><span id="tap-state">Hover / tap to freeze</span></div>
  </div>
  <div class="signal-tape"><div class="signal-tape-track"><span id="signal-tape-a"></span><span id="signal-tape-b" aria-hidden="true"></span></div></div>
  <section class="chart-shell" id="chart-shell"><canvas id="signal-ticker-canvas" tabindex="0" role="button" aria-label="Animated synthetic Trust Risk Friction signal ticker. Hover for a snapshot or tap to freeze and inspect."></canvas><div class="chart-legend"><span class="risk"><i></i>Risk</span><span class="friction"><i></i>Friction</span><span class="trust"><i></i>Trust</span><span class="load"><i></i>Load</span></div><div class="chart-readout" id="chart-readout"><strong id="readout-title"></strong><p id="readout-copy"></p></div><div class="chart-live-label" id="chart-live-label"><i></i><span>Primary route</span></div></section>
  <div class="signal-footer"><div><b id="signal-location"></b><span id="signal-footer-copy"></span></div><div class="route-state" id="route-state"><i></i><span id="route-copy"></span></div></div>
</main>
<script>
  const model = """ + serialized_payload + """;
  const shell = document.getElementById('signal-ticker-shell');
  const canvas = document.getElementById('signal-ticker-canvas');
  const ctx = canvas.getContext('2d');
  const readout = document.getElementById('chart-readout');
  const readoutTitle = document.getElementById('readout-title');
  const readoutCopy = document.getElementById('readout-copy');
  const tapState = document.getElementById('tap-state');
  const routeState = document.getElementById('route-state');
  const routeCopy = document.getElementById('route-copy');
  const liveLabel = document.getElementById('chart-live-label');
  const stream = model.stream || [];
  const reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let width = 1, height = 1, dpr = 1, offset = 0, lastFrame = 0, frameId = null, paused = false, hovered = false;
  let selected = null, selectedX = null;
  const speed = Number(model.controls.speed || 1);
  const sampleMs = 430;

  function modulo(value, length) { return ((value % length) + length) % length; }
  function sampleAt(index) { return stream[modulo(index, stream.length)]; }
  function plot() { return { left: 30, right: Math.max(48, width - 13), top: 18, bottom: Math.max(39, height - 27) }; }
  function yFor(value, bounds) { return bounds.bottom - (Number(value) / 100) * (bounds.bottom - bounds.top); }
  function blend(a, b, progress, key) { return Number(a[key]) + (Number(b[key]) - Number(a[key])) * progress; }
  function indices() {
    const bounds = plot(); const visible = Math.max(32, Math.min(82, Math.round((bounds.right - bounds.left) / 7)));
    const whole = Math.floor(offset); const fraction = offset - whole; const base = stream.length - visible + whole;
    return { bounds, visible, fraction, base, step: (bounds.right - bounds.left) / Math.max(1, visible - 1) };
  }
  function setCanvasSize() {
    const box = canvas.getBoundingClientRect(); dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    width = Math.max(1, Math.floor(box.width)); height = Math.max(1, Math.floor(box.height));
    canvas.width = Math.floor(width * dpr); canvas.height = Math.floor(height * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); draw();
  }
  function drawGrid(bounds) {
    ctx.save(); ctx.lineWidth = 1; ctx.strokeStyle = 'rgba(49,94,151,.10)';
    for (let y = bounds.top; y <= bounds.bottom; y += (bounds.bottom - bounds.top) / 4) { ctx.beginPath(); ctx.moveTo(bounds.left, y); ctx.lineTo(bounds.right, y); ctx.stroke(); }
    const xGap = Math.max(21, Math.round((bounds.right - bounds.left) / 12)); for (let x = bounds.left; x <= bounds.right; x += xGap) { ctx.beginPath(); ctx.moveTo(x, bounds.top); ctx.lineTo(x, bounds.bottom); ctx.stroke(); }
    ctx.fillStyle = 'rgba(61,93,122,.68)'; ctx.font = '700 7px Inter, sans-serif'; ctx.fillText('100', 4, bounds.top + 3); ctx.fillText('50', 8, (bounds.top + bounds.bottom) / 2 + 3); ctx.fillText('0', 13, bounds.bottom + 3); ctx.fillText('earlier', bounds.left, height - 8); ctx.fillText('now', bounds.right - 16, height - 8); ctx.restore();
  }
  function renderArea(points, bounds) {
    if (!points.length) return; const gradient = ctx.createLinearGradient(0, bounds.top, 0, bounds.bottom); gradient.addColorStop(0, 'rgba(101,181,231,.40)'); gradient.addColorStop(1, 'rgba(101,181,231,.035)');
    ctx.save(); ctx.beginPath(); points.forEach((point, index) => { const y = yFor(point.sample.load, bounds); index ? ctx.lineTo(point.x, y) : ctx.moveTo(point.x, y); }); ctx.lineTo(points[points.length - 1].x, bounds.bottom); ctx.lineTo(points[0].x, bounds.bottom); ctx.closePath(); ctx.fillStyle = gradient; ctx.fill(); ctx.restore();
  }
  function renderLine(points, bounds, key, colour, weight) {
    ctx.save(); ctx.lineWidth = weight; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.strokeStyle = colour; ctx.shadowColor = colour; ctx.shadowBlur = key === 'risk' ? 3.2 : 1.8; ctx.beginPath(); points.forEach((point, index) => { const y = yFor(point.sample[key], bounds); index ? ctx.lineTo(point.x, y) : ctx.moveTo(point.x, y); }); ctx.stroke(); ctx.restore();
  }
  function drawFallbackMarkers(points, bounds, now) {
    const breaches = points.filter(point => point.sample.fallback); if (!breaches.length) return;
    const priority = breaches[breaches.length - 1]; ctx.save(); ctx.lineWidth = 1; breaches.forEach(point => { ctx.strokeStyle = point === priority ? 'rgba(216,87,98,.72)' : 'rgba(216,87,98,.26)'; ctx.beginPath(); ctx.moveTo(point.x, bounds.top); ctx.lineTo(point.x, bounds.bottom); ctx.stroke(); });
    const pulse = paused || reducedMotion ? .78 : .55 + (Math.sin(now / 260) + 1) * .18; ctx.fillStyle = 'rgba(216,87,98,' + pulse + ')'; const labelX = Math.max(bounds.left + 2, Math.min(priority.x - 22, bounds.right - 46)); ctx.fillRect(labelX, bounds.top + 4, 44, 12); ctx.fillStyle = '#fff'; ctx.font = '800 6.4px Inter, sans-serif'; ctx.fillText('FALLBACK', labelX + 4, bounds.top + 12); ctx.restore();
  }
  function drawLeadDots(state, bounds) {
    const current = sampleAt(state.base + state.visible - 1); const next = sampleAt(state.base + state.visible); const progress = state.fraction;
    [['risk','#d85762',3.8],['friction','#1e4fa3',3.6],['trust','#8fb4ff',3.4]].forEach(item => { const key = item[0], colour = item[1], radius = item[2]; const value = blend(current, next, progress, key); const y = yFor(value, bounds); ctx.save(); ctx.fillStyle = colour; ctx.shadowColor = colour; ctx.shadowBlur = 8; ctx.beginPath(); ctx.arc(bounds.right, y, radius, 0, Math.PI * 2); ctx.fill(); ctx.restore(); });
  }
  function drawCrosshair(bounds) {
    if (!selected || selectedX === null) return; ctx.save(); ctx.strokeStyle = 'rgba(27,73,128,.44)'; ctx.setLineDash([3,3]); ctx.beginPath(); ctx.moveTo(selectedX, bounds.top); ctx.lineTo(selectedX, bounds.bottom); ctx.stroke(); ctx.restore();
  }
  function draw(now) {
    if (!stream.length) return; ctx.clearRect(0, 0, width, height); const state = indices(); const points = [];
    for (let index = 0; index <= state.visible; index += 1) { points.push({ index: state.base + index, x: state.bounds.left + index * state.step - state.fraction * state.step, sample: sampleAt(state.base + index) }); }
    ctx.save(); ctx.beginPath(); ctx.rect(state.bounds.left, state.bounds.top, state.bounds.right - state.bounds.left, state.bounds.bottom - state.bounds.top); ctx.clip(); drawGrid(state.bounds); renderArea(points, state.bounds); renderLine(points, state.bounds, 'risk', '#d85762', 2.15); renderLine(points, state.bounds, 'friction', '#1e4fa3', 2.05); renderLine(points, state.bounds, 'trust', '#8fb4ff', 1.75); drawFallbackMarkers(points, state.bounds, now); drawLeadDots(state, state.bounds); drawCrosshair(state.bounds); ctx.restore();
  }
  function locationText() {
    const options = new Intl.DateTimeFormat('en-GB', { weekday:'short', hour:'2-digit', minute:'2-digit', second:'2-digit', hourCycle:'h23', timeZone:model.focus.zone }).formatToParts(new Date()); const part = type => (options.find(item => item.type === type) || {}).value || '';
    return model.focus.code + ' · ' + part('weekday').toUpperCase() + ' ' + part('hour') + ':' + part('minute') + ':' + part('second');
  }
  function updateText() {
    const route = model.routing.fallback_active ? 'FALLBACK ROUTE' : 'PRIMARY ROUTE'; const tape = model.world + ' · TRUST ' + model.metrics.trust + ' · RISK ' + model.metrics.risk + ' · FRICTION ' + model.metrics.friction + ' · LATENCY ' + model.metrics.latency_ms + 'MS · ' + route + ' · ' + model.focus.code + ' ' + model.focus.local_operating_state.replace('_',' ').toUpperCase() + ' · ' + model.event.value + ' AT STAKE · ' + model.event.blocker.toUpperCase() + ' CHECK · ' + model.event.reviews + ' HUMAN REVIEWS';
    document.getElementById('signal-tape-a').textContent = tape; document.getElementById('signal-tape-b').textContent = tape; document.getElementById('signal-location').textContent = locationText(); document.getElementById('signal-footer-copy').textContent = ' · synthetic stream · ' + model.controls.label + ' posture'; routeCopy.textContent = route; routeState.classList.toggle('fallback', model.routing.fallback_active); liveLabel.classList.toggle('fallback', model.routing.fallback_active); liveLabel.querySelector('span').textContent = model.routing.fallback_active ? 'Fallback active' : 'Primary route';
  }
  function updateReadout(sample, x, frozen) {
    if (!sample) return; selected = sample; selectedX = x; const fallback = sample.fallback ? ' · <em>FALLBACK</em>' : ' · LIVE'; readoutTitle.innerHTML = (frozen ? 'PAUSED · ' : '') + 'SIGNAL SNAPSHOT'; readoutCopy.innerHTML = 'Trust ' + Math.round(sample.trust) + ' · Risk ' + Math.round(sample.risk) + ' · Friction ' + Math.round(sample.friction) + '<br>Latency ' + Math.round(sample.latency_ms) + 'ms' + fallback; readout.style.left = Math.max(77, Math.min(width - 77, x)) + 'px'; readout.style.top = '18px'; readout.classList.add('show');
  }
  function pointFromEvent(event) { const rect = canvas.getBoundingClientRect(); const state = indices(); const x = Math.max(state.bounds.left, Math.min(state.bounds.right, event.clientX - rect.left)); const visibleIndex = Math.max(0, Math.min(state.visible, Math.round((x - state.bounds.left + state.fraction * state.step) / state.step))); return { sample: sampleAt(state.base + visibleIndex), x: state.bounds.left + visibleIndex * state.step - state.fraction * state.step }; }
  function stopFrame() { if (frameId !== null) { cancelAnimationFrame(frameId); frameId = null; } }
  function frame(now) { if (!lastFrame) lastFrame = now; const elapsed = Math.min(64, now - lastFrame); lastFrame = now; if (!paused && !reducedMotion) offset += elapsed / sampleMs * speed; draw(now); updateText(); if (!paused && !reducedMotion) frameId = requestAnimationFrame(frame); }
  function setPaused(next, selection) { paused = next; shell.classList.toggle('paused', paused); tapState.textContent = paused ? 'Tap to resume' : 'Hover / tap to freeze'; if (selection) updateReadout(selection.sample, selection.x, paused); if (paused) { stopFrame(); draw(performance.now()); } else { selected = null; selectedX = null; readout.classList.remove('show'); lastFrame = performance.now(); if (!reducedMotion) frameId = requestAnimationFrame(frame); } }
  canvas.addEventListener('pointerdown', event => { event.preventDefault(); if (paused) { setPaused(false); return; } setPaused(true, pointFromEvent(event)); });
  canvas.addEventListener('pointermove', event => { if (event.pointerType === 'touch' || paused) return; hovered = true; const point = pointFromEvent(event); updateReadout(point.sample, point.x, false); draw(performance.now()); });
  canvas.addEventListener('pointerleave', () => { if (!paused) { hovered = false; selected = null; selectedX = null; readout.classList.remove('show'); draw(performance.now()); } });
  canvas.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); if (paused) setPaused(false); else { const state = indices(); setPaused(true, { sample: sampleAt(state.base + state.visible - 1), x: state.bounds.right }); } } });
  new ResizeObserver(setCanvasSize).observe(document.getElementById('chart-shell'));
  document.getElementById('signal-ticker-shell').style.setProperty('--tape-duration', Math.max(8, 29 / speed) + 's');
  updateText(); setCanvasSize(); if (!reducedMotion) { lastFrame = performance.now(); frameId = requestAnimationFrame(frame); } else { const state = indices(); updateReadout(sampleAt(state.base + state.visible - 1), state.bounds.right, false); }
  window.setInterval(() => { if (!paused) updateText(); }, 1000);
</script>
        """,
        height=357,
        scrolling=False,
    )


def _render_retired_orbit_live_simulation_canvas(
    event: dict[str, Any],
    profile: dict[str, Any],
    regions: list[dict[str, Any]],
    telemetry: dict[str, Any],
    private_mode: bool,
) -> None:
    """Render the three live visual systems with mobile tap-to-inspect controls.

    The visual is intentionally self-contained so a tap can pause its CSS motion
    and explain the selected regional session without changing the canonical
    Streamlit decision state.
    """

    blocker = next((item for item in event["evidence"] if item["state"] == "missing"), event["evidence"][-1])
    focus = max(
        regions,
        key=lambda region: ({"fast": 3, "ambient": 2, "still": 1}[region["motion_mode"]], int(region["load"])),
    )
    tone = "critical" if event["risk"].lower() == "critical" else "attention" if event["risk"].lower() in {"elevated", "moderate"} else "steady"
    payload = {
        "world": profile["short_name"],
        "continuous_network": profile["id"] == "axiom",
        "tone": tone,
        "event": {
            "value": private_value(event["value"], private_mode),
            "confidence": event["confidence"],
            "risk": event["risk"],
            "blocker": blocker["source"],
            "action": event["recommendation"],
            "reviews": profile["review_cases"],
        },
        "metrics": telemetry["metrics"],
        "trace": telemetry["trace"],
        "focus": focus["code"],
        "regions": [
            {
                key: region[key]
                for key in (
                    "code",
                    "city",
                    "zone",
                    "x",
                    "y",
                    "load",
                    "motion_mode",
                    "local_operating_state",
                    "network_active",
                )
            }
            for region in regions
        ],
    }
    serialized_payload = json.dumps(payload).replace("</", "<\\/")

    components.html(
        """
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  html, body { margin: 0; overflow: hidden; background: transparent; font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  button { font: inherit; }
  .live-sim {
    position: relative;
    overflow: hidden;
    min-height: 304px;
    border: 1px solid rgba(47,128,237,.2);
    border-radius: 21px;
    color: #153854;
    background: linear-gradient(145deg, rgba(255,255,255,.99), rgba(244,251,255,.95));
    box-shadow: 0 18px 40px rgba(53,96,132,.13), inset 0 1px 0 rgba(255,255,255,.94);
    cursor: pointer;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
  .sim-top { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:10px 12px 7px; }
  .sim-status { display:inline-flex; align-items:center; gap:6px; color:#4d6d86; font-size:9px; font-weight:820; letter-spacing:.1em; text-transform:uppercase; }
  .sim-status i { width:7px; height:7px; border-radius:50%; background:#f2994a; box-shadow:0 0 0 4px rgba(242,153,74,.12); }
  .steady .sim-status i { background:#00b894; box-shadow:0 0 0 4px rgba(0,184,148,.11); }
  .critical .sim-status i { background:#eb5757; box-shadow:0 0 0 4px rgba(235,87,87,.12); }
  .tap-label { color:#2f80ed; font-size:9px; font-weight:820; letter-spacing:.08em; text-transform:uppercase; white-space:nowrap; }
  .ticker { height:27px; overflow:hidden; border-top:1px solid rgba(47,128,237,.1); border-bottom:1px solid rgba(47,128,237,.1); background:linear-gradient(90deg, rgba(0,210,255,.11), rgba(255,255,255,.62), rgba(47,128,237,.08)); }
  .ticker-track { display:flex; align-items:center; width:max-content; min-width:200%; height:100%; animation: ticker-slide 29s linear infinite; }
  .ticker-track span { padding-right:38px; color:#356f99; font-size:8.5px; font-weight:820; letter-spacing:.085em; white-space:nowrap; }
  .sim-stage { position:relative; height:205px; overflow:hidden; isolation:isolate; }
  .sim-stage:before { content:""; position:absolute; width:250px; height:250px; left:50%; top:50%; z-index:0; border-radius:50%; transform:translate(-50%,-50%); background:radial-gradient(circle, rgba(0,210,255,.15), rgba(47,128,237,.075) 43%, transparent 70%); }
  .grid { position:absolute; inset:0; z-index:0; opacity:.55; background-image:linear-gradient(rgba(47,128,237,.09) 1px, transparent 1px),linear-gradient(90deg,rgba(47,128,237,.09) 1px,transparent 1px); background-size:24px 24px; mask-image:linear-gradient(to bottom, transparent, #000 18%, #000 84%, transparent); }
  .stream-map { position:absolute; inset:0; z-index:1; width:100%; height:100%; }
  .ambient { fill:none; stroke:rgba(0,210,255,.28); stroke-linecap:round; stroke-dasharray:13 19; animation: ambient-drift 14s cubic-bezier(.42,0,.58,1) infinite; }
  .ambient.a { stroke-width:1.2; }
  .ambient.b { stroke:rgba(47,128,237,.2); stroke-width:1.55; animation-duration:20s; animation-direction:reverse; }
  .ambient.c { stroke:rgba(18,184,134,.18); stroke-width:.95; animation-duration:17s; animation-delay:-4s; }
  .route-base { fill:none; stroke:rgba(47,128,237,.2); stroke-width:1.25; }
  .route-live { fill:none; stroke:url(#streamGradient); stroke-width:2.35; stroke-linecap:round; stroke-dasharray:9 10; animation: route-flow 5.8s linear infinite; filter:drop-shadow(0 1px 2px rgba(0,210,255,.24)); }
  .signal-area { fill:url(#loadGradient); opacity:.36; }
  .signal-line { fill:none; stroke-width:2.1; stroke-linecap:round; stroke-linejoin:round; animation: signal-breathe 2.7s ease-in-out infinite; }
  .signal-line.trust { stroke:#12a575; }
  .signal-line.risk { stroke:#d75d68; animation-delay:-.9s; }
  .signal-line.friction { stroke:#2f80ed; animation-delay:-1.6s; }
  .signal-dot { animation: signal-dot-pulse 2.25s ease-in-out infinite; }
  .signal-dot.trust { fill:#12a575; } .signal-dot.risk { fill:#d75d68; animation-delay:-.7s; } .signal-dot.friction { fill:#2f80ed; animation-delay:-1.3s; }
  .chart-axis { fill:#7b93a5; font-size:8px; font-weight:760; letter-spacing:.04em; }
  .signal-legend { position:absolute; z-index:6; top:9px; left:10px; display:flex; gap:4px; }
  .signal-legend span { display:inline-flex; align-items:center; gap:3px; padding:4px 5px; border:1px solid rgba(47,128,237,.13); border-radius:7px; background:rgba(255,255,255,.78); color:#4d6d86; box-shadow:0 4px 12px rgba(51,91,128,.06); font-size:7px; font-weight:830; letter-spacing:.055em; }
  .signal-legend b { color:#153854; font-size:8px; } .signal-legend .trust b { color:#118466; } .signal-legend .risk b { color:#c74f5c; } .signal-legend .friction b { color:#276fd2; }
  .orbit { position:absolute; z-index:2; left:50%; top:50%; border:1px dashed rgba(0,210,255,.35); border-radius:50%; transform:translate(-50%,-50%); }
  .orbit.one { width:167px; height:167px; animation: orbit-cw 11s linear infinite; }
  .orbit.two { width:205px; height:205px; border-color:rgba(47,128,237,.21); animation: orbit-ccw 17s linear infinite; }
  .orbit i { position:absolute; width:6px; height:6px; border-radius:50%; background:#00d2ff; box-shadow:0 0 0 4px rgba(0,210,255,.1),0 0 12px rgba(0,210,255,.52); animation: particle-burst 2.8s ease-in-out infinite; }
  .orbit i:nth-child(1) { top:-4px; left:48%; }
  .orbit i:nth-child(2) { right:5%; bottom:13%; width:4px; height:4px; animation-delay:-.85s; }
  .orbit i:nth-child(3) { left:7%; top:62%; width:3px; height:3px; animation-delay:-1.7s; }
  .orbit.two i { background:#2f80ed; box-shadow:0 0 0 3px rgba(47,128,237,.1),0 0 9px rgba(47,128,237,.3); }
  .orbit.two i:nth-child(1) { top:18%; left:5%; }
  .orbit.two i:nth-child(2) { right:13%; bottom:5%; animation-delay:-1.25s; }
  .fast .orbit.one, .network-fast .orbit.one { animation-duration:7s; } .fast .orbit.two, .network-fast .orbit.two { animation-duration:11s; }
  .network-fast .ambient { animation-duration:8s; }
  .network-fast .route-live { animation-duration:3.9s; }
  .network-fast .signal-line { animation-duration:1.65s; } .network-fast .signal-dot { animation-duration:1.3s; }
  .still .ambient { animation-duration:36s; opacity:.3; } .still .route-live { animation-duration:18s; opacity:.38; } .still .orbit { opacity:.44; animation-duration:24s; } .still .signal-line { opacity:.5; animation-duration:5.8s; }
  .meter { position:absolute; z-index:4; left:50%; top:50%; width:117px; height:117px; display:grid; place-items:center; border-radius:50%; transform:translate(-50%,-50%); background:radial-gradient(circle at 38% 28%,#fff 0%,#eef9ff 48%,#deeffb 76%); box-shadow:0 0 0 1px rgba(47,128,237,.2),0 11px 27px rgba(47,128,237,.16),inset 0 0 20px rgba(0,210,255,.12); }
  .meter:before { content:""; position:absolute; inset:8px; border-radius:inherit; background:conic-gradient(#2f80ed calc(var(--confidence) * 1%), rgba(47,128,237,.12) 0); -webkit-mask:radial-gradient(transparent 59%, #000 60%); mask:radial-gradient(transparent 59%, #000 60%); transform:rotate(-90deg); animation: meter-reveal .9s cubic-bezier(.18,.86,.24,1) both; }
  .meter-copy { position:relative; z-index:1; display:flex; flex-direction:column; align-items:center; text-align:center; }
  .meter-copy span { color:#5c7d97; font-size:8px; font-weight:830; letter-spacing:.105em; }
  .meter-copy strong { color:#153854; font-size:27px; line-height:1; letter-spacing:-.07em; }
  .meter-copy small { color:#607c93; font-size:8px; font-weight:760; }
  .region-node { position:absolute; z-index:5; display:grid; place-items:center; width:35px; height:28px; margin:-14px 0 0 -17px; border:1px solid rgba(47,128,237,.17); border-radius:9px; color:#47708e; background:rgba(255,255,255,.78); box-shadow:0 6px 16px rgba(57,97,132,.09); font-size:8px; font-weight:850; letter-spacing:.08em; cursor:pointer; }
  .region-node.active { color:#fff; border-color:#2f80ed; background:linear-gradient(135deg,#2f80ed,#00bfe8); box-shadow:0 7px 17px rgba(47,128,237,.23); }
  .region-node[data-mode="still"] { color:#7e92a2; }
  .region-node.active[data-mode="still"] { color:#fff; background:linear-gradient(135deg,#75899a,#98a9b6); border-color:#75899a; }
  .inspector { position:absolute; z-index:9; left:10px; right:10px; bottom:9px; padding:9px 10px; border:1px solid rgba(47,128,237,.22); border-radius:13px; background:rgba(255,255,255,.95); box-shadow:0 10px 25px rgba(47,88,124,.16); opacity:0; transform:translateY(10px); pointer-events:none; transition:opacity .18s ease, transform .18s ease; }
  .paused .inspector { opacity:1; transform:translateY(0); }
  .inspect-top { display:flex; justify-content:space-between; gap:8px; color:#2f80ed; font-size:8px; font-weight:840; letter-spacing:.09em; }
  .inspect-top span:last-child { color:#6d879b; }
  .inspector strong { display:block; margin-top:3px; color:#153854; font-size:13px; letter-spacing:-.02em; }
  .inspector p { margin:2px 0 0; color:#5b768d; font-size:10px; line-height:1.3; }
  .paused .ambient, .paused .route-live, .paused .signal-line, .paused .signal-dot, .paused .orbit, .paused .ticker-track, .paused .meter:before, .paused .region-node { animation-play-state:paused !important; }
  .sim-footer { display:flex; align-items:center; justify-content:space-between; gap:9px; min-height:35px; padding:7px 12px 9px; border-top:1px solid rgba(47,128,237,.1); color:#5f7c94; font-size:9px; font-weight:740; }
  .sim-footer b { color:#173955; font-size:10px; }
  .mood { display:inline-flex; align-items:center; gap:5px; color:#b46a18; font-size:8px; font-weight:840; letter-spacing:.09em; text-transform:uppercase; }
  .mood i { width:6px; height:6px; border-radius:50%; background:#f2994a; box-shadow:0 0 0 3px rgba(242,153,74,.12); }
  .steady .mood { color:#138167; } .steady .mood i { background:#12b886; box-shadow:0 0 0 3px rgba(18,184,134,.11); }
  .critical .mood { color:#b53d3d; } .critical .mood i { background:#eb5757; box-shadow:0 0 0 3px rgba(235,87,87,.12); }
  @keyframes ticker-slide { to { transform:translateX(-50%); } }
  @keyframes ambient-drift { from { stroke-dashoffset:0; } 50% { stroke-dashoffset:-92; } to { stroke-dashoffset:-186; } }
  @keyframes route-flow { to { stroke-dashoffset:-118; } }
  @keyframes orbit-cw { from { transform:translate(-50%,-50%) rotate(0deg); } to { transform:translate(-50%,-50%) rotate(360deg); } }
  @keyframes orbit-ccw { from { transform:translate(-50%,-50%) rotate(360deg); } to { transform:translate(-50%,-50%) rotate(0deg); } }
  @keyframes particle-burst { 0%,100% { opacity:.38; transform:scale(.7); } 45% { opacity:1; transform:scale(1.55); } 65% { opacity:.35; transform:scale(.82); } }
  @keyframes meter-reveal { from { opacity:0; transform:rotate(-90deg) scale(.82); } to { opacity:1; transform:rotate(-90deg) scale(1); } }
  @keyframes signal-breathe { 0%,100% { opacity:.62; } 50% { opacity:1; } }
  @keyframes signal-dot-pulse { 0%,100% { opacity:.58; r:3.1; } 50% { opacity:1; r:5.2; } }
  @media (prefers-reduced-motion:reduce) { *,*:before,*:after { animation:none !important; transition:none !important; } }
</style>
<main class="live-sim" id="live-sim" aria-label="Interactive live operating simulation" role="button" tabindex="0">
  <div class="sim-top"><div class="sim-status"><i></i><span>Live signals · Trust / Risk / Friction</span></div><div class="tap-label" id="tap-label">Tap to inspect</div></div>
  <div class="ticker"><div class="ticker-track"><span id="ticker-a"></span><span id="ticker-b" aria-hidden="true"></span></div></div>
  <section class="sim-stage" id="sim-stage">
    <div class="grid"></div>
    <svg class="stream-map" viewBox="0 0 600 280" preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id="loadGradient" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#00d2ff" stop-opacity=".42"/><stop offset="100%" stop-color="#00d2ff" stop-opacity="0"/></linearGradient>
      </defs>
      <text class="chart-axis" x="8" y="36">100</text><text class="chart-axis" x="12" y="132">50</text><text class="chart-axis" x="15" y="228">0</text>
      <path class="signal-area" id="load-area"/>
      <path class="signal-line trust" id="trust-trace"/>
      <path class="signal-line risk" id="risk-trace"/>
      <path class="signal-line friction" id="friction-trace"/>
      <circle class="signal-dot trust" id="trust-dot" r="4"/><circle class="signal-dot risk" id="risk-dot" r="4"/><circle class="signal-dot friction" id="friction-dot" r="4"/>
    </svg>
    <div class="signal-legend"><span class="trust">T <b id="trust-reading"></b></span><span class="risk">R <b id="risk-reading"></b></span><span class="friction">F <b id="friction-reading"></b></span></div>
    <div class="orbit one"><i></i><i></i><i></i></div><div class="orbit two"><i></i><i></i></div>
    <div class="meter" id="meter"><div class="meter-copy"><span>CONFIDENCE</span><strong id="confidence"></strong><small id="risk-label"></small></div></div>
    <div id="nodes"></div>
    <div class="inspector" id="inspector"><div class="inspect-top"><span>PAUSED · INSPECTING</span><span>Tap to resume</span></div><strong id="inspect-title"></strong><p id="inspect-copy"></p></div>
  </section>
  <div class="sim-footer"><div><b id="footer-focus"></b> <span id="footer-state"></span></div><div class="mood"><i></i><span id="mood-label"></span></div></div>
</main>
<script>
  const model = """ + serialized_payload + """;
  const root = document.getElementById('live-sim');
  const nodes = document.getElementById('nodes');
  const meter = document.getElementById('meter');
  const confidence = document.getElementById('confidence');
  const riskLabel = document.getElementById('risk-label');
  const inspectTitle = document.getElementById('inspect-title');
  const inspectCopy = document.getElementById('inspect-copy');
  const footerFocus = document.getElementById('footer-focus');
  const footerState = document.getElementById('footer-state');
  const moodLabel = document.getElementById('mood-label');
  const tapLabel = document.getElementById('tap-label');
  const trustTrace = document.getElementById('trust-trace');
  const riskTrace = document.getElementById('risk-trace');
  const frictionTrace = document.getElementById('friction-trace');
  const loadArea = document.getElementById('load-area');
  let selected = model.regions.find(region => region.code === model.focus) || model.regions[0];
  let paused = false;

  confidence.textContent = model.event.confidence + '%';
  riskLabel.textContent = model.metrics.risk + ' risk';
  meter.style.setProperty('--confidence', model.event.confidence);
  root.classList.add(model.tone);

  function chartPoint(value, index, total) {
    return { x: 18 + (index / Math.max(1, total - 1)) * 566, y: 232 - (Number(value) / 100) * 190 };
  }
  function tracePath(key) {
    return model.trace.map((point, index) => {
      const spot = chartPoint(point[key], index, model.trace.length);
      return (index ? 'L' : 'M') + spot.x.toFixed(1) + ',' + spot.y.toFixed(1);
    }).join(' ');
  }
  function drawSignalBoard() {
    const last = model.trace[model.trace.length - 1];
    trustTrace.setAttribute('d', tracePath('trust'));
    riskTrace.setAttribute('d', tracePath('risk'));
    frictionTrace.setAttribute('d', tracePath('friction'));
    const loadPath = tracePath('load');
    loadArea.setAttribute('d', loadPath + ' L584,238 L18,238 Z');
    [['trust', 'trust-dot'], ['risk', 'risk-dot'], ['friction', 'friction-dot']].forEach(([key, id]) => {
      const spot = chartPoint(last[key], model.trace.length - 1, model.trace.length);
      const dot = document.getElementById(id); dot.setAttribute('cx', spot.x); dot.setAttribute('cy', spot.y);
    });
    document.getElementById('trust-reading').textContent = model.metrics.trust;
    document.getElementById('risk-reading').textContent = model.metrics.risk;
    document.getElementById('friction-reading').textContent = model.metrics.friction;
  }

  function localSession(region) {
    const parts = new Intl.DateTimeFormat('en-US', {weekday:'short', hour:'2-digit', minute:'2-digit', hourCycle:'h23', timeZone:region.zone}).formatToParts(new Date());
    const read = type => parts.find(part => part.type === type)?.value || '';
    const day = read('weekday'); const hour = Number(read('hour')); const minute = read('minute');
    const weekday = !['Sat', 'Sun'].includes(day);
    const regionalWindow = weekday && hour >= 7 && hour < 20;
    const handoff = weekday && ((hour >= 5 && hour < 7) || (hour >= 20 && hour < 22));
    let mode = 'still'; let label = day === 'Sat' || day === 'Sun' ? 'Weekend watch' : 'After-hours watch';
    if (regionalWindow) { mode = 'fast'; label = 'Regional window active'; }
    else if (handoff) { mode = 'ambient'; label = 'Pre-open / handoff'; }
    return { day, time: String(hour).padStart(2, '0') + ':' + minute, mode, label };
  }
  function activityCopy(session) {
    if (session.mode === 'fast') return 'Synthetic regional activity is moving with this local operating window.';
    if (session.mode === 'ambient') return 'Synthetic handoff activity is moving slowly while this regional window prepares.';
    return model.continuous_network ? 'Local human session is quiet; the synthetic 24/7 network remains guarded in the background.' : 'The regional operating window is quiet; the visual stream is intentionally calm.';
  }
  function paint() {
    const session = localSession(selected);
    root.classList.remove('fast', 'ambient', 'still', 'network-fast'); root.classList.add(model.continuous_network ? 'network-fast' : session.mode);
    document.querySelectorAll('.region-node').forEach(button => button.classList.toggle('active', button.dataset.code === selected.code));
    const networkState = model.continuous_network ? '24/7 SYNTHETIC NETWORK ACTIVE · ' : '';
    const ticker = model.world + ' · TRUST ' + model.metrics.trust + ' · RISK ' + model.metrics.risk + ' · FRICTION ' + model.metrics.friction + ' · LATENCY ' + model.metrics.latency_ms + 'MS · ' + networkState + selected.code + ' ' + session.day.toUpperCase() + ' ' + session.time + ' · ' + session.label.toUpperCase() + ' · ' + model.event.value + ' AT STAKE · ' + model.event.blocker.toUpperCase() + ' CHECK · ' + model.event.reviews + ' HUMAN REVIEWS';
    document.getElementById('ticker-a').textContent = ticker; document.getElementById('ticker-b').textContent = ticker;
    inspectTitle.textContent = selected.city + ' · ' + session.day + ' ' + session.time;
    inspectCopy.textContent = 'Trust ' + model.metrics.trust + ' · Risk ' + model.metrics.risk + ' · Friction ' + model.metrics.friction + ' · ' + session.label + ' · synthetic activity ' + selected.load + '% · ' + activityCopy(session);
    footerFocus.textContent = selected.code + ' · ' + session.label;
    footerState.textContent = ' · ' + model.event.value + ' at stake';
    moodLabel.textContent = model.tone === 'critical' ? 'Critical stop' : model.tone === 'attention' ? 'Human attention' : 'Verified flow';
  }
  model.regions.forEach(region => {
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'region-node'; button.dataset.code = region.code; button.dataset.mode = region.motion_mode;
    button.style.left = region.x + '%'; button.style.top = region.y + '%'; button.textContent = region.code;
    button.setAttribute('aria-label', 'Inspect ' + region.city);
    button.addEventListener('click', event => { event.stopPropagation(); selected = region; paused = true; root.classList.add('paused'); tapLabel.textContent = 'Tap to resume'; paint(); });
    nodes.appendChild(button);
  });
  function togglePause() { paused = !paused; root.classList.toggle('paused', paused); tapLabel.textContent = paused ? 'Tap to resume' : 'Tap to inspect'; paint(); }
  root.addEventListener('click', togglePause);
  root.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); togglePause(); } });
  window.setInterval(() => { if (!paused) paint(); }, 1000);
  drawSignalBoard();
  paint();
</script>
        """,
        height=306,
        scrolling=False,
    )


def render_simulation_tuner(telemetry: dict[str, Any]) -> None:
    """Put meaningful simulator inputs within reach without crowding the glance."""

    with st.expander("Tune live simulation", expanded=st.session_state.sym_show_tuning):
        st.markdown(
            "<div class='sym-section-note' style='margin:.05rem 0 .6rem'>"
            "Changes the synthetic operating model, routing threshold, scenario range, and future audit record. "
            "Human authorization remains required.</div>",
            unsafe_allow_html=True,
        )
        st.selectbox(
            "Operating posture",
            list(SIMULATION_PRESETS),
            index=list(SIMULATION_PRESETS).index(st.session_state.sym_sim_preset),
            format_func=lambda key: str(SIMULATION_PRESETS[key]["label"]),
            key="sym_sim_preset",
            on_change=apply_simulation_preset,
        )
        stream_col, latency_col = st.columns(2, gap="small")
        with stream_col:
            st.radio(
                "Signal speed",
                [1, 2, 5],
                index=[1, 2, 5].index(st.session_state.sym_stream_speed),
                horizontal=True,
                format_func=lambda value: f"{value}×",
                key="sym_stream_speed",
                help="Visual-only playback speed. It does not change the decision model.",
            )
        with latency_col:
            st.slider(
                "Fallback at",
                min_value=160,
                max_value=520,
                value=st.session_state.sym_latency_threshold,
                step=10,
                key="sym_latency_threshold",
                format="%d ms",
                on_change=mark_simulation_custom,
            )
        risk_col, friction_col = st.columns(2, gap="small")
        with risk_col:
            st.slider(
                "Risk sensitivity",
                min_value=-20,
                max_value=20,
                value=st.session_state.sym_risk_bias,
                step=1,
                key="sym_risk_bias",
                on_change=mark_simulation_custom,
                help="Higher values make the synthetic model more conservative about risk.",
            )
        with friction_col:
            st.slider(
                "Friction sensitivity",
                min_value=-20,
                max_value=20,
                value=st.session_state.sym_friction_bias,
                step=1,
                key="sym_friction_bias",
                on_change=mark_simulation_custom,
                help="Higher values amplify the simulated cost of unresolved evidence and operational drag.",
            )
        routing = telemetry["routing"]
        route_tone = "#c64551" if routing["fallback_active"] else "#17816a"
        st.markdown(
            f"<div class='sym-disclosure' style='margin:.5rem 0 0;border-color:{route_tone}33'>"
            f"<strong style='color:{route_tone}'>{esc(routing['route'].upper())} ROUTE</strong> · "
            f"{esc(routing['reason'])}</div>",
            unsafe_allow_html=True,
        )


def render_decision_pulse(event: dict[str, Any], telemetry: dict[str, Any], private_mode: bool) -> None:
    """Render the compact decision reading beneath the live visual."""

    evidence = event["evidence"]
    verified = sum(item["state"] == "verified" for item in evidence)
    conflicting = sum(item["state"] == "conflicting" for item in evidence)
    missing = sum(item["state"] == "missing" for item in evidence)
    blocker = next((item for item in evidence if item["state"] == "missing"), evidence[-1])
    metrics = telemetry["metrics"]
    signal = esc(_short_signal(event["signal"]))
    title = esc(private_value(event["title"], private_mode))
    value = esc(private_value(event["value"], private_mode))

    st.markdown(
        f"""
<section class="sym-glance sym-decision-summary" aria-label="Active decision">
  <div class="sym-glance-status">
    <span class="sym-status"><span class="sym-dot amber"></span> Action required</span>
    <span class="sym-glance-queue">Queue {event["queue_position"]} · {esc(event["window"])}</span>
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
    <div class="sym-glance-metric trust"><b>{metrics["trust"]}</b><span>trust</span><i></i></div>
    <div class="sym-glance-metric risk"><b>{metrics["risk"]}</b><span>risk</span><i></i></div>
    <div class="sym-glance-metric friction"><b>{metrics["friction"]}</b><span>friction</span><i></i></div>
    <div class="sym-glance-metric evidence"><b>{verified}/{conflicting}/{missing}</b><span>evidence</span><i></i></div>
  </div>

  <div class="sym-blocker-strip">
    <span class="sym-dot amber"></span>
    <strong>{missing} blocker{'s' if missing != 1 else ''}</strong>
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

    cta, hold, tune = st.columns([1.2, .58, .52], gap="small")
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
    with tune:
        if st.button("Tune", key=f"{event['id']}-open-tune", use_container_width=True):
            st.session_state.sym_show_tuning = True
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
        state_class = "active" if region["motion_mode"] == "fast" else "handoff" if region["motion_mode"] == "ambient" else "quiet"
        opacity = max(.22, int(region["load"]) / 100)
        cards.append(
            f"""
<div class="sym-region" style="--pulse-opacity:{opacity:.2f}">
  <div class="sym-region-head">{esc(region["city"])} · {esc(region["code"])}</div>
  <div class="sym-region-time">{esc(region["time"])}</div>
  <div class="sym-region-state {state_class}">{esc(region["status"])} · {region["load"]}% load</div>
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
  <div class="sym-section-title">Counterfactual outcomes</div>
  <div class="sym-section-note">Compare what each available action could cost, protect, expose, or unlock</div>
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


def render_action_controls(event: dict[str, Any], profile: dict[str, Any], telemetry: dict[str, Any]) -> None:
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
        entry = audit_entry(event, pending, profile["current_user"], telemetry=telemetry)
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
  <div class="sym-section-title">Decision impact · before and after</div>
  <div class="sym-section-note">Synthetic outcome · accountable action preserved</div>
</div>
<section class="sym-card">
  <div class="sym-card-inner">
    <div class="sym-impact-grid">
      <article class="sym-impact before"><span>Before · unresolved</span><b>{esc(event["risk"])} exposure</b><p>{esc(private_value(event["value"], private_mode))} at stake · {esc(event["challenge"])}</p></article>
      <article class="sym-impact after"><span>After · {esc(outcome["state"])}</span><b>{esc(outcome["headline"])}</b><p>{esc(outcome["learning"])}</p></article>
    </div>
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
        '<div class="sym-section-head"><div class="sym-section-title">Decision replay · accountable record</div><div class="sym-section-note">Timestamped decisions, policy reason codes, and accountable authority</div></div>',
        unsafe_allow_html=True,
    )
    if not audit_log:
        st.markdown(
            '<div class="sym-empty">No action has been authorized yet. The first confirmed decision will enter the replay with its evidence, policy, outcome, and accountable human.</div>',
            unsafe_allow_html=True,
        )
        return

    entries: list[str] = []
    for record in audit_log[:6]:
        identity = private_value(record["authorized_by"], private_mode)
        outcome = record["outcome"]
        configuration = record.get("simulation_configuration", {})
        snapshot = record.get("signal_snapshot", {})
        replay_signal = ""
        if configuration and snapshot:
            replay_signal = (
                f"<br><span style='color:#6f8ba1'>"
                f"{esc(str(configuration.get('label', 'Simulation')))} posture · "
                f"{esc(str(snapshot.get('route', 'primary')).upper())} route · "
                f"{esc(str(snapshot.get('latency_ms', '—')))}ms captured at authorization</span>"
            )
        entries.append(
            f"""
<div class="sym-timeline-entry">
  <div class="sym-timeline-time">{esc(record["display_time"])} · {esc(record["policy"])}</div>
  <div class="sym-timeline-action">{esc(identity)} {esc(record["action"].lower())} · {esc(record["event"])}</div>
  <div class="sym-timeline-copy">
    {esc(outcome["learning"])} Confidence {record["confidence"]}% · {esc(record["risk"])} exposure · {esc(private_value(record["value"], private_mode))}{replay_signal}
  </div>
</div>
            """
        )
    st.markdown(f'<div class="sym-timeline">{"".join(entries)}</div>', unsafe_allow_html=True)


def _format_projection_value(value: float) -> str:
    """Format a synthetic projection in the compact financial notation used by the board."""

    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def _formal_chart_point(value: int, index: int, total: int) -> tuple[float, float]:
    return 28 + (index / max(1, total - 1)) * 664, 222 - (value / 100) * 178


def _formal_chart_path(trace: list[dict[str, int]], key: str) -> str:
    return " ".join(
        f"{'M' if index == 0 else 'L'}{x:.1f},{y:.1f}"
        for index, point in enumerate(trace)
        for x, y in [_formal_chart_point(point[key], index, len(trace))]
    )


def _formal_load_area(trace: list[dict[str, int]]) -> str:
    return f"{_formal_chart_path(trace, 'load')} L692,232 L28,232 Z"


def _formal_signal_clashes(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find genuine order changes between the formal operating measures.

    A crossover means the relative order of two independent signals changed.
    It is an attention marker—not a causal claim or an automated action.
    """

    pairs = (
        ("trust", "risk", "Trust", "Risk"),
        ("trust", "friction", "Trust", "Friction"),
        ("risk", "friction", "Risk", "Friction"),
    )
    clashes: list[dict[str, Any]] = []
    for index in range(1, len(trace)):
        previous = trace[index - 1]
        current = trace[index]
        for first_key, second_key, first_label, second_label in pairs:
            previous_delta = int(previous[first_key]) - int(previous[second_key])
            current_delta = int(current[first_key]) - int(current[second_key])
            if previous_delta * current_delta > 0 or (previous_delta == 0 and current_delta == 0):
                continue
            denominator = abs(previous_delta) + abs(current_delta)
            progress = abs(previous_delta) / denominator if denominator else .5
            value = int(previous[first_key]) + progress * (int(current[first_key]) - int(previous[first_key]))
            x, y = _formal_chart_point(value, index - 1 + progress, len(trace))
            leader = first_label if int(current[first_key]) >= int(current[second_key]) else second_label
            follower = second_label if leader == first_label else first_label
            clashes.append(
                {
                    "x": x,
                    "y": y,
                    "label": f"{leader} moved above {follower}",
                }
            )
    return clashes[-5:]


def render_formal_equalizer_board(telemetry: dict[str, Any]) -> None:
    """Render the formal signal board as a living dotted equalizer.

    The browser only scrolls the engine's canonical synthetic signal stream.
    Trust controls the upper amplitude, risk/friction control the lower
    amplitude, and operating load brightens the center band. Hovering is
    observational; tapping freezes the exact displayed frame without changing
    any recommendation or underlying simulation state.
    """

    trace = telemetry["ticker_trace"]
    clashes = _formal_signal_clashes(trace)
    payload = {
        "trace": trace,
        "metrics": telemetry["metrics"],
        "routing": telemetry["routing"],
        "controls": telemetry["controls"],
        "time_basis": telemetry["time_basis"],
        "clash_label": clashes[-1]["label"] if clashes else "No crossover in the retained trace",
        "has_clash": bool(clashes),
    }
    serialized_payload = json.dumps(payload).replace("</", "<\\/")

    components.html(
        """
<style>
  :root { color-scheme:light; }
  * { box-sizing:border-box; }
  html,body { margin:0; overflow:hidden; background:transparent; font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
  .formal-equalizer { position:relative; overflow:hidden; min-height:449px; border:1px solid rgba(36,89,153,.21); border-radius:18px; color:#173854; background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(247,251,254,.96)); box-shadow:0 13px 31px rgba(42,83,122,.11),inset 0 1px 0 rgba(255,255,255,.92); user-select:none; }
  .formal-equalizer:before { content:""; position:absolute; inset:0; pointer-events:none; opacity:.62; background-image:linear-gradient(rgba(46,100,163,.065) 1px,transparent 1px),linear-gradient(90deg,rgba(46,100,163,.065) 1px,transparent 1px); background-size:22px 22px; }
  .equalizer-head { position:relative; z-index:3; display:flex; align-items:flex-start; justify-content:space-between; gap:9px; padding:11px 12px 8px; }.equalizer-overline { color:#3a6b90; font-size:7px; font-weight:850; letter-spacing:.1em; text-transform:uppercase; }.equalizer-head h3 { margin:2px 0 0; color:#173854; font-size:13px; letter-spacing:-.02em; }.equalizer-head p { margin:3px 0 0; max-width:600px; color:#617c92; font-size:8.7px; line-height:1.3; font-weight:650; }.equalizer-route { display:inline-flex; align-items:center; gap:5px; flex:0 0 auto; margin-top:2px; padding:5px 7px; border:1px solid rgba(42,97,152,.14); border-radius:999px; background:rgba(255,255,255,.8); color:#217b67; font-size:7.1px; font-weight:850; letter-spacing:.075em; text-transform:uppercase; white-space:nowrap; }.equalizer-route i { width:6px; height:6px; border-radius:50%; background:#18a878; box-shadow:0 0 0 3px rgba(24,168,120,.12); }.equalizer-route.fallback { color:#ba4753; }.equalizer-route.fallback i { background:#d85762; box-shadow:0 0 0 3px rgba(216,87,98,.13); animation:equalizer-alert 1.05s ease-in-out infinite; }
  .equalizer-metrics { position:relative; z-index:2; display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); overflow:hidden; margin:0 12px; border:1px solid rgba(49,103,164,.18); border-radius:12px; background:rgba(255,255,255,.67); }.equalizer-metrics div { min-width:0; min-height:64px; padding:10px 10px 8px; border-right:1px solid rgba(49,103,164,.16); }.equalizer-metrics div:last-child { border-right:0; }.equalizer-metrics span { display:block; color:#668198; font-size:7.7px; font-weight:850; letter-spacing:.085em; text-transform:uppercase; }.equalizer-metrics b { display:block; margin-top:6px; color:#183e60; font-size:15px; letter-spacing:-.035em; }.equalizer-metrics i { display:block; height:2px; margin-top:8px; border-radius:99px; background:#8fb4ff; }.equalizer-metrics .risk i { background:#d85762; }.equalizer-metrics .friction i { background:#1e4fa3; }.equalizer-metrics .latency i { background:#36aee2; }
  .equalizer-clash { position:relative; z-index:2; display:inline-flex; align-items:center; gap:6px; margin:9px 12px 8px; padding:6px 8px; border:1px solid rgba(224,162,58,.38); border-radius:999px; color:#9d6519; background:rgba(255,249,235,.89); font-size:7.4px; font-weight:850; letter-spacing:.065em; text-transform:uppercase; }.equalizer-clash i { width:6px; height:6px; border-radius:50%; background:#e0a23a; box-shadow:0 0 0 3px rgba(224,162,58,.13); animation:equalizer-clash-pulse 1.8s ease-in-out infinite; }.equalizer-clash.quiet { color:#668095; border-color:rgba(86,124,154,.18); background:rgba(255,255,255,.67); }.equalizer-clash.quiet i { background:#8aa5b8; box-shadow:none; animation:none; }
  .equalizer-stage { position:relative; z-index:1; height:245px; overflow:hidden; border-top:1px solid rgba(50,104,164,.09); border-bottom:1px solid rgba(50,104,164,.11); background:radial-gradient(ellipse at 52% 50%,rgba(219,238,251,.56),rgba(250,253,255,.4) 56%,rgba(237,247,253,.66)); }.equalizer-stage:before { content:""; position:absolute; inset:-20% -10%; pointer-events:none; opacity:.75; background:radial-gradient(ellipse at 73% 32%,rgba(77,134,237,.12),transparent 42%),radial-gradient(ellipse at 20% 77%,rgba(0,190,227,.08),transparent 41%); animation:equalizer-wash 9s ease-in-out infinite alternate; }.equalizer-stage:after { content:""; position:absolute; inset:0; pointer-events:none; opacity:.25; background:linear-gradient(90deg,transparent 0 21%,rgba(71,179,232,.17) 28%,transparent 35% 64%,rgba(77,134,237,.11) 70%,transparent 76%); background-size:180% 100%; animation:equalizer-stream 12s linear infinite; }
  #formal-equalizer-canvas { position:relative; z-index:1; display:block; width:100%; height:100%; outline:none; touch-action:manipulation; cursor:crosshair; } #formal-equalizer-canvas:focus-visible { box-shadow:inset 0 0 0 2px rgba(47,128,237,.55); }
  .equalizer-legend { position:absolute; z-index:3; right:10px; bottom:8px; display:flex; align-items:center; gap:6px; padding:5px 7px; border:1px solid rgba(44,99,156,.13); border-radius:999px; background:rgba(255,255,255,.84); color:#5c788f; font-size:7px; font-weight:830; letter-spacing:.055em; text-transform:uppercase; pointer-events:none; }.equalizer-legend span { display:inline-flex; align-items:center; gap:3px; }.equalizer-legend i { width:6px; height:6px; border-radius:50%; background:currentColor; }.equalizer-legend .trust { color:#8fb4ff; }.equalizer-legend .risk { color:#d85762; }.equalizer-legend .friction { color:#1e4fa3; }.equalizer-legend .load { color:#36aee2; }
  .equalizer-hint { position:absolute; z-index:3; left:10px; bottom:9px; display:inline-flex; align-items:center; gap:4px; color:#55778f; font-size:6.9px; font-weight:850; letter-spacing:.07em; text-transform:uppercase; pointer-events:none; }.equalizer-hint i { width:6px; height:6px; border-radius:50%; background:#36aee2; box-shadow:0 0 0 3px rgba(54,174,226,.1); animation:equalizer-clash-pulse 2.2s ease-in-out infinite; }
  .equalizer-window { position:absolute; z-index:4; top:10px; min-width:154px; max-width:196px; padding:7px 8px; border:1px solid rgba(38,96,157,.22); border-radius:10px; color:#173954; background:rgba(255,255,255,.94); box-shadow:0 10px 24px rgba(36,74,111,.16); backdrop-filter:blur(10px); opacity:0; transform:translate(-50%,-5px) scale(.98); transition:opacity .14s ease,transform .14s ease; pointer-events:none; }.equalizer-window.show { opacity:1; transform:translate(-50%,0) scale(1); }.equalizer-window strong { display:block; color:#2a6995; font-size:6.8px; font-weight:850; letter-spacing:.09em; text-transform:uppercase; }.equalizer-window b { display:block; margin-top:2px; color:#173954; font-size:9px; }.equalizer-window p { margin:2px 0 0; color:#55758d; font-size:7.3px; line-height:1.35; white-space:pre-line; }.equalizer-window em { display:block; margin-top:3px; color:#a56b18; font-size:6.8px; font-style:normal; font-weight:850; letter-spacing:.045em; text-transform:uppercase; }
  .formal-equalizer.paused .equalizer-stage:before,.formal-equalizer.paused .equalizer-stage:after,.formal-equalizer.paused .equalizer-route i,.formal-equalizer.paused .equalizer-clash i,.formal-equalizer.paused .equalizer-hint i { animation-play-state:paused; }
  @keyframes equalizer-alert { 0%,100% { opacity:.58; transform:scale(.8); } 50% { opacity:1; transform:scale(1.3); } } @keyframes equalizer-clash-pulse { 0%,100% { opacity:.52; transform:scale(.78); } 50% { opacity:1; transform:scale(1.25); } } @keyframes equalizer-wash { from { transform:translate3d(-2%,1%,0) scale(1); } to { transform:translate3d(2%,-2%,0) scale(1.06); } } @keyframes equalizer-stream { from { background-position:100% 0; } to { background-position:-80% 0; } }
  @media (max-width:460px) { .formal-equalizer { min-height:432px; border-radius:16px; }.equalizer-head { padding:9px 10px 7px; }.equalizer-overline { font-size:6.5px; }.equalizer-head h3 { font-size:12px; }.equalizer-head p { font-size:8px; max-width:230px; }.equalizer-route { padding:4px 6px; font-size:6.4px; }.equalizer-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); margin:0 10px; }.equalizer-metrics div { min-height:51px; padding:7px 8px 6px; border-bottom:1px solid rgba(49,103,164,.14); }.equalizer-metrics div:nth-child(2) { border-right:0; }.equalizer-metrics div:nth-child(3),.equalizer-metrics div:nth-child(4) { border-bottom:0; }.equalizer-metrics span { font-size:6.8px; }.equalizer-metrics b { margin-top:3px; font-size:13px; }.equalizer-metrics i { margin-top:4px; }.equalizer-clash { margin:7px 10px 6px; font-size:6.6px; }.equalizer-stage { height:214px; }.equalizer-legend { right:7px; bottom:7px; gap:4px; padding:4px 5px; font-size:5.9px; }.equalizer-hint { left:8px; bottom:7px; font-size:5.9px; }.equalizer-window { top:8px; min-width:142px; max-width:175px; padding:6px 7px; }.equalizer-window b { font-size:8.4px; }.equalizer-window p { font-size:6.7px; } }
  @media (prefers-reduced-motion:reduce) { *,*:before,*:after { animation:none !important; transition:none !important; } }
</style>
<main class="formal-equalizer" id="formal-equalizer" aria-label="Interactive live signal equalizer">
  <header class="equalizer-head"><div><div class="equalizer-overline">Formal Symbiosis board · evolved</div><h3>Live Signals · Equalizer</h3><p>Dotted decision energy · crossovers surface a clash.</p></div><div class="equalizer-route" id="equalizer-route"><i></i><span id="equalizer-route-copy"></span></div></header>
  <section class="equalizer-metrics" aria-label="Current formal signal metrics"><div class="trust"><span>Trust</span><b id="metric-trust"></b><i></i></div><div class="risk"><span>Risk</span><b id="metric-risk"></b><i></i></div><div class="friction"><span>Friction</span><b id="metric-friction"></b><i></i></div><div class="latency"><span>Latency</span><b id="metric-latency"></b><i></i></div></section>
  <div class="equalizer-clash" id="equalizer-clash"><i></i><span id="equalizer-clash-copy"></span></div>
  <section class="equalizer-stage" id="equalizer-stage"><canvas id="formal-equalizer-canvas" tabindex="0" role="button" aria-label="Animated dotted signal equalizer. Hover for the current sample or tap anywhere to freeze and inspect it."></canvas><div class="equalizer-window" id="equalizer-window" aria-live="polite"><strong id="equalizer-window-state"></strong><b id="equalizer-window-title"></b><p id="equalizer-window-copy"></p><em id="equalizer-window-note"></em></div><div class="equalizer-hint"><i></i><span id="equalizer-hint-copy">Hover for detail · tap to freeze</span></div><div class="equalizer-legend"><span class="trust"><i></i>Trust</span><span class="risk"><i></i>Risk</span><span class="friction"><i></i>Friction</span><span class="load"><i></i>Load</span></div></section>
</main>
<script>
  const model = """ + serialized_payload + """;
  const shell = document.getElementById('formal-equalizer'); const canvas = document.getElementById('formal-equalizer-canvas'); const ctx = canvas.getContext('2d'); const stage = document.getElementById('equalizer-stage');
  const routeNode = document.getElementById('equalizer-route'); const routeCopy = document.getElementById('equalizer-route-copy'); const clashNode = document.getElementById('equalizer-clash'); const clashCopy = document.getElementById('equalizer-clash-copy'); const hintCopy = document.getElementById('equalizer-hint-copy');
  const info = document.getElementById('equalizer-window'); const infoState = document.getElementById('equalizer-window-state'); const infoTitle = document.getElementById('equalizer-window-title'); const infoCopy = document.getElementById('equalizer-window-copy'); const infoNote = document.getElementById('equalizer-window-note');
  const stream = model.trace || []; const reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches; const speed = Number(model.controls.speed || 1); const sampleMs = 430;
  let width=1,height=1,dpr=1,offset=0,lastTime=0,frameId=null,paused=false,selected=null,selectedX=null;
  function clamp(value,min,max) { return Math.max(min,Math.min(max,value)); } function modulo(value,length) { return ((value%length)+length)%length; } function sampleAt(index) { return stream[modulo(index,stream.length)]; }
  function bounds() { const left=29,right=Math.max(52,width-13),top=15,bottom=Math.max(37,height-25); return {left,right,top,bottom,mid:(top+bottom)/2}; }
  function state() { const area=bounds(); const visible=Math.max(32,Math.min(88,Math.round((area.right-area.left)/7))); const whole=Math.floor(offset); const fraction=offset-whole; return {area,visible,fraction,base:stream.length-visible+whole,step:(area.right-area.left)/Math.max(1,visible-1)}; }
  function resize() { const box=canvas.getBoundingClientRect(); dpr=Math.max(1,Math.min(2,window.devicePixelRatio||1)); width=Math.max(1,Math.floor(box.width)); height=Math.max(1,Math.floor(box.height)); canvas.width=Math.floor(width*dpr); canvas.height=Math.floor(height*dpr); ctx.setTransform(dpr,0,0,dpr,0,0); draw(performance.now()); }
  function drawGrid(area) { ctx.save(); ctx.strokeStyle='rgba(48,99,157,.095)'; ctx.lineWidth=1; for(let row=0;row<5;row+=1) { const y=area.top+(area.bottom-area.top)*(row/4); ctx.beginPath(); ctx.moveTo(area.left,y); ctx.lineTo(area.right,y); ctx.stroke(); } const gap=Math.max(22,Math.round((area.right-area.left)/13)); for(let x=area.left;x<=area.right;x+=gap) { ctx.beginPath(); ctx.moveTo(x,area.top); ctx.lineTo(x,area.bottom); ctx.stroke(); } ctx.setLineDash([3,4]); ctx.strokeStyle='rgba(31,78,139,.28)'; ctx.beginPath(); ctx.moveTo(area.left,area.mid); ctx.lineTo(area.right,area.mid); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle='rgba(71,101,128,.68)'; ctx.font='800 6.8px Inter, sans-serif'; ctx.fillText('TRUST',3,area.top+4); ctx.fillText('BAL',8,area.mid+3); ctx.fillText('PRESSURE',3,area.bottom+2); ctx.fillText('earlier',area.left,height-8); ctx.fillText('now',area.right-16,height-8); ctx.restore(); }
  function pressure(sample) { return (Number(sample.risk)+Number(sample.friction))/2; } function rowsFor(sample,area) { const gap=clamp((area.bottom-area.top)/31,4.2,6); const maximum=Math.max(8,Math.floor((area.bottom-area.top)/(gap*2))-1); const up=clamp(Math.round(2+(Number(sample.trust)/100)*maximum*.92+Math.abs(Number(sample.load)-50)*.035),2,maximum); const down=clamp(Math.round(2+(pressure(sample)/100)*maximum*.92+Math.abs(Number(sample.load)-50)*.035),2,maximum); return {up,down,gap,maximum}; }
  function lowerTone(sample) { return Number(sample.risk)>=Number(sample.friction) ? '#d85762' : '#1e4fa3'; } function crossing(previous,current) { if(!previous) return ''; const pairs=[['trust','risk','Trust','Risk'],['trust','friction','Trust','Friction'],['risk','friction','Risk','Friction']]; for(const pair of pairs) { const before=Number(previous[pair[0]])-Number(previous[pair[1]]); const after=Number(current[pair[0]])-Number(current[pair[1]]); if(before*after<=0 && !(before===0&&after===0)) { const leader=Number(current[pair[0]])>=Number(current[pair[1]])?pair[2]:pair[3]; const follower=leader===pair[2]?pair[3]:pair[2]; return leader+' moved above '+follower; } } return ''; }
  function drawWave(points,area,now) {
    points.forEach((point,index) => {
      const profile=rowsFor(point.sample,area); const loadAlpha=.28+(Number(point.sample.load)/100)*.35;
      for(let row=-profile.up;row<=profile.down;row+=1) {
        const distance=Math.abs(row)/Math.max(profile.up,profile.down); const pulse=paused || reducedMotion ? .75 : .68+.23*((Math.sin(now/185+point.index*.77+row*.91)+1)/2);
        let colour='#4d86ed'; if(row<0) colour='#8fb4ff'; else if(row>0) colour=lowerTone(point.sample); if(Math.abs(row)<=1 && index%2===0) colour='#36aee2';
        ctx.save(); ctx.globalAlpha=(.2+(1-distance)*.61+loadAlpha*.18)*pulse; ctx.fillStyle=colour; ctx.shadowColor=colour; ctx.shadowBlur=row===0?4:distance<.28?2.4:0;
        const radius=1.05+(1-distance)*.42+(row===0?.2:0); ctx.beginPath(); ctx.arc(point.x,area.mid+row*profile.gap,radius,0,Math.PI*2); ctx.fill(); ctx.restore();
      }
      const clash=crossing(point.previous,point.sample);
      if(clash) { const pulse=paused || reducedMotion ? .75 : .48+.24*((Math.sin(now/240+index)+1)/2); ctx.save(); ctx.globalAlpha=pulse; ctx.strokeStyle='#e0a23a'; ctx.shadowColor='#e0a23a'; ctx.shadowBlur=6; ctx.lineWidth=1.15; ctx.beginPath(); ctx.arc(point.x,area.mid,4.5+profile.gap*.6,0,Math.PI*2); ctx.stroke(); ctx.restore(); }
    });
  }
  function drawLead(current,now) { const latest=sampleAt(current.base+current.visible-1); const next=sampleAt(current.base+current.visible); const mix=current.fraction; const sample={trust:Number(latest.trust)+(Number(next.trust)-Number(latest.trust))*mix,risk:Number(latest.risk)+(Number(next.risk)-Number(latest.risk))*mix,friction:Number(latest.friction)+(Number(next.friction)-Number(latest.friction))*mix,load:Number(latest.load)+(Number(next.load)-Number(latest.load))*mix}; const profile=rowsFor(sample,current.area); const pulse=paused || reducedMotion ? .85 : .7+.25*((Math.sin(now/205)+1)/2); const colour=lowerTone(sample); const stem=Math.min(18,Math.max(profile.up,profile.down)*profile.gap*.3); ctx.save(); ctx.globalAlpha=.58*pulse; ctx.strokeStyle=colour; ctx.shadowColor=colour; ctx.shadowBlur=9; ctx.lineWidth=1.35; ctx.beginPath(); ctx.moveTo(current.area.right,current.area.mid-stem); ctx.lineTo(current.area.right,current.area.mid+stem); ctx.stroke(); ctx.fillStyle=colour; ctx.globalAlpha=.92; ctx.beginPath(); ctx.arc(current.area.right,current.area.mid,2.8,0,Math.PI*2); ctx.fill(); ctx.restore(); }
  function drawFallback(points,area,now) { const breaches=points.filter(point=>Boolean(point.sample.fallback)); if(!breaches.length) return; const priority=breaches[breaches.length-1]; ctx.save(); breaches.forEach(point=>{ctx.strokeStyle=point===priority?'rgba(216,87,98,.72)':'rgba(216,87,98,.23)';ctx.lineWidth=1;ctx.setLineDash([3,4]);ctx.beginPath();ctx.moveTo(point.x,area.top);ctx.lineTo(point.x,area.bottom);ctx.stroke();});ctx.setLineDash([]);const pulse=paused || reducedMotion ? .8 : .52+.22*((Math.sin(now/220)+1)/2);ctx.globalAlpha=pulse;ctx.fillStyle='#d85762';const labelX=clamp(priority.x-23,area.left+2,area.right-47);ctx.fillRect(labelX,area.top+4,46,12);ctx.fillStyle='#fff';ctx.font='800 6.3px Inter, sans-serif';ctx.fillText('FALLBACK',labelX+4,area.top+12);ctx.restore(); }
  function drawGuide(area) { if(!selected||selectedX===null) return; ctx.save();ctx.strokeStyle='rgba(29,77,133,.45)';ctx.setLineDash([3,3]);ctx.beginPath();ctx.moveTo(selectedX,area.top);ctx.lineTo(selectedX,area.bottom);ctx.stroke();ctx.restore(); }
  function draw(now) { if(!stream.length) return; ctx.clearRect(0,0,width,height); const current=state(); const points=[]; for(let index=0;index<=current.visible;index+=1) { points.push({index:current.base+index,x:current.area.left+index*current.step-current.fraction*current.step,sample:sampleAt(current.base+index),previous:sampleAt(current.base+index-1)}); } ctx.save();ctx.beginPath();ctx.rect(current.area.left,current.area.top,current.area.right-current.area.left,current.area.bottom-current.area.top);ctx.clip();drawGrid(current.area);drawWave(points,current.area,now);drawFallback(points,current.area,now);drawLead(current,now);drawGuide(current.area);ctx.restore(); }
  function updateHeader() { const fallback=Boolean(model.routing.fallback_active); routeNode.classList.toggle('fallback',fallback); routeCopy.textContent=(fallback?'Fallback':'Primary')+' route'; clashNode.classList.toggle('quiet',!model.has_clash); clashCopy.textContent=model.has_clash?'Signal clash · '+model.clash_label:'No crossover in retained trace'; document.getElementById('metric-trust').textContent=model.metrics.trust; document.getElementById('metric-risk').textContent=model.metrics.risk; document.getElementById('metric-friction').textContent=model.metrics.friction; document.getElementById('metric-latency').textContent=model.metrics.latency_ms+'ms'; }
  function updateInfo(sample,x,frozen,previous) { if(!sample) return; selected=sample;selectedX=x;const clash=crossing(previous,sample);const route=sample.fallback?'Fallback route':'Primary route';infoState.textContent=frozen?'FROZEN FRAME':'LIVE LOOKUP';infoTitle.textContent=route+' · '+Math.round(sample.latency_ms)+'ms';infoCopy.textContent='Trust '+Math.round(sample.trust)+' · Risk '+Math.round(sample.risk)+' · Friction '+Math.round(sample.friction)+' · Load '+Math.round(sample.load)+'% · '+(sample.fallback?'fallback threshold crossed':'inside route threshold');infoNote.textContent=clash?'Signal clash · '+clash:(frozen?'Tap again to resume the stream':'Hovering does not change the decision');info.style.left=clamp(x,92,width-92)+'px';info.classList.add('show'); }
  function pointFromEvent(event) { const rect=canvas.getBoundingClientRect(); const current=state(); const x=clamp(event.clientX-rect.left,current.area.left,current.area.right); const relative=Math.round((x-current.area.left+current.fraction*current.step)/current.step); const visibleIndex=clamp(relative,0,current.visible); const index=current.base+visibleIndex; return {sample:sampleAt(index),previous:sampleAt(index-1),x:current.area.left+visibleIndex*current.step-current.fraction*current.step}; }
  function stop() { if(frameId!==null) { cancelAnimationFrame(frameId);frameId=null; } } function tick(now) { if(!lastTime)lastTime=now;const elapsed=Math.min(64,now-lastTime);lastTime=now;if(!paused&&!reducedMotion)offset+=elapsed/sampleMs*speed;draw(now);if(!paused&&!reducedMotion)frameId=requestAnimationFrame(tick); }
  function setPaused(next,point) { paused=next;shell.classList.toggle('paused',paused);hintCopy.textContent=paused?'Frozen · tap again to resume':'Hover for detail · tap to freeze';if(point)updateInfo(point.sample,point.x,paused,point.previous);if(paused){stop();draw(performance.now());}else{selected=null;selectedX=null;info.classList.remove('show');lastTime=performance.now();if(!reducedMotion)frameId=requestAnimationFrame(tick);} }
  canvas.addEventListener('pointerdown',event=>{event.preventDefault();if(paused){setPaused(false);return;}setPaused(true,pointFromEvent(event));});canvas.addEventListener('pointermove',event=>{if(event.pointerType==='touch'||paused)return;const point=pointFromEvent(event);updateInfo(point.sample,point.x,false,point.previous);draw(performance.now());});canvas.addEventListener('pointerleave',()=>{if(!paused){selected=null;selectedX=null;info.classList.remove('show');draw(performance.now());}});canvas.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();if(paused)setPaused(false);else{const current=state();const index=current.base+current.visible-1;setPaused(true,{sample:sampleAt(index),previous:sampleAt(index-1),x:current.area.right});}}});
  new ResizeObserver(resize).observe(stage);updateHeader();resize();if(!reducedMotion){lastTime=performance.now();frameId=requestAnimationFrame(tick);}else{const current=state();const index=current.base+current.visible-1;updateInfo(sampleAt(index),current.area.right,false,sampleAt(index-1));}
</script>
        """,
        height=460,
        scrolling=False,
    )


def render_formal_signal_board(event: dict[str, Any], telemetry: dict[str, Any]) -> None:
    """Render the formal decision signals in the interactive equalizer view."""

    render_formal_equalizer_board(telemetry)
    return

    trace = telemetry["trace"]
    metrics = telemetry["metrics"]
    latest = trace[-1]
    clashes = _formal_signal_clashes(trace)
    clash_marks = "".join(
        f'<g class="sym-formal-clash"><line x1="{clash["x"]:.1f}" x2="{clash["x"]:.1f}" y1="32" y2="220" class="sym-formal-clash-line"/><circle cx="{clash["x"]:.1f}" cy="{clash["y"]:.1f}" r="4.1" class="sym-formal-clash-dot"><title>{esc(clash["label"])}</title></circle></g>'
        for clash in clashes
    )
    clash_note = (
        f'<div class="sym-formal-clash-note"><i></i> Signal clash · {esc(clashes[-1]["label"])}</div>'
        if clashes
        else '<div class="sym-formal-clash-note quiet"><i></i> No crossover in the retained trace</div>'
    )
    grid_lines = "".join(
        f'<line x1="28" x2="692" y1="{y}" y2="{y}" class="sym-formal-grid-line"/>' for y in (44, 88, 132, 176, 220)
    )
    st.markdown(
        f"""
<section class="sym-formal-board" aria-label="Live decision signals">
  <div class="sym-formal-head">
    <div>
      <div class="sym-formal-overline">Formal Symbiosis board · evolved</div>
      <h3>Live Signals (Ticker View)</h3>
      <p>Independent Trust / Risk / Friction signals can converge and cross. Latency spikes trigger fallback routing.</p>
    </div>
    <div class="sym-formal-now"><span class="sym-dot {'red' if telemetry['routing']['fallback_active'] else 'green'}"></span> {esc(telemetry['routing']['route'])} · {esc(telemetry["time_basis"])}</div>
  </div>
  <div class="sym-formal-metrics" aria-label="Formal signal metrics">
    <div class="trust"><span>Trust</span><b>{metrics["trust"]}</b><i></i></div>
    <div class="risk"><span>Risk</span><b>{metrics["risk"]}</b><i></i></div>
    <div class="friction"><span>Friction</span><b>{metrics["friction"]}</b><i></i></div>
    <div class="latency"><span>Latency</span><b>{metrics["latency_ms"]}ms</b><i></i></div>
  </div>
  {clash_note}
  <div class="sym-formal-chart-wrap">
    <svg class="sym-formal-chart" viewBox="0 0 720 250" preserveAspectRatio="none" role="img" aria-label="Synthetic trust risk and friction signal trace">
      <defs><linearGradient id="sym-formal-load" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#48b8e8" stop-opacity=".33"/><stop offset="100%" stop-color="#48b8e8" stop-opacity="0"/></linearGradient></defs>
      {grid_lines}
      <text x="4" y="48" class="sym-formal-axis">100</text><text x="8" y="136" class="sym-formal-axis">50</text><text x="13" y="224" class="sym-formal-axis">0</text>
      <path d="{_formal_load_area(trace)}" class="sym-formal-load"/>
      <path d="{_formal_chart_path(trace, 'trust')}" class="sym-formal-line trust"/>
      <path d="{_formal_chart_path(trace, 'risk')}" class="sym-formal-line risk"/>
      <path d="{_formal_chart_path(trace, 'friction')}" class="sym-formal-line friction"/>
      {clash_marks}
      <circle cx="{_formal_chart_point(latest['trust'], len(trace) - 1, len(trace))[0]:.1f}" cy="{_formal_chart_point(latest['trust'], len(trace) - 1, len(trace))[1]:.1f}" r="4" class="sym-formal-dot trust"/>
      <circle cx="{_formal_chart_point(latest['risk'], len(trace) - 1, len(trace))[0]:.1f}" cy="{_formal_chart_point(latest['risk'], len(trace) - 1, len(trace))[1]:.1f}" r="4" class="sym-formal-dot risk"/>
      <circle cx="{_formal_chart_point(latest['friction'], len(trace) - 1, len(trace))[0]:.1f}" cy="{_formal_chart_point(latest['friction'], len(trace) - 1, len(trace))[1]:.1f}" r="4" class="sym-formal-dot friction"/>
      <text x="28" y="244" class="sym-formal-axis">earlier</text><text x="333" y="244" class="sym-formal-axis">decision trace</text><text x="663" y="244" class="sym-formal-axis">now</text>
    </svg>
    <div class="sym-formal-legend"><span class="trust">Trust</span><span class="risk">Risk</span><span class="friction">Friction</span><span class="load">Operating load</span></div>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_analysis(
    event: dict[str, Any], profile: dict[str, Any], regions: list[dict[str, Any]], telemetry: dict[str, Any]
) -> None:
    """Render the original board-risk and ledger tools as secondary review layers."""

    projection = telemetry["projection"]
    metrics = telemetry["metrics"]
    max_bucket = max(projection["histogram"])
    bars = "".join(
        f'<i style="height:{max(5, round((bucket / max_bucket) * 100))}%"></i>' for bucket in projection["histogram"]
    )
    ledger_rows: list[str] = []
    for item in event["evidence"]:
        tone = "verified" if item["state"] == "verified" else "attention" if item["state"] == "conflicting" else "critical"
        ledger_rows.append(
            f"<tr><td>{esc(item['source'])}</td><td>Evidence</td><td><span class='sym-ledger-state {tone}'>{esc(item['state'])}</span></td><td>{esc(item['reliability'])}</td><td>{esc(item['impact'])}</td></tr>"
        )
    for region in sorted(regions, key=lambda item: int(item["load"]), reverse=True)[:3]:
        tone = "verified" if region["motion_mode"] == "fast" else "attention" if region["motion_mode"] == "ambient" else "neutral"
        ledger_rows.append(
            f"<tr><td>{esc(region['city'])} · {esc(region['code'])}</td><td>Operating region</td><td><span class='sym-ledger-state {tone}'>{esc(region['status'])}</span></td><td>{region['load']}% load</td><td>{esc(region['posture'])}</td></tr>"
        )

    with st.expander("Formal analytics · scenario range and signal register", expanded=False):
        st.markdown(
            f"""
<div class="sym-section-head" style="margin-top:.1rem">
  <div class="sym-section-title">Monte Carlo Risk Projection</div>
  <div class="sym-section-note">Seed-locked synthetic scenario range derived from this decision’s Trust / Risk / Friction state</div>
</div>
<div class="sym-projection-grid">
  <section class="sym-projection-card"><span>Base exposure</span><b>{_format_projection_value(projection['base_exposure'])}</b><small>current case posture</small></section>
  <section class="sym-projection-card"><span>P50</span><b>{_format_projection_value(projection['p50'])}</b><small>median scenario</small></section>
  <section class="sym-projection-card"><span>P90</span><b>{_format_projection_value(projection['p90'])}</b><small>tail threshold</small></section>
  <section class="sym-projection-card"><span>P99</span><b>{_format_projection_value(projection['p99'])}</b><small>severe tail</small></section>
</div>
<section class="sym-histogram-card"><div class="sym-histogram-head"><span>Scenario distribution</span><small>synthetic seed · {metrics['latency_ms']}ms signal latency</small></div><div class="sym-histogram">{bars}</div></section>
<div class="sym-section-head" style="margin-top:1rem"><div class="sym-section-title">Signal register</div><div class="sym-section-note">The formal evidence and operating inputs behind the recommendation</div></div>
<div class="sym-ledger-wrap"><table class="sym-ledger"><thead><tr><th>source</th><th>signal</th><th>state</th><th>measure</th><th>decision relevance</th></tr></thead><tbody>{''.join(ledger_rows)}</tbody></table></div>
            """,
            unsafe_allow_html=True,
        )


def render_landing(profile: dict[str, Any]) -> None:
    """Offer a deliberately short entry that previews motion, not a product essay."""

    logo = mynki_logo_data_uri()
    st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
<section class="sym-entry">
  <div class="sym-entry-mark" aria-hidden="true"><img src="{logo}" alt=""></div>
  <h1>Symbiosis</h1>
  <p>The formal decision system—now a mobile-first cockpit.</p>
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
    render_site_footer()


def render_site_footer() -> None:
    """Keep the requested parent-brand link present without adding copy noise."""

    st.markdown(
        '<footer class="sym-site-footer"><a href="https://mynki.ai" target="_blank" rel="noopener noreferrer">mynki.ai</a></footer>',
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
        controls=simulation_controls_from_state(),
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
    telemetry = decision_telemetry(event, regions, controls=simulation_controls_from_state())

    if st.session_state.sym_view == "glance":
        render_glance_header(profile)
        render_live_signals(
            event,
            profile,
            st.session_state.sym_private_mode,
            telemetry["controls"],
        )
        render_simulation_tuner(telemetry)
        render_decision_pulse(event, telemetry, st.session_state.sym_private_mode)
        render_glance_controls(event)
        render_glance_futures(event, st.session_state.sym_private_mode)
        render_site_footer()
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
    render_review_topology(
        event,
        profile,
        st.session_state.sym_private_mode,
        telemetry["controls"],
    )
    regions = render_global_pulse(profile, st.session_state.sym_private_mode)
    render_event_and_recommendation(event, profile, st.session_state.sym_private_mode)
    render_evidence(event)
    render_futures(event)
    render_action_controls(event, profile, telemetry)
    render_outcome(event, st.session_state.sym_private_mode)
    render_timeline(st.session_state.sym_audit, st.session_state.sym_private_mode)
    render_formal_signal_board(event, telemetry)
    render_analysis(event, profile, regions, telemetry)

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
    render_site_footer()


if __name__ == "__main__":
    run()
