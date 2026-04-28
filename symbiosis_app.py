# ============================================================
# SYMBIOSIS — Cinematic AI Handshake Demo (Patch 2)
# Visual storyboard frames: Incoming → Processing → Gatekeeping
# No transcripts. No walls of text. Just system thinking on-screen.
# ============================================================

import time
import random
import math
import textwrap
import html
import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components
try:
    import altair as alt
except Exception:  # altair may not be installed in some envs
    alt = None


# ------------------------------------------------------------
# VISUAL HELPERS (gauges + live ticker)
# ------------------------------------------------------------

# ------------------------------------------------------------
# SYNTHETIC AMEX-LIKE TRANSACTION FEED (demo data)
# ------------------------------------------------------------

SEGMENTS = ["Corporate", "Business", "Personal"]
GEO_SCOPES = ["Global", "Continent", "US", "Region"]
CHANNELS = ["POS", "ECOM"]


# 7-continent model (simulation)
CONTINENTS = [
    ("North America", "NA", ["US", "CA", "MX"]),
    ("South America", "SA", ["BR", "AR", "CL", "CO", "PE"]),
    ("Europe", "EU", ["GB", "DE", "FR", "ES", "NL", "IT"]),
    ("Africa", "AF", ["ZA", "EG", "NG", "KE", "MA"]),
    ("Asia", "AS", ["JP", "SG", "IN", "KR", "CN"]),
    ("Australia", "AU", ["AU", "NZ"]),
    ("Antarctica", "AN", ["AQ"]),
]

MCC = [
    ("Travel", ["Air", "Hotel", "Rail", "Rideshare"]),
    ("Dining", ["Restaurant", "Coffee", "Bar"]),
    ("Retail", ["Apparel", "Electronics", "Luxury"]),
    ("Services", ["SaaS", "Agency", "Consulting"]),
    ("Groceries", ["Market", "Delivery"]),
]

RISK_REASONS = [
    "velocity_spike",
    "geo_anomaly",
    "new_device",
    "mcc_outlier",
    "amount_outlier",
    "ip_reputation",
]


def _pick_region(rng: random.Random) -> tuple[str, str, str]:
    continent_name, continent_code, countries = rng.choice(CONTINENTS)
    return continent_name, continent_code, rng.choice(countries)


def _pick_mcc(rng: random.Random) -> tuple[str, str]:
    cat, subs = rng.choice(MCC)
    return cat, rng.choice(subs)


def _mask_ip(ip: str) -> str:
    # Only show coarse IP for fraud drilldown (privacy + realism)
    parts = ip.split(".")
    if len(parts) != 4:
        return "—"
    return f"{parts[0]}.{parts[1]}.{parts[2]}.x"


def _mk_ip(rng: random.Random) -> str:
    return f"{rng.randint(1,223)}.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}"


def mk_txn(rng: random.Random, segment: str, channel: str, geo_scope: str, sensitivity: int) -> dict:
    """Generate a single synthetic transaction event.

    IMPORTANT: This is demo data. No real AmEx data is used.
    """
    continent, region, country = _pick_region(rng)
    mcc_cat, mcc_sub = _pick_mcc(rng)

    # Amount distribution by segment/channel (roughly plausible)
    base = {"Corporate": 220, "Business": 140, "Personal": 70}[segment]
    chan_mul = 1.15 if channel == "ECOM" else 1.0
    amount = max(3, int(abs(rng.gauss(base, base * 0.65)) * chan_mul))

    # Core risk score (0..100)
    risk = clamp(int(abs(rng.gauss(28, 18)) + (sensitivity * 0.22)))

    # Fraud probability: higher when risk is high and in ECOM
    p_fraud = (0.02 + (risk / 180.0)) * (1.6 if channel == "ECOM" else 0.9)
    is_fraud = rng.random() < min(0.35, p_fraud)

    # If fraud, bump risk and attach a masked IP (drilldown only for fraud)
    ip = _mk_ip(rng) if is_fraud else ""
    if is_fraud:
        risk = clamp(risk + rng.randint(12, 35))

    reason = rng.choice(RISK_REASONS) if is_fraud or risk >= 65 else "normal"

    # Transport + network context (simulation)
    # ground dominates, but air/marine exist and may route via satellite
    transport = rng.choices(
        population=["ground", "air", "marine"],
        weights=[0.86, 0.10, 0.04],
        k=1,
    )[0]

    if transport in ("air", "marine"):
        network = rng.choices(["satellite", "terrestrial"], weights=[0.70, 0.30], k=1)[0]
    else:
        network = rng.choices(["terrestrial", "satellite"], weights=[0.96, 0.04], k=1)[0]

    # Scope filtering label (visual only)
    if geo_scope == "US":
        continent = "North America"
        region = "NA"
        country = "US"
    elif geo_scope == "Continent":
        # collapse to continent rollup for privacy/aggregation
        country = region
    elif geo_scope == "Region":
        # keep chosen region, but collapse country to region-level for privacy
        country = region

    return {
        "segment": segment,
        "channel": channel,
        "continent": continent,
        "region": region,
        "country": country,
        "transport": transport,
        "network": network,
        "mcc": f"{mcc_cat}/{mcc_sub}",
        "amount": amount,
        "risk": risk,
        "fraud": is_fraud,
        "ip": _mask_ip(ip) if is_fraud else "—",
        "reason": reason,
    }


def md(html: str) -> None:
    """Render HTML in Streamlit markdown without accidental code-block indentation."""
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


def gauge(label: str, value: int, color: str):
    """Simple horizontal bar gauge instead of boring numbers."""
    pct = max(0, min(100, value))
    md(
        f"""
<div class="card" style="padding:16px">
  <div class="metric-label">{label}</div>
  <div style="height:10px;background:#e2e8f0;border-radius:999px;margin-top:8px">
    <div style="width:{pct}%;height:10px;background:{color};border-radius:999px"></div>
  </div>
  <div style="font-size:26px;font-weight:900;margin-top:6px">{value}</div>
</div>
"""
    )


def render_ticker(pos_events: list[str], ecom_events: list[str], fraud_events: list[str]) -> None:
    def j(xs: list[str]) -> str:
        return "   |   ".join(xs) if xs else "—"

    st.markdown(
        f"""
<div class="tape-wrap">
  <div class="tape-lane">
    <div class="lane-label"><span class="lane-dot dot-pos"></span> POS</div>
    <div class="lane-track"><div class="lane-run">{j(pos_events)}</div></div>
  </div>
  <div class="tape-lane">
    <div class="lane-label"><span class="lane-dot dot-ecom"></span> ECOM</div>
    <div class="lane-track"><div class="lane-run">{j(ecom_events)}</div></div>
  </div>
  <div class="tape-lane">
    <div class="lane-label"><span class="lane-dot dot-fraud"></span> FRAUD</div>
    <div class="lane-track"><div class="lane-run">{j(fraud_events)}</div></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="SYMBIOSIS",
    layout="wide",
    initial_sidebar_state="expanded",
)



# ------------------------------------------------------------
# THEME (graph paper, VC-readable type)
# ------------------------------------------------------------

def apply_theme(base_font_px: int = 22, tape_seconds: int = 24) -> None:
    # NOTE: This is intentionally NOT an f-string.
    # CSS contains lots of `{}` braces, and f-strings will treat them as expressions.
    css = """
<style>
:root {
  --base-font: {{BASE_FONT_PX}}px;
  --tape-speed: {{TAPE_SECONDS}}s;
}

html, body, [class*="css"] {
  background-color: #f6f9fc !important;
  color: #0f172a !important;
  font-size: var(--base-font) !important;
  line-height: 1.35;
}

/* graph paper grid */
div[data-testid="stAppViewContainer"] {
  background:
    linear-gradient(#e2e8f0 1px, transparent 1px),
    linear-gradient(90deg, #e2e8f0 1px, transparent 1px);
  background-size: 28px 28px;
  background-color: #f6f9fc !important;
}

.block-container {
  padding-top: 2rem;
  max-width: 1500px;
  padding-bottom: 160px; /* leave room for tape */
}

h1 {
  font-size: 60px !important;
  font-weight: 950;
  letter-spacing: 1px;
  color: #0f172a !important;
}

.smallcap {
  font-size: 14px;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #dbe3ea;
  padding: 22px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  word-break: break-word;
}

.card, .card * { color: #0f172a !important; }

.metric-label {
  color: #475569 !important;
  font-weight: 900;
  font-size: 17px;
  letter-spacing: 0.02em;
}

.frame-title {
  font-size: 22px;
  font-weight: 950;
  margin-bottom: 6px;
}

.frame-sub {
  color: #475569 !important;
  font-size: 18px;
}

.decision {
  font-size: 82px;
  font-weight: 950;
  text-align: center;
  margin-top: 12px;
}

.accept { color: #16a34a; }
.block  { color: #dc2626; }
.defer  { color: #f59e0b; }

.badge {
  display: inline-block;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 12px;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  background: #eef2f7;
  font-weight: 900;
}

.badge-green { color: #16a34a; }
.badge-red   { color: #dc2626; }
.badge-amber { color: #b45309; }

/* KPI delta styling (▲▼ ±) */
.delta {
  font-weight: 950;
  letter-spacing: 0.02em;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.delta-up { color: #16a34a !important; }
.delta-down { color: #dc2626 !important; }
.delta-flat { color: #64748b !important; }

/* SLA breach pulse (latency / incident emphasis) */
@keyframes breachPulse {
  0% { box-shadow: 0 0 0 rgba(220,38,38,0.0); }
  50% { box-shadow: 0 0 0 10px rgba(220,38,38,0.12); }
  100% { box-shadow: 0 0 0 rgba(220,38,38,0.0); }
}
.breach-pulse {
  animation: breachPulse 1.15s ease-in-out infinite;
  border-color: rgba(220,38,38,0.55) !important;
}

@keyframes dashMove {
  to { stroke-dashoffset: -28; }
}
.route-dash {
  stroke-dasharray: 10 8;
  animation: dashMove 0.85s linear infinite;
}

.rule {
  height: 1px;
  background: #dbe3ea;
  margin: 18px 0;
}

div[data-testid="stSidebar"] {
  background: #ffffff !important;
  color: #0f172a !important;
  border-right: 1px solid #e2e8f0;
}

div[data-testid="stHeader"], header {
  background: transparent !important;
}

/* MARKET TAPE (3 lanes, finance vibe) */
.tape-wrap {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #ffffff;
  border-top: 1px solid #dbe3ea;
  color: #0f172a;
  overflow: hidden;
  z-index: 9999;
}

.tape-lane {
  display: grid;
  grid-template-columns: 120px 1fr;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-top: 1px solid #eef2f7;
}

.tape-lane:first-child { border-top: none; }

.lane-label {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-weight: 950;
  letter-spacing: 0.16em;
  font-size: 12px;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.lane-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  display: inline-block;
}

.dot-pos { background: #0ea5e9; }
.dot-ecom { background: #8b5cf6; }
.dot-fraud { background: #ef4444; }

.lane-track {
  overflow: hidden;
  white-space: nowrap;
}

 .lane-run {
  display: inline-block;
  padding-left: 100%;
  animation: tape var(--tape-speed) linear infinite;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-weight: 950;
  font-size: 16px;
  line-height: 1.2;
}

/* Ensure ticker deltas render with their own colors (don't get overridden) */
.tape-wrap .delta-up { color: #16a34a !important; }
.tape-wrap .delta-down { color: #dc2626 !important; }
.tape-wrap .delta-flat { color: #64748b !important; }

@keyframes tape {
  0% { transform: translateX(0); }
  100% { transform: translateX(-100%); }
}

/* Brand header bar */
.brandbar {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16px;
  padding:14px 18px;
  border:1px solid #dbe3ea;
  border-radius:14px;
  background:#ffffff;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  margin-top: 10px;
  margin-bottom: 18px;
}
.brand-left {
  display:flex;
  align-items:center;
  gap:12px;
}
.amex-badge {
  width:52px;
  height:36px;
  border-radius:10px;
  background:#0b74de;
  display:flex;
  align-items:center;
  justify-content:center;
  color:#ffffff;
  font-weight:950;
  letter-spacing:0.08em;
  font-size:14px;
}
.brand-title {
  font-size:26px;
  font-weight:950;
  margin:0;
  line-height:1.1;
}
.brand-sub {
  font-size:14px;
  color:#475569 !important;
  margin:0;
  opacity:0.9;
}
.role-chip {
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:8px 12px;
  border-radius:999px;
  border:1px solid #dbe3ea;
  background:#f8fafc;
  font-weight:900;
  font-size:12px;
  letter-spacing:0.10em;
  text-transform:uppercase;
}
.dot {
  width:10px;
  height:10px;
  border-radius:999px;
  background:#16a34a;
  display:inline-block;
}

/* Before/After block */
.ba-wrap { margin-top: 10px; }
.ba-card {
  background:#ffffff;
  border-radius:14px;
  border:1px solid #dbe3ea;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  padding:18px;
}
.ba-head {
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:14px;
  margin-bottom: 12px;
}
.ba-h {
  font-size:24px;
  font-weight:950;
  margin:0;
}
.ba-kicker {
  font-size:14px;
  color:#475569 !important;
  margin:0;
  opacity:0.85;
}
.ba-grid {
  display:grid;
  grid-template-columns: 1fr 1fr;
  gap:14px;
}
.ba-col {
  border:1px solid #e2e8f0;
  border-radius:12px;
  padding:14px;
  background:#f8fafc;
}
.ba-col h4 {
  margin:0 0 10px 0;
  font-size:14px;
  letter-spacing:0.10em;
  text-transform:uppercase;
  opacity:0.8;
}
.kv {
  display:flex;
  justify-content:space-between;
  gap:12px;
  padding:8px 0;
  border-bottom:1px solid #e2e8f0;
  font-size:16px;
}
.kv:last-child { border-bottom:none; }
.kv b { font-weight:950; }
.good { color:#16a34a !important; font-weight:950; }
.bad  { color:#dc2626 !important; font-weight:950; }
.warn { color:#b45309 !important; font-weight:950; }
</style>
"""
    css = css.replace("{{BASE_FONT_PX}}", str(base_font_px))
    css = css.replace("{{TAPE_SECONDS}}", str(int(tape_seconds)))
    md(css)


# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------

st.title("SYMBIOSIS")
st.caption("AI Consent + Risk Gate — Storyboarded Real-Time System Simulation")


# ------------------------------------------------------------
# SIDEBAR CONTROLS
# ------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="smallcap">Controls</div>', unsafe_allow_html=True)

    persona = st.selectbox(
        "Persona",
        ["Risk Averse", "Balanced", "Rebellious", "Privacy Maximalist"],
        index=0,
    )

    segment = st.selectbox("Account Segment", SEGMENTS, index=0, help="Switch between Corporate, Business, and Personal card populations.")
    geo_scope = st.selectbox("Geo Scope", GEO_SCOPES, index=0, help="Global / US / Region rollups for the simulated feed.")

    continent_focus = None
    if geo_scope == "Continent":
        continent_focus = st.selectbox(
            "Continent",
            [c[0] for c in CONTINENTS],
            index=0,
            help="Roll up activity by continent. Narrower scope = calmer signals.",
        )

    channels = st.multiselect("Channels", CHANNELS, default=["POS", "ECOM"], help="Show POS, ECOM, or both.")

    sensitivity = st.slider("Privacy Sensitivity", 0, 100, 70)
    urgency = st.slider("Brand Urgency", 0, 100, 60)

    mode = st.selectbox("Mode", ["Simulation (seeded)", "Realtime (jitter)"], index=0)
    seed = st.number_input("Seed (deterministic)", min_value=0, max_value=999999, value=1337, step=1)
    reroll = st.checkbox(
        "Reroll each run",
        value=("Realtime" in mode),
        help="OFF = deterministic (same seed → same run). ON = new scenario each click (seed auto-jitter).",
    )
    # Persist key controls in session_state so downstream sections never see NameError
    st.session_state.mode = mode
    st.session_state.seed = int(seed)
    st.session_state.reroll = bool(reroll)

    st.markdown("<div class='rule'></div>", unsafe_allow_html=True)
    st.markdown("<div class='smallcap'>Incident / Routing</div>", unsafe_allow_html=True)

    override_enabled = st.checkbox(
        "Manual override (routing)",
        value=False,
        help="For demos: force live/fallback route to prove incident controls and auditability.",
    )
    override_route = st.selectbox(
        "Override route",
        ["auto", "live", "fallback"],
        index=0,
        disabled=not override_enabled,
        help="auto = policy engine decides. live = primary path. fallback = degraded-safe path.",
    )

    st.session_state.override_enabled = bool(override_enabled)
    st.session_state.override_route = str(override_route)

    speed = st.slider("Playback speed", 1, 10, 6, help="Higher = faster")
    ui_font = st.slider("UI font size", 16, 30, 22, help="Bigger = readable on laptops + phones.")
    exec_mode = st.checkbox(
        "Executive Mode",
        value=False,
        help="One-click board view: collapses operator detail and emphasizes KPIs, deltas, and incident posture.",
    )
    st.session_state.exec_mode = bool(exec_mode)
    st.markdown(f"<div class='smallcap'>Seed shown: <b>{seed}</b></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='smallcap'>Executive mode: <b>{'ON' if st.session_state.get('exec_mode', False) else 'OFF'}</b></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='rule'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        run = st.button("Run Handshake", key="run_handshake_btn")
    with col_b:
        stop = st.button("Stop", key="stop_btn")


# ------------------------------------------------------------
# BRAND HEADER BAR (needs sidebar vars: mode/seed/reroll)
# ------------------------------------------------------------

#
# Pull from session_state (prevents NameError if this block ever executes before sidebar)
_mode = st.session_state.get("mode", "Simulation (seeded)")
_seed = int(st.session_state.get("seed", 1337))
_reroll = bool(st.session_state.get("reroll", False))

_seed_locked = ("Simulation" in _mode) and (not _reroll)
_seed_badge = "SEED LOCK" if _seed_locked else "SEED JITTER"
_seed_dot = "#16a34a" if _seed_locked else "#f59e0b"

md(
    f"""
<div class=\"brandbar\">
  <div class=\"brand-left\">
    <div class=\"amex-badge\">AMEX</div>
    <div>
      <p class=\"brand-title\">AmEx TrustGate™</p>
      <p class=\"brand-sub\">American Express | Consent + Risk Orchestration Engine</p>
    </div>
  </div>

  <div style=\"display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:flex-end\">
    <div class=\"role-chip\"><span class=\"dot\" style=\"background:{_seed_dot}\"></span> {_seed_badge} | SEED {_seed}</div>
    <div class=\"role-chip\"><span class=\"dot\"></span> INTERNAL TOOL | RISK + COMPLIANCE</div>
    <div class=\"role-chip\"><span class=\"dot\" style=\"background:#0ea5e9\"></span> EXEC MODE | {'ON' if st.session_state.get('exec_mode', False) else 'OFF'}</div>
  </div>
</div>
""",
)


# Sidebar state/session vars for live runner
if "running" not in st.session_state:
    st.session_state.running = False
if "seed_used" not in st.session_state:
    st.session_state.seed_used = int(seed)
if "tick" not in st.session_state:
    st.session_state.tick = 0
if "series" not in st.session_state:
    st.session_state.series = []
if "txns" not in st.session_state:
    st.session_state.txns = []
if "intent" not in st.session_state:
    st.session_state.intent = None
if "base_state" not in st.session_state:
    st.session_state.base_state = None

if "stop" in locals() and stop:
    st.session_state.running = False

# Additional session-state initializations for slow update cadence
if "last_slow_ts" not in st.session_state:
    st.session_state.last_slow_ts = 0.0
if "slow_interval_s" not in st.session_state:
    st.session_state.slow_interval_s = 10.0

# Persistent render cache for storyboard and KPIs
if "last_render" not in st.session_state:
    st.session_state.last_render = {
        "kpis": {"trust": 52, "risk": 42, "friction": 28, "latency_ms": 120},
        "incoming": {"req_per_s": 0, "intent": "Awaiting intent"},
        "processing": {"ai_load": 0, "slo_ms": 250, "latency_ms": 0, "fallback_used": False},
        "gate": {"allowed": ["device", "budget"], "blocked": ["location", "account_number"], "decision": "DEFER"},
        "negotiate": {
            "stage": "Awaiting request",
            "ask": ["spending_categories", "budget"],
            "counter": ["device"],
            "conditions": ["on-device", "no-retention", "transparency panel"],
        },
        "outcome": {"final": "DEFER", "est_savings": 0, "margin_lift": 0.0, "time_saved_min": 0, "compliance": "PASS"},
        "before_after": {
            "before_trust": 52,
            "before_risk": 78,
            "before_latency": 4200,
            "after_trust": 52,
            "after_risk": 42,
            "after_latency": 120,
            "savings": 42,
        },
    }


if "last_decision" not in st.session_state:
    st.session_state.last_decision = "DEFER"

# Deterministic audit trail / replay log
if "decision_log" not in st.session_state:
    st.session_state.decision_log = []

if "policy_reason" not in st.session_state:
    st.session_state.policy_reason = "—"

# Incident tracking + counterfactuals
if "breach_started_ts" not in st.session_state:
    st.session_state.breach_started_ts = None
if "incident_tier" not in st.session_state:
    st.session_state.incident_tier = "OK"
if "breach_seconds" not in st.session_state:
    st.session_state.breach_seconds = 0


def update_incident_state(latency_ms: int, slo_ms: int, fallback_used: bool) -> None:
    """Maintain SLA breach timer + escalation tier."""
    now = time.time()
    breached = bool(latency_ms > slo_ms) or bool(fallback_used)

    if breached:
        if st.session_state.get("breach_started_ts") is None:
            st.session_state.breach_started_ts = now
        st.session_state.breach_seconds = int(now - float(st.session_state.get("breach_started_ts") or now))
    else:
        st.session_state.breach_started_ts = None
        st.session_state.breach_seconds = 0

    s = int(st.session_state.get("breach_seconds", 0))
    if not breached:
        st.session_state.incident_tier = "OK"
    elif s < 8:
        st.session_state.incident_tier = "WARN"
    elif s < 25:
        st.session_state.incident_tier = "BREACH"
    else:
        st.session_state.incident_tier = "CRITICAL"
if "counterfactual" not in st.session_state:
    st.session_state.counterfactual = {}

# KPI delta memory (for ▲▼ +/- in the bottom ticker)
if "prev_kpis" not in st.session_state:
    st.session_state.prev_kpis = {"trust": None, "risk": None, "friction": None, "latency_ms": None}
if "kpi_deltas" not in st.session_state:
    st.session_state.kpi_deltas = {"trust": 0, "risk": 0, "friction": 0, "latency_ms": 0}
if "kpi_deltas_pct" not in st.session_state:
    st.session_state.kpi_deltas_pct = {"trust": 0.0, "risk": 0.0, "friction": 0.0, "latency_ms": 0.0}


def _pct_delta(curr: int, prev: int) -> float:
    if prev in (None, 0):
        return 0.0
    return ((curr - prev) / float(prev)) * 100.0


def update_kpi_deltas(curr: dict) -> None:
    """Update ▲▼ deltas for KPI tape + exec scanning.

    Stores both absolute and percent deltas in session_state.
    """
    prev = st.session_state.get("prev_kpis", {}) or {}

    out_abs = {}
    out_pct = {}
    for k in ("trust", "risk", "friction", "latency_ms"):
        c = curr.get(k)
        p = prev.get(k)
        if p is None:
            out_abs[k] = 0
            out_pct[k] = 0.0
        else:
            out_abs[k] = int(c) - int(p)
            out_pct[k] = float(_pct_delta(int(c), int(p)))

    st.session_state.kpi_deltas = out_abs
    st.session_state.kpi_deltas_pct = out_pct
    st.session_state.prev_kpis = {k: int(curr.get(k)) for k in ("trust", "risk", "friction", "latency_ms")}


def fmt_kpi_delta(label: str, value: int, d_abs: int, d_pct: float, invert: bool) -> str:
    """Return a compact delta line."""
    good = (d_abs < 0) if invert else (d_abs > 0)
    if d_abs == 0:
        arrow = "&#8226;"  # •
        cls = "delta-flat"
    else:
        arrow = "&#9650;" if good else "&#9660;"  # ▲ ▼
        cls = "delta-up" if good else "delta-down"

    pct_txt = f"{d_pct:+.0f}%" if abs(d_pct) >= 0.5 else "±0%"
    abs_txt = f"({d_abs:+d})"

    return f"<span class='delta {cls}'>{arrow} {label} {pct_txt} {abs_txt}</span>"


# Apply theme after sidebar controls to use chosen font size
# Tape speed should feel like a market crawl, not a runaway train.
_tape_map = {"Global": 26, "Continent": 30, "US": 34, "Region": 38}
_tape_seconds = _tape_map.get(geo_scope, 30)
apply_theme(int(ui_font), tape_seconds=_tape_seconds)



# ------------------------------------------------------------
# SIMULATION PRIMITIVES
# ------------------------------------------------------------

# Streamlit requires widget keys to be unique *within a single run*.
# Some panels can render more than once depending on layout/slots; this helper
# guarantees uniqueness without you having to play whack-a-mole.
if "_sym_key_counter" not in st.session_state:
    st.session_state._sym_key_counter = 0

def _uk(prefix: str) -> str:
    st.session_state._sym_key_counter += 1
    return f"{prefix}_{st.session_state._sym_key_counter}"


# Helper: humanize category labels for UI
def humanize(label: str) -> str:
    """Make machine labels readable for humans."""
    s = (label or "").replace("_", " ").strip()
    # keep acronyms like "AI" intact if they appear
    return " ".join(w.upper() if w.lower() in {"ai", "slo"} else w.capitalize() for w in s.split())


def clamp(v: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, v))


def _delta_str(d: int, invert: bool = False) -> str:
    """Return a compact ▲▼ and +/- string for tickers.

    IMPORTANT:
    - Use HTML entities for arrows to avoid font/glyph issues across browsers/devices.
    - This returns HTML and requires unsafe_allow_html=True where rendered.
    """
    if d is None:
        return ""

    # invert means lower is better (risk, friction, latency)
    good = (d < 0) if invert else (d > 0)

    # Always show an explicit +/- value (baseline delta)
    if d == 0:
        arrow = "&#8226;"   # •
        val = "±0"
        cls = "delta-flat"
    else:
        # Use entities so arrows render reliably everywhere
        arrow = "&#9650;" if good else "&#9660;"  # ▲ / ▼
        val = f"{d:+d}"  # includes + or -
        cls = "delta-up" if good else "delta-down"

    # Return HTML so the ticker can color the deltas.
    return f"<span class='delta {cls}'>{arrow} {val}</span>"


def _kpi_ticker_head(trust: int, risk: int, friction: int, latency_ms: int) -> str:
    d = st.session_state.get("kpi_deltas", {"trust": 0, "risk": 0, "friction": 0, "latency_ms": 0})
    # trust: higher is better; risk/friction/latency: lower is better
    return (
        f"TRUST {trust} {_delta_str(int(d.get('trust', 0)), invert=False)}"
        f"  |  RISK {risk} {_delta_str(int(d.get('risk', 0)), invert=True)}"
        f"  |  FRIC {friction} {_delta_str(int(d.get('friction', 0)), invert=True)}"
        f"  |  LAT {latency_ms}ms {_delta_str(int(d.get('latency_ms', 0)), invert=True)}"
    )


def persona_bias(persona_name: str) -> dict:
    if persona_name == "Privacy Maximalist":
        return {"risk": +10, "trust": -2, "friction": +6}
    if persona_name == "Risk Averse":
        return {"risk": +6, "trust": -1, "friction": +4}
    if persona_name == "Rebellious":
        return {"risk": +2, "trust": -3, "friction": +8}
    return {"risk": +3, "trust": +0, "friction": +2}


def mk_rng(mode_label: str, seed_value: int) -> random.Random:
    # In realtime mode, we still allow reproducibility if seed is provided,
    # but we add mild jitter derived from the RNG itself.
    rng = random.Random(seed_value)
    return rng


CATEGORIES = [
    ("spending_categories", 28),
    ("budget", 32),
    ("device", 18),
    ("timing_patterns", 44),
    ("merchant_names", 62),
    ("location", 92),
    ("account_number", 100),
]


def category_gate(rng: random.Random, sensitivity: int) -> tuple[list[str], list[str]]:
    """Returns (allowed, blocked) categories based on sensitivity.

    Higher sensitivity blocks more and especially blocks high-sensitivity categories.
    """
    allowed: list[str] = []
    blocked: list[str] = []

    threshold = clamp(78 - int(sensitivity * 0.55), 18, 78)  # sensitivity 0 -> 78, 100 -> 23

    for name, base_sensitivity in CATEGORIES:
        score = base_sensitivity + rng.randint(-8, 8)
        if name in ("account_number",):
            blocked.append(name)
            continue
        # "location" is treated as effectively PII-ish here; default to blocked unless very low sensitivity
        if name == "location" and sensitivity >= 15:
            blocked.append(name)
            continue

        if score <= threshold:
            allowed.append(name)
        else:
            blocked.append(name)

    # Always keep the story readable: if everything got blocked, allow one low-sensitivity category.
    if not allowed:
        allowed.append("device")
        if "device" in blocked:
            blocked.remove("device")

    return allowed, blocked


def decide_outcome(trust: int, risk: int, friction: int, urgency: int) -> str:
    # BLOCK only when risk is truly extreme
    if risk >= 88:
        return "BLOCK"

    # DEFER when the interaction cost is high and the brand isn't urgent
    if friction >= 78 and urgency <= 50:
        return "DEFER"

    # ACCEPT when trust is decent and risk/friction are within bounds
    if trust >= 55 and risk <= 72 and friction <= 75:
        return "ACCEPT"

    # If urgency is high, allow acceptance with slightly higher friction
    if urgency >= 75 and trust >= 52 and risk <= 70 and friction <= 82:
        return "ACCEPT"

    # Default: defer (safer ask or better timing)
    return "DEFER"


def decision_class(decision: str) -> str:
    return {"ACCEPT": "accept", "BLOCK": "block", "DEFER": "defer"}[decision]


def badge(decision: str) -> str:
    cls = {"ACCEPT": "badge-green", "BLOCK": "badge-red", "DEFER": "badge-amber"}[decision]
    return f"<span class='badge {cls}'>{decision}</span>"


# ------------------------------------------------------------
# POLICY ENGINE (tiny but real): routing + reason codes
# ------------------------------------------------------------

class PolicyEngine:
    """Minimal deterministic policy engine for routing + explainability."""

    def route(self, latency_ms: int, slo_ms: int, mode_label: str) -> tuple[str, str, bool]:
        # Rule 01: latency breach => fallback routing
        if latency_ms > slo_ms:
            return ("fallback", "fallback_routing_triggered: latency>SLO", True)
        # Rule 02: realtime mode can still prefer live routing
        if "Realtime" in (mode_label or ""):
            return ("live", "primary_route_ok: realtime", False)
        return ("live", "primary_route_ok: within_SLO", False)

policy_engine = PolicyEngine()

# ------------------------------------------------------------
# TOP KPI ROW
# ------------------------------------------------------------

kpi_slot = st.empty()
chart_slot = st.empty()
decision_slot = st.empty()

results_slot = st.empty()

replay_slot = st.empty()
counterfactual_slot = st.empty()
incident_slot = st.empty()
audit_slot = st.empty()
cluster_slot = st.empty()
topology_slot = st.empty()
trace_slot = st.empty()
mc_slot = st.empty()
evidence_slot = st.empty()

tx_slot = st.empty()
# ------------------------------------------------------------
# REPLAY LOG (last 10 decisions) — auditability for execs/VCs
# ------------------------------------------------------------

def render_replay_log() -> None:
    """Show last 10 routing/decision events with deltas (audit trail)."""
    with replay_slot.container():
        md(
            """
<div class='card'>
  <div class='frame-title'>Replay Log (last 10 decisions)</div>
  <div class='frame-sub'>Deterministic audit trail: timestamped decisions + routing reason codes + deltas.</div>
</div>
"""
        )

        logs = st.session_state.get("decision_log", [])
        if not logs:
            st.caption("No events yet. Click Run Handshake.")
            return

        df = pd.DataFrame(logs).tail(10).copy()
        # Keep it punchy for exec scanning
        cols = [
            "ts",
            "decision",
            "route",
            "reason",
            "trust",
            "risk",
            "friction",
            "latency_ms",
            "d_trust",
            "d_risk",
            "d_friction",
            "d_latency",
        ]
        df = df[[c for c in cols if c in df.columns]]
        st.dataframe(df, width="stretch", hide_index=True)

# ------------------------------------------------------------
# COUNTERFACTUAL OUTCOMES — prove it's an engine, not a dashboard
# ------------------------------------------------------------

def render_counterfactual() -> None:
    """Show counterfactual outcomes that depend on the *actual* routing decisions."""
    with counterfactual_slot.container():
        md(
            """
<div class='card'>
  <div class='frame-title'>Counterfactual Outcomes</div>
  <div class='frame-sub'>What would have happened under alternate routing / incident timelines.</div>
</div>
"""
        )

        cf = st.session_state.get("counterfactual", {}) or {}
        if not cf:
            st.caption("No counterfactuals yet. Click Run Handshake.")
            return

        rows = [
            {
                "scenario": "If fallback had NOT triggered",
                "impact": f"loss = ${cf.get('no_fallback_loss', 0)}",
                "notes": cf.get("no_fallback_note", "—"),
            },
            {
                "scenario": "If latency persisted 30s longer",
                "impact": f"exposure = ${cf.get('latency_30s_exposure', 0)}",
                "notes": cf.get("latency_note", "—"),
            },
        ]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


# ------------------------------------------------------------
# INCIDENT RESPONSE — enterprise-grade feel (SLA, tiering, overrides)
# ------------------------------------------------------------

def render_incident_panel() -> None:
    with incident_slot.container():
        tier = st.session_state.get("incident_tier", "OK")
        breach_s = st.session_state.get("breach_seconds", 0)
        auto_path = st.session_state.get("policy_reason", "—")

        # Cheap, readable tier badge
        if tier == "OK":
            tier_badge = "<span class='badge badge-green'>TIER 0 · OK</span>"
        elif tier == "WARN":
            tier_badge = "<span class='badge badge-amber'>TIER 1 · WARN</span>"
        elif tier == "BREACH":
            tier_badge = "<span class='badge badge-red'>TIER 2 · SLA BREACH</span>"
        else:
            tier_badge = "<span class='badge badge-red'>TIER 3 · CRITICAL</span>"

        override_enabled = bool(st.session_state.get("override_enabled", False))
        override_route = str(st.session_state.get("override_route", "auto"))
        override_txt = f"ON ({override_route})" if override_enabled and override_route != "auto" else "OFF"

        md(
            f"""
<div class='card'>
  <div class='frame-title'>Incident Response</div>
  <div class='frame-sub'>Escalation tiering, SLA breach timer, mitigation selection, and manual override control.</div>
  <div style='height:10px'></div>
  <div style='display:flex;gap:10px;flex-wrap:wrap;align-items:center'>
    {tier_badge}
    <span class='role-chip'><span class='dot'></span> SLA breach timer: <b>{int(breach_s)}s</b></span>
    <span class='role-chip'><span class='dot'></span> Manual override: <b>{html.escape(override_txt)}</b></span>
  </div>
  <div style='height:12px'></div>
  <div class='metric-label'>Auto-mitigation path selected</div>
  <div style='font-size:14px;font-weight:900;opacity:0.9'>{html.escape(str(auto_path))}</div>
  <div style='height:8px'></div>
  <div class='metric-label'>Manual override option</div>
  <div style='font-size:14px;opacity:0.85'>Use the sidebar to force routing for demos. Audit trail captures the override reason code.</div>
</div>
"""
        )


# ------------------------------------------------------------
# STREAMLIT COMPAT: download_button width API changed
# - Newer Streamlit prefers `width="stretch"`
# - Older Streamlit uses `use_container_width=True`
# This wrapper avoids warnings + keeps the demo portable.
# ------------------------------------------------------------

def dl_button(
    label: str,
    data,
    file_name: str,
    mime: str,
    key: str,
    disabled: bool = False,
):
    """Portable download button.

    Uses `width="stretch"` when available; falls back to `use_container_width=True`.
    """
    try:
        return st.download_button(
            label,
            data=data,
            file_name=file_name,
            mime=mime,
            disabled=disabled,
            width="stretch",
            key=key,
        )
    except TypeError:
        # Older Streamlit versions
        return st.download_button(
            label,
            data=data,
            file_name=file_name,
            mime=mime,
            disabled=disabled,
            use_container_width=True,
            key=key,
        )

# ------------------------------------------------------------
# AUDIT EXPORT — JSON snapshot, CSV log, PDF mock
# ------------------------------------------------------------

def _make_pdf_bytes(title: str, lines: list[str]) -> bytes:
    """Create a simple PDF. If reportlab isn't available, return empty bytes."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO

        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        w, h = letter

        y = h - 72
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, y, title)
        y -= 28

        c.setFont("Helvetica", 10)
        for ln in lines:
            if y < 72:
                c.showPage()
                y = h - 72
                c.setFont("Helvetica", 10)
            c.drawString(72, y, ln[:120])
            y -= 14

        c.showPage()
        c.save()
        return buf.getvalue()
    except Exception:
        return b""


def render_audit_exports() -> None:
    with audit_slot.container():
        md(
            """
<div class='card'>
  <div class='frame-title'>Audit Export</div>
  <div class='frame-sub'>Artifacts that make this a product demo: JSON snapshot, CSV decision log, and a board-ready PDF mock.</div>
</div>
"""
        )

        lr = st.session_state.get("last_render", {})
        replay = (st.session_state.get("decision_log", []) or [])[-10:]
        snapshot = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "mode": st.session_state.get("mode"),
            "seed": st.session_state.get("seed"),
            "geo_scope": str(globals().get("geo_scope", "—")),
            "persona": str(globals().get("persona", "—")),
            "kpis": lr.get("kpis", {}),
            "decision": lr.get("outcome", {}),
            "policy_reason": st.session_state.get("policy_reason", "—"),
            "counterfactual": st.session_state.get("counterfactual", {}),
            "incident": {
                "tier": st.session_state.get("incident_tier", "OK"),
                "breach_seconds": int(st.session_state.get("breach_seconds", 0)),
                "override_enabled": bool(st.session_state.get("override_enabled", False)),
                "override_route": str(st.session_state.get("override_route", "auto")),
            },
            "replay_last_10": replay,
        }

        json_bytes = json.dumps(snapshot, indent=2).encode("utf-8")

        # CSV of last 10 decisions
        if replay:
            csv_bytes = pd.DataFrame(replay).to_csv(index=False).encode("utf-8")
        else:
            csv_bytes = b""

        # Board-ready PDF mock (simple)
        lines = [
            f"Mode: {snapshot.get('mode')}",
            f"Seed: {snapshot.get('seed')}",
            f"Geo Scope: {snapshot.get('geo_scope')}",
            f"Persona: {snapshot.get('persona')}",
            "",
            f"KPIs: {snapshot.get('kpis')}",
            f"Decision: {snapshot.get('decision')}",
            f"Policy Reason: {snapshot.get('policy_reason')}",
            "",
            f"Counterfactual: {snapshot.get('counterfactual')}",
            f"Incident: {snapshot.get('incident')}",
        ]
        pdf_bytes = _make_pdf_bytes("SYMBIOSIS · Board Summary (Mock)", lines)

        c1, c2, c3 = st.columns(3)
        with c1:
            dl_button(
                "Download JSON snapshot",
                data=json_bytes,
                file_name="symbiosis_audit_snapshot.json",
                mime="application/json",
                key=_uk("audit_json_snapshot"),
            )
        with c2:
            dl_button(
                "Download CSV (last 10 decisions)",
                data=csv_bytes,
                file_name="symbiosis_replay_last10.csv",
                mime="text/csv",
                disabled=(not bool(csv_bytes)),
                key=_uk("audit_csv_last10"),
            )
        with c3:
            if pdf_bytes:
                dl_button(
                    "Download Board-ready PDF (mock)",
                    data=pdf_bytes,
                    file_name="symbiosis_board_summary_mock.pdf",
                    mime="application/pdf",
                    key=_uk("audit_board_pdf"),
                )
            else:
                # Fallback if reportlab isn't installed
                dl_button(
                    "Download Board-ready summary (txt)",
                    data="\n".join(lines).encode("utf-8"),
                    file_name="symbiosis_board_summary_mock.txt",
                    mime="text/plain",
                    key=_uk("audit_board_txt"),
                )

# ------------------------------------------------------------
# "IMPOSSIBLE" PANELS — architecture proof (not just UI)
# 1) Anomaly clustering (deterministic)
# 2) Service-mesh topology (dynamic route highlighting)
# 3) Explanation trace tree (governance)
# 4) Monte Carlo risk projection (seed-locked)
# + Evidence pack export (PNG/JSON/CSV/PDF/ZIP)
# ------------------------------------------------------------

# Deterministic k-means (tiny, no sklearn)
def _kmeans_2d(points: list[tuple[float, float]], k: int, rng: random.Random, iters: int = 8):
    if not points or k <= 0:
        return [], []
    k = min(k, len(points))
    centers = list(rng.sample(points, k))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    labels = [0] * len(points)
    for _ in range(iters):
        # assign
        for i, p in enumerate(points):
            best = 0
            bestd = dist2(p, centers[0])
            for ci in range(1, k):
                d = dist2(p, centers[ci])
                if d < bestd:
                    bestd = d
                    best = ci
            labels[i] = best

        # recompute
        sums = [[0.0, 0.0, 0] for _ in range(k)]
        for (x, y), lab in zip(points, labels):
            sums[lab][0] += x
            sums[lab][1] += y
            sums[lab][2] += 1
        for ci in range(k):
            if sums[ci][2] == 0:
                centers[ci] = rng.choice(points)
            else:
                centers[ci] = (sums[ci][0] / sums[ci][2], sums[ci][1] / sums[ci][2])

    return centers, labels


def _det_rng(tag: str = "") -> random.Random:
    """Stable RNG for panels: seed-locked when Simulation + no reroll."""
    base_seed = int(st.session_state.get("seed", 1337))
    mode_label = str(st.session_state.get("mode", "Simulation (seeded)"))
    reroll = bool(st.session_state.get("reroll", False))
    locked = ("Simulation" in mode_label) and (not reroll)

    # When locked: use the seed as-is. When not: add a small time jitter.
    if locked:
        s = base_seed
    else:
        s = base_seed + int(time.time() * 1000) % 100000

    # Tag salt so each panel has its own deterministic stream.
    salt = sum(ord(c) for c in (tag or "")) % 10000
    return random.Random(s + salt)


def render_anomaly_cluster() -> None:
    """Clusters by risk + latency + geography + channel, deterministic under seed lock."""
    md(
        """
<div class='card'>
  <div class='frame-title'>Real Anomaly Clustering</div>
  <div class='frame-sub'>Clusters by risk + latency + geography + channel. Reacts to routing. Deterministic under Seed Lock.</div>
</div>
"""
    )

    tx = st.session_state.get("txns", []) or []
    lr = st.session_state.get("last_render", {}) or {}
    kpis = lr.get("kpis", {}) or {}
    latency_ms = int(kpis.get("latency_ms", 180))

    if not tx:
        st.caption("No transactions yet. Run the handshake to generate signal.")
        return

    # Build feature points (risk vs latency) and attach labels for tooltips.
    # Latency per txn is simulated off the current KPI latency with small jitter.
    rng = _det_rng("cluster")

    pts = []
    meta = []
    for e in tx[-260:]:
        r = float(e.get("risk", 0))
        # geography + channel influence (not cosmetic):
        geo = str(e.get("region", "NA"))
        ch = str(e.get("channel", "POS"))
        gmul = 1.10 if geo in ("AS", "EU") else (1.18 if geo in ("AF", "AN") else 1.0)
        cmul = 1.12 if ch == "ECOM" else 1.0
        lat = float(max(10, int((latency_ms * gmul * cmul) + rng.randint(-40, 55))))

        # normalize latency to 0..100 for clustering/plotting
        lat_norm = min(100.0, max(0.0, (lat / 900.0) * 100.0))
        pts.append((r, lat_norm))
        meta.append({
            "risk": int(r),
            "latency_ms": int(lat),
            "latency_norm": float(lat_norm),
            "region": geo,
            "channel": ch,
            "fraud": bool(e.get("fraud", False)),
            "reason": str(e.get("reason", "—")),
        })

    # k selection: small, readable
    k = 4
    centers, labels = _kmeans_2d(pts, k=k, rng=rng, iters=9)

    rows = []
    for (x, y), lab, m in zip(pts, labels, meta):
        rows.append({
            "risk": x,
            "latency_norm": y,
            "cluster": int(lab),
            "region": m["region"],
            "channel": m["channel"],
            "fraud": m["fraud"],
            "reason": m["reason"],
            "latency_ms": m["latency_ms"],
        })

    df = pd.DataFrame(rows)

    # Regime shift label (reacts to routing)
    route = str(lr.get("processing", {}).get("fallback_used", False))
    route_lbl = "FALLBACK" if route == "True" else "LIVE"
    st.caption(f"Regime: {route_lbl} · Points: {len(df)} · Clusters: {k}")

    if alt is not None:
        chart = (
            alt.Chart(df)
            .mark_circle(size=70, opacity=0.72)
            .encode(
                x=alt.X("risk:Q", title="Risk (0-100)", scale=alt.Scale(domain=[0, 100])),
                y=alt.Y("latency_norm:Q", title="Latency (normalized)", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color("cluster:N", title="Cluster"),
                tooltip=[
                    alt.Tooltip("cluster:N"),
                    alt.Tooltip("risk:Q"),
                    alt.Tooltip("latency_ms:Q", title="latency_ms"),
                    alt.Tooltip("region:N"),
                    alt.Tooltip("channel:N"),
                    alt.Tooltip("fraud:N"),
                    alt.Tooltip("reason:N"),
                ],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, width="stretch")
    else:
        st.scatter_chart(df, x="risk", y="latency_norm")


def render_topology_view() -> None:
    """Service mesh style: Edge → Consent → Risk → Policy → Live/Fallback."""
    md(
        """
<div class='card'>
  <div class='frame-title'>Multi-Node System Topology</div>
  <div class='frame-sub'>Service-mesh view. Route highlights shift when fallback triggers or override is forced.</div>
</div>
"""
    )

    lr = st.session_state.get("last_render", {}) or {}
    processing = lr.get("processing", {}) or {}
    fb = bool(processing.get("fallback_used", False))

    override_enabled = bool(st.session_state.get("override_enabled", False))
    override_route = str(st.session_state.get("override_route", "auto"))

    # Determine effective route
    if override_enabled and override_route in ("live", "fallback"):
        eff = override_route
    else:
        eff = "fallback" if fb else "live"

    live_color = "#16a34a"  # green
    fb_color = "#f59e0b"    # amber
    idle = "#94a3b8"        # slate

    live_edge = live_color if eff == "live" else idle
    fb_edge = fb_color if eff == "fallback" else idle

    # Animate ONLY the active route line (cinematic flow)
    live_dash_cls = "route-dash" if eff == "live" else ""
    fb_dash_cls = "route-dash" if eff == "fallback" else ""

    # SVG is reliable, zero external deps.
    svg = f"""
<div class='card' style='padding:12px'>
<svg viewBox='0 0 980 210' width='100%' height='210' style='border-radius:12px'>
  <defs>
    <filter id='glow'>
      <feGaussianBlur stdDeviation='3.2' result='coloredBlur'/>
      <feMerge>
        <feMergeNode in='coloredBlur'/>
        <feMergeNode in='SourceGraphic'/>
      </feMerge>
    </filter>
  </defs>

  <!-- edges -->
  <line x1='80'  y1='105' x2='240' y2='105' stroke='#0f172a' stroke-opacity='0.25' stroke-width='6'/>
  <line x1='260' y1='105' x2='420' y2='105' stroke='#0f172a' stroke-opacity='0.25' stroke-width='6'/>
  <line x1='440' y1='105' x2='600' y2='105' stroke='#0f172a' stroke-opacity='0.25' stroke-width='6'/>

  <line x1='620' y1='105' x2='760' y2='60'  stroke='{live_edge}' stroke-width='8' filter='url(#glow)' class='{live_dash_cls}'/>
  <line x1='620' y1='105' x2='760' y2='150' stroke='{fb_edge}' stroke-width='8' filter='url(#glow)' class='{fb_dash_cls}'/>

  <!-- nodes -->
  <rect x='20'  y='70'  width='120' height='70' rx='14' fill='#ffffff' stroke='#dbe3ea'/>
  <text x='80'  y='110' text-anchor='middle' font-size='14' font-weight='900' fill='#0f172a'>EDGE</text>

  <rect x='200' y='70'  width='120' height='70' rx='14' fill='#ffffff' stroke='#dbe3ea'/>
  <text x='260' y='103' text-anchor='middle' font-size='14' font-weight='900' fill='#0f172a'>CONSENT</text>
  <text x='260' y='122' text-anchor='middle' font-size='11' fill='#475569'>minimize</text>

  <rect x='380' y='70'  width='120' height='70' rx='14' fill='#ffffff' stroke='#dbe3ea'/>
  <text x='440' y='103' text-anchor='middle' font-size='14' font-weight='900' fill='#0f172a'>RISK</text>
  <text x='440' y='122' text-anchor='middle' font-size='11' fill='#475569'>scoring</text>

  <rect x='560' y='70'  width='120' height='70' rx='14' fill='#ffffff' stroke='#dbe3ea'/>
  <text x='620' y='103' text-anchor='middle' font-size='14' font-weight='900' fill='#0f172a'>POLICY</text>
  <text x='620' y='122' text-anchor='middle' font-size='11' fill='#475569'>routing</text>

  <rect x='760' y='25'  width='200' height='70' rx='14' fill='#ffffff' stroke='#dbe3ea'/>
  <text x='860' y='58' text-anchor='middle' font-size='14' font-weight='900' fill='#0f172a'>LIVE MODEL</text>
  <text x='860' y='78' text-anchor='middle' font-size='11' fill='#475569'>primary path</text>

  <rect x='760' y='115' width='200' height='70' rx='14' fill='#ffffff' stroke='#dbe3ea'/>
  <text x='860' y='148' text-anchor='middle' font-size='14' font-weight='900' fill='#0f172a'>FALLBACK</text>
  <text x='860' y='168' text-anchor='middle' font-size='11' fill='#475569'>degraded-safe</text>

  <!-- label -->
  <text x='20' y='18' font-size='12' fill='#475569'>Active route: {html.escape(eff.upper())}</text>
</svg>
</div>
"""
    md(svg)


def _trace_tree() -> dict:
    """Build an explanation trace tree for the current decision."""
    lr = st.session_state.get("last_render", {}) or {}
    k = lr.get("kpis", {}) or {}
    gate = lr.get("gate", {}) or {}
    out = lr.get("outcome", {}) or {}

    return {
        "inputs": {
            "mode": st.session_state.get("mode"),
            "seed": st.session_state.get("seed"),
            "geo_scope": globals().get("geo_scope", "—"),
            "channels": globals().get("channels", []),
            "latency_ms": int(k.get("latency_ms", 0)),
            "trust": int(k.get("trust", 0)),
            "risk": int(k.get("risk", 0)),
            "friction": int(k.get("friction", 0)),
        },
        "rule_fired": str(st.session_state.get("policy_reason", "—")),
        "routing": {
            "override_enabled": bool(st.session_state.get("override_enabled", False)),
            "override_route": str(st.session_state.get("override_route", "auto")),
        },
        "data_minimization": {
            "allowed": gate.get("allowed", []),
            "blocked": gate.get("blocked", []),
        },
        "decision": {
            "final": out.get("final", "DEFER"),
            "compliance": out.get("compliance", "PASS"),
        },
        "business": {
            "est_savings_per_month": int(out.get("est_savings", 0)),
            "margin_lift_pct": float(out.get("margin_lift", 0.0)),
            "time_saved_min": int(out.get("time_saved_min", 0)),
        },
    }


def _render_tree_lines(node, prefix: str = "") -> list[str]:
    lines: list[str] = []
    if isinstance(node, dict):
        for i, (k, v) in enumerate(node.items()):
            last = i == (len(node) - 1)
            elbow = "└─" if last else "├─"
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{elbow} {k}")
                lines.extend(_render_tree_lines(v, prefix + ("   " if last else "│  ")))
            else:
                lines.append(f"{prefix}{elbow} {k}: {v}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            last = i == (len(node) - 1)
            elbow = "└─" if last else "├─"
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{elbow} [item]")
                lines.extend(_render_tree_lines(v, prefix + ("   " if last else "│  ")))
            else:
                lines.append(f"{prefix}{elbow} {v}")
    else:
        lines.append(f"{prefix}{node}")
    return lines


def render_explanation_trace() -> None:
    md(
        """
<div class='card'>
  <div class='frame-title'>AI Explanation Trace Tree</div>
  <div class='frame-sub'>Inputs → rule fired → routing → data minimization gate → outcome → value/compliance. Deterministic + replayable.</div>
</div>
"""
    )

    tree = _trace_tree()
    lines = _render_tree_lines(tree)
    md("<div class='card' style='padding:14px'><pre style='margin:0;white-space:pre-wrap;font-size:12px;line-height:1.35'>" + html.escape("\n".join(lines)) + "</pre></div>")


def render_monte_carlo() -> None:
    """Seeded Monte Carlo showing P50/P90/P99 tail risk."""
    md(
        """
<div class='card'>
  <div class='frame-title'>Monte Carlo Risk Projection</div>
  <div class='frame-sub'>Seed-locked simulation: exposure distribution + P50/P90/P99 tail risk for board reporting.</div>
</div>
"""
    )

    lr = st.session_state.get("last_render", {}) or {}
    k = lr.get("kpis", {}) or {}
    trust = float(k.get("trust", 55))
    risk = float(k.get("risk", 45))
    friction = float(k.get("friction", 30))
    latency_ms = float(k.get("latency_ms", 180))

    rng = _det_rng("mc")

    # Base exposure model: higher risk + higher latency => more exposure.
    # This is a demo model, but it behaves like an actual system dial.
    base = max(0.0, (risk * 1.6) + (latency_ms / 20.0) + (friction * 0.8) - (trust * 0.6))
    base = base * 120.0  # scale to dollars

    n = 700
    sims = []
    for _ in range(n):
        # fat-tailed multiplier (lognormal-ish)
        m = math.exp(rng.gauss(0.0, 0.55))
        # occasional shock when latency is high
        shock = 1.0 + (0.0 if latency_ms < 250 else max(0.0, rng.gauss(0.25, 0.18)))
        sims.append(base * m * shock)

    sims.sort()

    def pct(p):
        if not sims:
            return 0
        idx = int(round((p / 100.0) * (len(sims) - 1)))
        return sims[max(0, min(len(sims) - 1, idx))]

    p50 = pct(50)
    p90 = pct(90)
    p99 = pct(99)

    metrics = pd.DataFrame([
        {"metric": "Base exposure", "value": round(base, 2)},
        {"metric": "P50", "value": round(p50, 2)},
        {"metric": "P90", "value": round(p90, 2)},
        {"metric": "P99", "value": round(p99, 2)},
    ])
    st.dataframe(metrics, width="stretch", hide_index=True)

    # Histogram buckets (board-friendly)
    bins = 18
    lo = sims[0]
    hi = sims[-1]
    if hi <= lo:
        st.caption("Not enough variance yet.")
        return

    step = (hi - lo) / bins
    buckets = [0] * bins
    for v in sims:
        bi = int((v - lo) / step)
        bi = max(0, min(bins - 1, bi))
        buckets[bi] += 1

    hist = pd.DataFrame({
        "bucket": [f"{int(lo + i * step):,}" for i in range(bins)],
        "count": buckets,
    })
    st.bar_chart(hist.set_index("bucket")["count"], width="stretch")


def _make_snapshot_png_bytes() -> bytes:
    """Lightweight PNG snapshot (KPIs + decision). This is a demo artifact."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        lr = st.session_state.get("last_render", {}) or {}
        k = lr.get("kpis", {}) or {}
        out = lr.get("outcome", {}) or {}

        W, H = 1280, 720
        img = Image.new("RGB", (W, H), (246, 249, 252))
        d = ImageDraw.Draw(img)

        # Fonts (fallback safely)
        try:
            f_big = ImageFont.truetype("Arial.ttf", 56)
            f_med = ImageFont.truetype("Arial.ttf", 28)
            f_small = ImageFont.truetype("Arial.ttf", 20)
        except Exception:
            f_big = ImageFont.load_default()
            f_med = ImageFont.load_default()
            f_small = ImageFont.load_default()

        d.rectangle([40, 40, W - 40, H - 40], outline=(219, 227, 234), width=3)
        d.text((70, 70), "SYMBIOSIS · Evidence Snapshot", fill=(15, 23, 42), font=f_big)

        lines = [
            f"Mode: {st.session_state.get('mode')}",
            f"Seed: {st.session_state.get('seed')}",
            f"Trust: {int(k.get('trust', 0))}",
            f"Risk: {int(k.get('risk', 0))}",
            f"Friction: {int(k.get('friction', 0))}",
            f"Latency: {int(k.get('latency_ms', 0))}ms",
            f"Decision: {out.get('final', 'DEFER')} · Compliance: {out.get('compliance', 'PASS')}",
            f"Policy reason: {st.session_state.get('policy_reason', '—')}",
        ]

        y = 170
        for ln in lines:
            d.text((80, y), ln, fill=(71, 85, 105), font=f_med)
            y += 44

        d.text((80, H - 110), "Note: PNG snapshot is a demo artifact (KPIs + decision).", fill=(100, 116, 139), font=f_small)

        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return b""


def render_evidence_pack() -> None:
    md(
        """
<div class='card'>
  <div class='frame-title'>Evidence Pack</div>
  <div class='frame-sub'>Downloadable artifacts: ticker snapshot PNG + JSON + CSV + board-ready PDF mock, bundled into a ZIP.</div>
</div>
"""
    )

    # Reuse existing audit builders
    lr = st.session_state.get("last_render", {})
    replay = (st.session_state.get("decision_log", []) or [])[-10:]

    # JSON snapshot (same schema as audit panel)
    snapshot = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": st.session_state.get("mode"),
        "seed": st.session_state.get("seed"),
        "geo_scope": str(globals().get("geo_scope", "—")),
        "persona": str(globals().get("persona", "—")),
        "kpis": (lr or {}).get("kpis", {}),
        "decision": (lr or {}).get("outcome", {}),
        "policy_reason": st.session_state.get("policy_reason", "—"),
        "counterfactual": st.session_state.get("counterfactual", {}),
        "incident": {
            "tier": st.session_state.get("incident_tier", "OK"),
            "breach_seconds": int(st.session_state.get("breach_seconds", 0)),
            "override_enabled": bool(st.session_state.get("override_enabled", False)),
            "override_route": str(st.session_state.get("override_route", "auto")),
        },
        "replay_last_10": replay,
    }
    json_bytes = json.dumps(snapshot, indent=2).encode("utf-8")

    # CSV
    csv_bytes = pd.DataFrame(replay).to_csv(index=False).encode("utf-8") if replay else b""

    # PDF mock
    lines = [
        f"Mode: {snapshot.get('mode')}",
        f"Seed: {snapshot.get('seed')}",
        f"Geo Scope: {snapshot.get('geo_scope')}",
        f"Persona: {snapshot.get('persona')}",
        "",
        f"KPIs: {snapshot.get('kpis')}",
        f"Decision: {snapshot.get('decision')}",
        f"Policy Reason: {snapshot.get('policy_reason')}",
        "",
        f"Counterfactual: {snapshot.get('counterfactual')}",
        f"Incident: {snapshot.get('incident')}",
    ]
    pdf_bytes = _make_pdf_bytes("SYMBIOSIS · Board Summary (Mock)", lines)

    png_bytes = _make_snapshot_png_bytes()

    # ZIP bundle
    import io, zipfile

    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("symbiosis_audit_snapshot.json", json_bytes)
        if csv_bytes:
            z.writestr("symbiosis_replay_last10.csv", csv_bytes)
        if pdf_bytes:
            z.writestr("symbiosis_board_summary_mock.pdf", pdf_bytes)
        else:
            z.writestr(
                "symbiosis_board_summary_mock.txt",
                "\n".join(lines).encode("utf-8"),
            )
        if png_bytes:
            z.writestr("symbiosis_snapshot.png", png_bytes)
    zip_bytes = zbuf.getvalue()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        dl_button(
            "Ticker snapshot (PNG)",
            data=png_bytes if png_bytes else b"",
            file_name="symbiosis_snapshot.png",
            mime="image/png",
            disabled=(not bool(png_bytes)),
            key=_uk("evidence_png"),
        )
    with c2:
        dl_button(
            "JSON snapshot",
            data=json_bytes,
            file_name="symbiosis_audit_snapshot.json",
            mime="application/json",
            key=_uk("evidence_json"),
        )
    with c3:
        dl_button(
            "CSV log (last 10)",
            data=csv_bytes,
            file_name="symbiosis_replay_last10.csv",
            mime="text/csv",
            disabled=(not bool(csv_bytes)),
            key=_uk("evidence_csv_last10"),
        )
    with c4:
        dl_button(
            "Evidence Pack (ZIP)",
            data=zip_bytes,
            file_name="symbiosis_evidence_pack.zip",
            mime="application/zip",
            key=_uk("evidence_zip"),
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    with st.expander("Share / Mobile Export Guidance"):
        st.markdown(
            """
**Mobile (iOS / Android):**
1. Tap **Evidence Pack (ZIP)**.
2. Choose **Open in Files** or **Save to Downloads**.
3. Forward via email, Slack, or attach inside Acrobat.

**Desktop:**
1. Download ZIP.
2. Extract locally.
3. Attach JSON / PDF / PNG to board email or compliance archive.

Artifacts included:
- PNG Snapshot (exec visual)
- JSON audit schema
- CSV replay (last 10 decisions)
- Board-ready PDF mock
"""
        )


# ------------------------------------------------------------
# SAFE RENDER (prevents blank expanders if one panel throws)
# ------------------------------------------------------------

def safe_render(label: str, fn) -> None:
    """Render a panel safely.

    Streamlit can sometimes fail inside containers/expanders and leave a blank body.
    This wrapper ensures we surface the error instead of silently collapsing.
    """
    try:
        fn()
    except Exception as e:
        st.error(f"Panel failed: {label}")
        try:
            st.exception(e)
        except Exception:
            st.write(str(e))

# ------------------------------------------------------------
# BEFORE / AFTER BUSINESS COMPARISON

def render_architecture_stack() -> None:
    exec_mode = bool(st.session_state.get("exec_mode", False))

    # If we have never run the handshake, keep panels visible but lightweight.
    has_signal = bool(st.session_state.get("decision_log")) or bool(st.session_state.get("txns"))

    # Executive: show the big story blocks first.
    if exec_mode:
        md("<div class='smallcap'>Executive Stack</div>")

        with st.expander("System Topology (Service Mesh)", expanded=True):
            safe_render("System Topology (Service Mesh)", render_topology_view)

        with st.expander("Explanation Trace Tree (Governance)", expanded=True):
            safe_render("Explanation Trace Tree (Governance)", render_explanation_trace)

        with st.expander("Monte Carlo Projection (Board Risk)", expanded=True):
            safe_render("Monte Carlo Projection (Board Risk)", render_monte_carlo)

        with st.expander("Evidence Pack (PNG / JSON / CSV / PDF / ZIP)", expanded=False):
            safe_render("Evidence Pack (PNG / JSON / CSV / PDF / ZIP)", render_evidence_pack)

        with st.expander("Anomaly Clustering (Deterministic)", expanded=False):
            if has_signal:
                safe_render("Anomaly Clustering (Deterministic)", render_anomaly_cluster)
            else:
                st.caption("Run Handshake to generate clustering signal.")

        return

    # Operator / Builder mode: collapse by default, but keep available.
    md("<div class='smallcap'>System Stack</div>")

    with st.expander("System Topology (Service Mesh)", expanded=True):
        safe_render("System Topology (Service Mesh)", render_topology_view)

    with st.expander("Anomaly Clustering (Deterministic)", expanded=False):
        if has_signal:
            safe_render("Anomaly Clustering (Deterministic)", render_anomaly_cluster)
        else:
            st.caption("Run Handshake to generate clustering signal.")

    with st.expander("Explanation Trace Tree (Governance)", expanded=False):
        safe_render("Explanation Trace Tree (Governance)", render_explanation_trace)

    with st.expander("Monte Carlo Projection (Board Risk)", expanded=False):
        safe_render("Monte Carlo Projection (Board Risk)", render_monte_carlo)

    with st.expander("Evidence Pack (PNG / JSON / CSV / PDF / ZIP)", expanded=False):
        safe_render("Evidence Pack (PNG / JSON / CSV / PDF / ZIP)", render_evidence_pack)


# Render the architecture stack on every run so panels don't appear blank.
render_architecture_stack()

# ------------------------------------------------------------
# BEFORE / AFTER BUSINESS COMPARISON (Executive clarity)
# ------------------------------------------------------------

before_after_slot = st.empty()

def render_before_after(
    before_trust: int,
    before_risk: int,
    before_latency: int,
    after_trust: int,
    after_risk: int,
    after_latency: int,
    savings: int,
):
    with before_after_slot.container():
        html = f"""<div class=\"ba-wrap\">\
<div class=\"ba-card\">\
  <div class=\"ba-head\">\
    <div>\
      <p class=\"ba-h\">Before vs After — TrustGate™ Impact</p>\
      <p class=\"ba-kicker\">What changes when consent + risk are automated inside AmEx.</p>\
    </div>\
    <div class=\"role-chip\"><span class=\"dot\"></span> RISK REDUCTION | LIABILITY SHIELD</div>\
  </div>\
\
  <div class=\"ba-grid\">\
    <div class=\"ba-col\">\
      <h4>Before | Manual + Fragmented</h4>\
      <div class=\"kv\"><span>Trust</span><b>{before_trust}</b></div>\
      <div class=\"kv\"><span>Privacy Risk</span><b class=\"bad\">{before_risk}</b></div>\
      <div class=\"kv\"><span>Latency</span><b class=\"bad\">{before_latency}ms</b></div>\
      <div class=\"kv\"><span>Manual Reviews</span><b class=\"warn\">HIGH</b></div>\
      <div class=\"kv\"><span>Data Exposure</span><b class=\"bad\">BROAD</b></div>\
    </div>\
\
    <div class=\"ba-col\">\
      <h4>After | TrustGate™ Automated</h4>\
      <div class=\"kv\"><span>Trust</span><b class=\"good\">{after_trust}</b></div>\
      <div class=\"kv\"><span>Privacy Risk</span><b class=\"warn\">{after_risk}</b></div>\
      <div class=\"kv\"><span>Latency</span><b class=\"good\">{after_latency}ms</b></div>\
      <div class=\"kv\"><span>Manual Reviews</span><b class=\"good\">LOW</b></div>\
      <div class=\"kv\"><span>Est. Savings</span><b class=\"good\">${savings}/mo</b></div>\
    </div>\
  </div>\
</div>\
</div>"""
        md(html)


# ------------------------------------------------------------
# EXEC PANELS (KPI + Fraud rollup + Before/After) — client-side animation
# ------------------------------------------------------------

def render_exec_panels_animated(
    trust: int,
    risk: int,
    friction: int,
    latency_ms: int,
    before_trust: int,
    before_risk: int,
    before_latency: int,
    after_trust: int,
    after_risk: int,
    after_latency: int,
    savings: int,
    scope: str,
    speed_slider: int,
) -> None:
    """Render KPI row + fraud rollup + before/after with client-side animation.

    Critical: DO NOT use f-strings inside the <script> block (JS uses `{}` too).
    We build a plain template and .replace() tokens to avoid Python parsing JS.
    """

    interval_ms, vol = _live_params(scope, speed_slider)
    # Exec panels should feel live but calmer than the ticker view.
    interval_ms = int(max(120, interval_ms * 2))  # ~half speed of ticker

    # Remount only when scope/speed changes.
    block_id = f"tg_exec_{scope.lower()}_{int(speed_slider)}"

    tpl = r"""
<div id="__BID___wrap" style="width:100%">
  <!-- KPI ROW -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px">
    <div class="card" style="padding:16px">
      <div class="metric-label">Trust</div>
      <div style="height:10px;background:#e2e8f0;border-radius:999px;margin-top:8px">
        <div id="__BID___trust_bar" style="width:__TRUST__%;height:10px;background:#16a34a;border-radius:999px;transition:width 260ms linear"></div>
      </div>
      <div id="__BID___trust_num" style="font-size:26px;font-weight:900;margin-top:6px">__TRUST_N__</div>
    </div>

    <div class="card" style="padding:16px">
      <div class="metric-label">Privacy Risk</div>
      <div style="height:10px;background:#e2e8f0;border-radius:999px;margin-top:8px">
        <div id="__BID___risk_bar" style="width:__RISK__%;height:10px;background:#dc2626;border-radius:999px;transition:width 260ms linear"></div>
      </div>
      <div id="__BID___risk_num" style="font-size:26px;font-weight:900;margin-top:6px">__RISK_N__</div>
    </div>

    <div class="card" style="padding:16px">
      <div class="metric-label">Friction</div>
      <div style="height:10px;background:#e2e8f0;border-radius:999px;margin-top:8px">
        <div id="__BID___fric_bar" style="width:__FRIC__%;height:10px;background:#f59e0b;border-radius:999px;transition:width 260ms linear"></div>
      </div>
      <div id="__BID___fric_num" style="font-size:26px;font-weight:900;margin-top:6px">__FRIC_N__</div>
    </div>

    <div class="card" style="padding:16px">
      <div class="metric-label">Latency</div>
      <div style="height:10px;background:#e2e8f0;border-radius:999px;margin-top:8px">
        <div id="__BID___lat_bar" style="width:__LATP__%;height:10px;background:#0ea5e9;border-radius:999px;transition:width 260ms linear"></div>
      </div>
      <div id="__BID___lat_num" style="font-size:30px;font-weight:950;margin-top:6px">__LATMS__ms</div>
    </div>
  </div>

  <div style="height:14px"></div>

  <!-- FRAUD ROLLUP (animated bars) -->
  <div class="card" style="padding:18px">
    <div class="frame-sub" style="font-weight:850">Fraud flags by region (simulated)</div>
    <div style="height:10px"></div>
    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;align-items:end;height:180px">
      <div><div id="__BID___bar_AF" style="height:60px;background:#2563eb;border-radius:10px;transition:height 420ms ease"></div><div style="text-align:center;margin-top:8px;font-size:12px;opacity:0.75">AF</div></div>
      <div><div id="__BID___bar_AN" style="height:40px;background:#2563eb;border-radius:10px;transition:height 420ms ease"></div><div style="text-align:center;margin-top:8px;font-size:12px;opacity:0.75">AN</div></div>
      <div><div id="__BID___bar_AS" style="height:120px;background:#2563eb;border-radius:10px;transition:height 420ms ease"></div><div style="text-align:center;margin-top:8px;font-size:12px;opacity:0.75">AS</div></div>
      <div><div id="__BID___bar_AU" style="height:90px;background:#2563eb;border-radius:10px;transition:height 420ms ease"></div><div style="text-align:center;margin-top:8px;font-size:12px;opacity:0.75">AU</div></div>
      <div><div id="__BID___bar_EU" style="height:70px;background:#2563eb;border-radius:10px;transition:height 420ms ease"></div><div style="text-align:center;margin-top:8px;font-size:12px;opacity:0.75">EU</div></div>
      <div><div id="__BID___bar_NA" style="height:80px;background:#2563eb;border-radius:10px;transition:height 420ms ease"></div><div style="text-align:center;margin-top:8px;font-size:12px;opacity:0.75">NA</div></div>
    </div>
  </div>

  <div style="height:14px"></div>

  <!-- BEFORE/AFTER -->
  <div class="ba-wrap">
    <div class="ba-card">
      <div class="ba-head">
        <div>
          <p class="ba-h">Before vs After — TrustGate™ Impact</p>
          <p class="ba-kicker">What changes when consent + risk are automated inside AmEx.</p>
        </div>
        <div class="role-chip"><span class="dot"></span> RISK REDUCTION | LIABILITY SHIELD</div>
      </div>
      <div class="ba-grid">
        <div class="ba-col">
          <h4>Before | Manual + Fragmented</h4>
          <div class="kv"><span>Trust</span><b>__BTR__</b></div>
          <div class="kv"><span>Privacy Risk</span><b class="bad">__BRK__</b></div>
          <div class="kv"><span>Latency</span><b class="bad">__BLT__ms</b></div>
          <div class="kv"><span>Manual Reviews</span><b class="warn">HIGH</b></div>
          <div class="kv"><span>Data Exposure</span><b class="bad">BROAD</b></div>
        </div>
        <div class="ba-col">
          <h4>After | TrustGate™ Automated</h4>
          <div class="kv"><span>Trust</span><b id="__BID___aft_trust" class="good">__ATR__</b></div>
          <div class="kv"><span>Privacy Risk</span><b id="__BID___aft_risk" class="warn">__ARK__</b></div>
          <div class="kv"><span>Latency</span><b id="__BID___aft_lat" class="good">__ALT__ms</b></div>
          <div class="kv"><span>Manual Reviews</span><b class="good">LOW</b></div>
          <div class="kv"><span>Est. Savings</span><b id="__BID___aft_save" class="good">$__SAV__/mo</b></div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
(function() {
  const wrap = document.getElementById("__BID___wrap");
  if (!wrap) return;
  if (wrap.__tg_exec_running) return;
  wrap.__tg_exec_running = true;

  const interval = __INT__;
  const vol = __VOL__;

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function stepToward(v, t, rate) { return v + (t - v) * rate; }

  let trust = __TRUST_N__;
  let risk  = __RISK_N__;
  let fric  = __FRIC_N__;
  let lat   = __LATMS__;

  const T_TRUST = trust;
  const T_RISK  = risk;
  const T_FRIC  = fric;
  const T_LAT   = lat;

  const elTrustBar = document.getElementById("__BID___trust_bar");
  const elRiskBar  = document.getElementById("__BID___risk_bar");
  const elFricBar  = document.getElementById("__BID___fric_bar");
  const elLatBar   = document.getElementById("__BID___lat_bar");

  const elTrustNum = document.getElementById("__BID___trust_num");
  const elRiskNum  = document.getElementById("__BID___risk_num");
  const elFricNum  = document.getElementById("__BID___fric_num");
  const elLatNum   = document.getElementById("__BID___lat_num");

  const elAftTrust = document.getElementById("__BID___aft_trust");
  const elAftRisk  = document.getElementById("__BID___aft_risk");
  const elAftLat   = document.getElementById("__BID___aft_lat");
  const elAftSave  = document.getElementById("__BID___aft_save");

  const bars = {
    AF: document.getElementById("__BID___bar_AF"),
    AN: document.getElementById("__BID___bar_AN"),
    AS: document.getElementById("__BID___bar_AS"),
    AU: document.getElementById("__BID___bar_AU"),
    EU: document.getElementById("__BID___bar_EU"),
    NA: document.getElementById("__BID___bar_NA")
  };

  // Fraud bars should feel "alive" but NOT seizure-inducing.
  // Update slowly and ease toward targets.
  let lastFraudUpdate = 0;
  const fraudInterval = 9000; // ~every 9s
  const fraudTargets = {AF: 90, AN: 55, AS: 115, AU: 85, EU: 80, NA: 100};
  const fraudHeights = {AF: 90, AN: 55, AS: 115, AU: 85, EU: 80, NA: 100};

  function reseedFraudTargets() {
    const keys = Object.keys(fraudTargets);
    for (const k of keys) {
      // Keep the variation believable and bounded (no wild flips).
      const base = fraudTargets[k];
      const jitter = (Math.random() - 0.5) * 60; // +/-30
      fraudTargets[k] = clamp(Math.round(base + jitter), 36, 160);
    }
  }

  function easeFraudBars() {
    const keys = Object.keys(bars);
    for (const k of keys) {
      const el = bars[k];
      if (!el) continue;
      fraudHeights[k] = stepToward(fraudHeights[k], fraudTargets[k], 0.22);
      el.style.height = Math.round(fraudHeights[k]) + "px";
    }
  }

  function updateFraudBars(ts) {
    if (ts - lastFraudUpdate < fraudInterval) {
      easeFraudBars();
      return;
    }
    lastFraudUpdate = ts;
    reseedFraudTargets();
    easeFraudBars();
  }

  function tick(ts) {
    const j = (Math.random() - 0.5) * vol * 1.2;

    trust = clamp(stepToward(trust + j, T_TRUST, 0.10), 0, 100);
    risk  = clamp(stepToward(risk  + j, T_RISK,  0.10), 0, 100);
    fric  = clamp(stepToward(fric  + j, T_FRIC,  0.09), 0, 100);

    lat = clamp(stepToward(lat + (Math.random() - 0.5) * vol * 10, T_LAT, 0.10), 10, 900);

    if (elTrustBar) elTrustBar.style.width = Math.round(trust) + "%";
    if (elRiskBar)  elRiskBar.style.width  = Math.round(risk) + "%";
    if (elFricBar)  elFricBar.style.width  = Math.round(fric) + "%";
    if (elLatBar)   elLatBar.style.width   = clamp(Math.round((lat / 250) * 100), 0, 100) + "%";

    if (elTrustNum) elTrustNum.textContent = String(Math.round(trust));
    if (elRiskNum)  elRiskNum.textContent  = String(Math.round(risk));
    if (elFricNum)  elFricNum.textContent  = String(Math.round(fric));
    if (elLatNum)   elLatNum.textContent   = String(Math.round(lat)) + "ms";

    if (elAftTrust) elAftTrust.textContent = String(Math.round(trust));
    if (elAftRisk)  elAftRisk.textContent  = String(Math.round(risk));
    if (elAftLat)   elAftLat.textContent   = String(Math.round(lat)) + "ms";
    if (elAftSave)  elAftSave.textContent  = "$" + String(clamp(Math.round(__SAVN__ + (trust - risk) * 0.15), 0, 999)) + "/mo";

    updateFraudBars(ts);
  }

  tick(0);
  setInterval(function() { tick(performance.now()); }, interval);
})();
</script>
"""

    # Fill tokens safely (no JS brace parsing issues)
    lat_pct = min(100, int((latency_ms / 250) * 100))

    html_block = tpl
    html_block = html_block.replace("__BID__", block_id)
    html_block = html_block.replace("__INT__", str(int(interval_ms)))
    html_block = html_block.replace("__VOL__", str(float(vol)))

    html_block = html_block.replace("__TRUST__", str(max(0, min(100, trust))))
    html_block = html_block.replace("__RISK__", str(max(0, min(100, risk))))
    html_block = html_block.replace("__FRIC__", str(max(0, min(100, friction))))
    html_block = html_block.replace("__LATP__", str(lat_pct))

    html_block = html_block.replace("__TRUST_N__", str(int(trust)))
    html_block = html_block.replace("__RISK_N__", str(int(risk)))
    html_block = html_block.replace("__FRIC_N__", str(int(friction)))
    html_block = html_block.replace("__LATMS__", str(int(latency_ms)))

    html_block = html_block.replace("__BTR__", str(int(before_trust)))
    html_block = html_block.replace("__BRK__", str(int(before_risk)))
    html_block = html_block.replace("__BLT__", str(int(before_latency)))

    html_block = html_block.replace("__ATR__", str(int(after_trust)))
    html_block = html_block.replace("__ARK__", str(int(after_risk)))
    html_block = html_block.replace("__ALT__", str(int(after_latency)))

    html_block = html_block.replace("__SAV__", str(int(savings)))
    html_block = html_block.replace("__SAVN__", str(int(savings)))

    with kpi_slot.container():
        components.html(html_block, height=760, scrolling=False)


def render_kpis(trust: int, risk: int, friction: int, latency_ms: int) -> None:
    with kpi_slot.container():
        cols = st.columns(4)

        with cols[0]:
            gauge("Trust", trust, "#16a34a")

        with cols[1]:
            gauge("Privacy Risk", risk, "#dc2626")

        with cols[2]:
            gauge("Friction", friction, "#f59e0b")

        with cols[3]:
            pct = min(100, int((latency_ms / 250) * 100))
            tier = str(st.session_state.get("incident_tier", "OK"))
            pulse_cls = "breach-pulse" if tier in ("BREACH", "CRITICAL") else ""

            d_abs = int(st.session_state.get("kpi_deltas", {}).get("latency_ms", 0))
            d_pct = float(st.session_state.get("kpi_deltas_pct", {}).get("latency_ms", 0.0))
            delta_line = fmt_kpi_delta("LAT", int(latency_ms), d_abs, d_pct, invert=True)

            md(
                f"""
<div class="card {pulse_cls}" style="padding:16px">
  <div class="metric-label">Latency</div>
  <div style="height:10px;background:#e2e8f0;border-radius:999px;margin-top:8px">
    <div style="width:{pct}%;height:10px;background:#0ea5e9;border-radius:999px"></div>
  </div>
  <div style="font-size:30px;font-weight:950;margin-top:6px">{latency_ms}ms</div>
  <div style="margin-top:6px;font-size:12px;opacity:0.95">{delta_line}</div>
</div>
"""
            )


# ------------------------------------------------------------
# LIVE SIGNALS (Ticker View) — client-side animation (no reruns)
# ------------------------------------------------------------

def _live_params(scope: str, speed_slider: int) -> tuple[int, float]:
    """Return (interval_ms, volatility) for the live chart.

    Broader scope => faster + more volatile.
    Slider increases speed a bit, but we keep it sane.
    """
    base = {
        "Global": (60, 10.0),
        "Continent": (90, 7.0),
        "US": (120, 5.0),
        "Region": (160, 3.5),
    }.get(scope, (110, 6.0))

    interval_ms, vol = base

    # speed slider: 1..10 => modest acceleration (avoid seizure UI)
    accel = max(0.55, 1.05 - (speed_slider * 0.05))
    interval_ms = int(max(40, interval_ms * accel))
    vol = float(vol * (1.0 + (speed_slider - 6) * 0.04))

    return interval_ms, vol


def render_market_chart(df: "pd.DataFrame") -> None:
    """Render the 'Ticker View'.

    IMPORTANT:
    - When running: animate client-side with a Vega timer so ONLY this chart moves.
      No Streamlit reruns, no flashing UI.
    - When stopped: render a static chart from the passed df.
    """
    if st.session_state.get("running", False):
        interval_ms, vol = _live_params(geo_scope, speed)

        # Remount the live canvas only when the parameters change.
        # This avoids accumulating timers on Streamlit reruns.
        canvas_id = f"tg_live_canvas_{geo_scope.lower()}_{int(speed)}"
        window_n = 160  # fixed history window; chart scrolls right->left forever

        # NOTE: This MUST NOT be an f-string.
        # The JS uses template literals like `${t}` which would be interpreted by Python f-strings as `{t}`.
        tpl = r"""
<div class="card">
  <div class="frame-title"><strong>Live Signals (Ticker View)</strong></div>
  <div class="frame-sub">Trust / Risk / Friction drift in real time. Latency spikes trigger fallback routing.</div>
  <div style="height:10px"></div>
  <div id="__CID___wrap" style="width:100%;height:320px;min-height:320px;">
    <canvas id="__CID__" style="width:100%;height:100%;border-radius:12px;"></canvas>
  </div>
</div>

<script>
(function() {
  const wrap = document.getElementById("__CID___wrap");
  const canvas = document.getElementById("__CID__");
  if (!wrap || !canvas) return;

  // Prevent multiple animation loops if Streamlit reruns.
  if (wrap.__tg_running) return;
  wrap.__tg_running = true;

  const ctx = canvas.getContext("2d");

  // Canvas runtime state
  let W = 0, H = 0;
  let hoverIndex = null;
  let freeze = false;

  const N = __N__;
  const interval = __INT__;
  const volatility = __VOL__;

  const padL = 12, padR = 12, padT = 10, padB = 12;

  // Resize canvas to container; keep crisp lines.
  function resize() {
    const rect = wrap.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const w = Math.max(600, Math.floor(rect.width));
    const h = Math.max(240, Math.floor(rect.height));
    W = w;
    H = h;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();

  // Hover inspection (desktop) + click-to-freeze
  canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;

    const usableW = W - padL - padR;
    const step = usableW / (N - 1);

    hoverIndex = Math.round((x - padL) / step);
    hoverIndex = Math.max(0, Math.min(N - 1, hoverIndex));
  });

  canvas.addEventListener("mouseleave", () => {
    hoverIndex = null;
  });

  canvas.addEventListener("click", () => {
    freeze = !freeze; // pin/unpin the current frame
  });

  window.addEventListener("resize", resize);

  let trust = 58, risk = 52, friction = 44;
  let latency = 180;

  const trustArr = Array(N).fill(trust);
  const riskArr  = Array(N).fill(risk);
  const fricArr  = Array(N).fill(friction);
  const latArr   = Array(N).fill(latency);

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function stepToward(v, target, rate) { return v + (target - v) * rate; }

  // Mean reversion targets
  const T_TRUST = 58;
  const T_RISK  = 52;
  const T_FRIC  = 44;
  const T_LAT   = 180;

  function draw() {
    const w = W;
    const h = H;

    ctx.clearRect(0, 0, w, h);

    // Subtle grid (matches graph paper vibe)
    ctx.lineWidth = 1;
    ctx.strokeStyle = "#e2e8f0";
    for (let x = 0; x <= w; x += 56) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y <= h; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    const pw = w - padL - padR;
    const ph = h - padT - padB;
    const xStep = pw / (N - 1);

    function yOf(v) {
      return padT + (1 - (v / 100)) * ph;
    }

    // Latency as an area (normalized 0..100)
    ctx.globalAlpha = 0.22;
    ctx.fillStyle = "#0ea5e9";
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const x = padL + i * xStep;
      const latNorm = clamp((latArr[i] / 900) * 100, 0, 100);
      const y = yOf(latNorm);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.lineTo(padL + (N - 1) * xStep, padT + ph);
    ctx.lineTo(padL, padT + ph);
    ctx.closePath();
    ctx.fill();
    ctx.globalAlpha = 1.0;

    function drawLine(arr, color) {
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let i = 0; i < N; i++) {
        const x = padL + i * xStep;
        const y = yOf(arr[i]);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }

    // Only the ticker view dances.
    drawLine(fricArr, "#2563eb");
    drawLine(riskArr, "#93c5fd");
    drawLine(trustArr, "#dc2626");

    // Axes labels + ticks (keep it readable, not a Bloomberg terminal)
    ctx.fillStyle = "#64748b";
    ctx.font = "11px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial";

    // Y-axis ticks: 0, 25, 50, 75, 100
    const yTicks = [0, 25, 50, 75, 100];
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    for (const v of yTicks) {
      const y = yOf(v);
      // tick mark
      ctx.strokeStyle = "rgba(100, 116, 139, 0.45)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(padL - 5, y);
      ctx.lineTo(padL, y);
      ctx.stroke();
      // label
      ctx.fillText(String(v), 6, y);
    }

    // X-axis labels based on the rolling window duration
    const windowSeconds = Math.max(1, Math.round(((N - 1) * interval) / 1000));
    const midSeconds = Math.max(1, Math.round(windowSeconds / 2));

    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
    ctx.fillText(`-${windowSeconds}s`, padL, h - 4);

    ctx.textAlign = "center";
    ctx.fillText(`-${midSeconds}s`, padL + (pw * 0.5), h - 4);

    ctx.textAlign = "right";
    ctx.fillText("now", padL + pw, h - 4);

    // Hover inspection: crosshair + tooltip (desktop). Click toggles freeze.
    if (hoverIndex !== null) {
      const x = padL + hoverIndex * xStep;

      ctx.save();

      // Crosshair
      ctx.strokeStyle = "rgba(15, 23, 42, 0.25)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, padT);
      ctx.lineTo(x, padT + ph);
      ctx.stroke();

      const t = trustArr[hoverIndex].toFixed(1);
      const r = riskArr[hoverIndex].toFixed(1);
      const f = fricArr[hoverIndex].toFixed(1);
      const l = Math.round(latArr[hoverIndex]);

      const text = `Trust ${t}  |  Risk ${r}  |  Friction ${f}  |  Lat ${l}ms`;

      // Tooltip text style
      ctx.font = "12px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";

      const tw = ctx.measureText(text).width + 16;

      // Tooltip placement (stay inside canvas)
      const tx = Math.min(x + 12, w - tw - 8);
      const ty = padT + 16;

      ctx.fillStyle = "rgba(15, 23, 42, 0.88)";
      ctx.fillRect(tx, ty - 13, tw, 26);

      ctx.fillStyle = "#ffffff";
      ctx.fillText(text, tx + 8, ty);

      // Freeze indicator
      if (freeze) {
        const ft = "FROZEN";
        const fw = ctx.measureText(ft).width + 14;
        ctx.fillStyle = "rgba(220, 38, 38, 0.90)";
        ctx.fillRect(tx, ty + 20, fw, 22);
        ctx.fillStyle = "#ffffff";
        ctx.fillText(ft, tx + 7, ty + 31);
      }

      ctx.restore();
    }
  }

  function tick() {
    // Random walk + mean reversion
    const j = (Math.random() - 0.5) * volatility * 2;

    trust = clamp(stepToward(trust + j, T_TRUST, 0.06), 0, 100);
    risk  = clamp(stepToward(risk  + j, T_RISK,  0.06), 0, 100);
    friction = clamp(stepToward(friction + j, T_FRIC, 0.05), 0, 100);

    latency = clamp(stepToward(latency + (Math.random() - 0.5) * volatility * 18, T_LAT, 0.06), 10, 900);

    // Scroll left; append newest on the right (unless frozen)
    if (!freeze) {
      trustArr.shift(); trustArr.push(trust);
      riskArr.shift();  riskArr.push(risk);
      fricArr.shift();  fricArr.push(friction);
      latArr.shift();   latArr.push(latency);
    }

    draw();
  }

  // Run forever
  draw();
  setInterval(tick, interval);
})();
</script>
"""

        # Remove any remaining backslash-escaped quotes in the HTML attributes
        html_block = tpl.replace('\\"', '"')
        html_block = html_block.replace("__CID__", canvas_id)
        html_block = html_block.replace("__N__", str(int(window_n)))
        html_block = html_block.replace("__INT__", str(int(interval_ms)))
        html_block = html_block.replace("__VOL__", str(float(vol)))

        with chart_slot.container():
            components.html(html_block, height=390, scrolling=False)
        return

    # STOPPED: static chart
    if df is None or df.empty:
        return

    df2 = df.tail(90).copy()

    with chart_slot.container():
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if alt is None:
            md(
                """<div class='card'>
  <div class='frame-title'><strong>Live Signals (Ticker View)</strong></div>
  <div class='frame-sub'>Trust / Risk / Friction drift in real time. Latency spikes trigger fallback routing.</div>
</div>"""
            )
            st.line_chart(df2.set_index("t")[["trust", "risk", "friction"]])
            st.area_chart(df2.set_index("t")[["latency_ms"]])
            return

        base = alt.Chart(df2).transform_fold(["trust", "risk", "friction"], as_=["metric", "value"])
        lines = (
            base.mark_line(strokeWidth=2)
            .encode(
                x=alt.X("t:Q", title="", axis=alt.Axis(ticks=True, labels=True, labelColor="#64748b")),
                y=alt.Y("value:Q", title="", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color("metric:N", title=""),
            )
            .properties(height=240)
        )
        latency = (
            alt.Chart(df2)
            .mark_area(opacity=0.28)
            .encode(
                x=alt.X("t:Q", title="", axis=alt.Axis(ticks=True, labels=True, labelColor="#64748b")),
                y=alt.Y("latency_ms:Q", title="", scale=alt.Scale(zero=True)),
            )
            .properties(height=120)
        )

        md(
            """<div class='card'>
  <div class='frame-title'><strong>Live Signals (Ticker View)</strong></div>
  <div class='frame-sub'>Trust / Risk / Friction drift in real time. Latency spikes trigger fallback routing.</div>
</div>"""
        )
        st.altair_chart(lines, width="stretch")
        st.altair_chart(latency, width="stretch")


# ------------------------------------------------------------
# LIVE TRANSACTION FEED (streaming log)
# ------------------------------------------------------------

def render_tx_feed(tx_df: "pd.DataFrame") -> None:
    """Render a compact, VC-readable live feed + fraud drilldown."""
    if tx_df is None or tx_df.empty:
        return

    with tx_slot.container():
        md(
            """
<div class='card'>
  <div class='frame-title'>Live AmEx Transaction Feed (Simulated)</div>
  <div class='frame-sub'>Global → national → regional rollups. IP drilldown appears only when a transaction is flagged as fraud.</div>
</div>
"""
        )

        # Show last events first
        df_view = tx_df.tail(18).copy().iloc[::-1]

        # Add a simple human-friendly status column
        df_view["status"] = df_view["fraud"].apply(lambda x: "FLAGGED" if x else "OK")

        show_cols = ["segment", "channel", "continent", "region", "country", "transport", "network", "mcc", "amount", "risk", "status", "reason", "ip"]
        df_view = df_view[show_cols]

        st.dataframe(
            df_view,
            use_container_width=True,
            hide_index=True,
        )

        # Tiny rollup: flagged count by region (keeps exec brains awake)
        flagged = tx_df[tx_df["fraud"] == True]
        if not flagged.empty:
            roll = flagged.groupby("region").size().reset_index(name="flagged")
            st.caption("Fraud flags by region (simulated)")
            st.bar_chart(roll.set_index("region")["flagged"])


# ------------------------------------------------------------
# ARCHITECTURE PANELS (always visible)
# ------------------------------------------------------------

st.markdown("<div class='rule'></div>", unsafe_allow_html=True)

# Existing enterprise panels

# "Impossible" panels
with st.expander("Anomaly Clustering — Deep View", expanded=True):
    render_anomaly_cluster()

with st.expander("Service Mesh Topology — Infrastructure View", expanded=True):
    render_topology_view()

with st.expander("AI Explanation Trace — Governance View", expanded=False):
    render_explanation_trace()

with st.expander("Monte Carlo Risk Projection — Board View", expanded=False):
    render_monte_carlo()

with st.expander("Evidence Pack — Export & Audit", expanded=False):
    render_evidence_pack()


# ------------------------------------------------------------
# STORYBOARD FRAMES (3-column cinematic strip)
# ------------------------------------------------------------

st.markdown("<div class='rule'></div>", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)

frame_incoming = f1.empty()
frame_processing = f2.empty()
frame_gate = f3.empty()

# second row frames
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
q1, q2 = st.columns(2)
frame_negotiate = q1.empty()
frame_outcome = q2.empty()


def render_frame_incoming(req_per_s: int, intent: str) -> None:
    frame_incoming.markdown(
        textwrap.dedent(
            f"""
<div class="card">
  <p class="frame-title">Frame 01 — Incoming</p>
  <div class="frame-sub">Brand AI requests attention + permission.</div>
  <div style="height:10px"></div>
  <div class="metric-label">Intent</div>
  <div style="font-size:22px;font-weight:800">{intent}</div>
  <div style="height:14px"></div>
  <div class="metric-label">Request Rate</div>
  <div style="font-size:34px;font-weight:900">{req_per_s}/s</div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_frame_processing(ai_load: int, slo_ms: int, latency_ms: int, fallback_used: bool) -> None:
    reason = st.session_state.get("policy_reason", "—")
    fb = "Fallback routing" if fallback_used else "Live routing"
    frame_processing.markdown(
        textwrap.dedent(
            f"""
<div class="card">
  <p class="frame-title">Frame 02 — Processing</p>
  <div class="frame-sub">System evaluates risk, computes constraints, routes logic.</div>
  <div style="height:10px"></div>
  <div class="metric-label">AI Load</div>
  <div style="font-size:34px;font-weight:900">{ai_load}%</div>
  <div style="height:10px"></div>
  <div class="metric-label">SLO</div>
  <div style="font-size:18px;font-weight:800">{latency_ms}ms / {slo_ms}ms</div>
  <div style="height:12px"></div>
  <div class="metric-label">Route</div>
  <div style="font-size:18px;font-weight:900">{fb}</div>
  <div style="height:6px"></div>
  <div class="metric-label">Reason code</div>
  <div style="font-size:14px;font-weight:850;opacity:0.9">{html.escape(str(reason))}</div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_frame_gate(allowed: list[str], blocked: list[str], decision: str) -> None:
    allowed_txt = ", ".join(humanize(x) for x in allowed[:4]) + ("…" if len(allowed) > 4 else "")
    blocked_txt = ", ".join(humanize(x) for x in blocked[:4]) + ("…" if len(blocked) > 4 else "")

    frame_gate.markdown(
        textwrap.dedent(
            f"""
<div class="card">
  <p class="frame-title">Frame 03 — Gatekeeping</p>
  <div class="frame-sub">Your privacy guard reviews the request and negotiates safer terms.</div>
  <div style="height:10px"></div>
  <div class="metric-label">Allowed</div>
  <div style="font-size:16px;font-weight:750">{allowed_txt}</div>
  <div style="height:10px"></div>
  <div class="metric-label">Blocked</div>
  <div style="font-size:16px;font-weight:750;opacity:0.85">{blocked_txt}</div>
  <div style="height:14px"></div>
  <div>{badge(decision)}</div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


# New storyboard frames: negotiation and outcome/gain

def render_frame_negotiate(stage: str, ask: list[str], counter: list[str], conditions: list[str]) -> None:
    ask_txt = ", ".join(humanize(x) for x in ask) if ask else "—"
    counter_txt = ", ".join(humanize(x) for x in counter) if counter else "—"
    cond_txt = " · ".join(humanize(x) for x in conditions) if conditions else "—"

    frame_negotiate.markdown(
        textwrap.dedent(
            f"""
<div class="card">
  <p class="frame-title">Frame 04 — Negotiation</p>
  <div class="frame-sub">Consent terms are negotiated. Data is minimized.</div>
  <div style="height:10px"></div>
  <div class="metric-label">Stage</div>
  <div style="font-size:18px;font-weight:850">{stage}</div>
  <div style="height:10px"></div>
  <div class="metric-label">Requested</div>
  <div style="font-size:14px;font-weight:750">{ask_txt}</div>
  <div style="height:10px"></div>
  <div class="metric-label">Counteroffer</div>
  <div style="font-size:14px;font-weight:850">{counter_txt}</div>
  <div style="height:10px"></div>
  <div class="metric-label">Conditions</div>
  <div style="font-size:14px;font-weight:750;opacity:0.9">{cond_txt}</div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_frame_outcome(final: str, est_savings: int, margin_lift: float, time_saved_min: int, compliance: str) -> None:
    cls = decision_class(final)
    comp_badge = "<span class='badge badge-green'>PASS</span>" if compliance == "PASS" else "<span class='badge badge-red'>FAIL</span>"

    frame_outcome.markdown(
        textwrap.dedent(
            f"""
<div class="card">
  <p class="frame-title">Frame 05 — Outcome + Gain</p>
  <div class="frame-sub">Decision is executed. Value is realized.</div>
  <div style="height:10px"></div>
  <div class="metric-label">Outcome</div>
  <div style="font-size:40px;font-weight:950" class="{cls}">{final}</div>
  <div style="height:10px"></div>
  <div class="metric-label">Compliance</div>
  <div>{comp_badge}</div>
  <div style="height:14px"></div>
  <div class="metric-label">Estimated Savings</div>
  <div style="font-size:28px;font-weight:950">${est_savings}/mo</div>
  <div style="height:8px"></div>
  <div class="metric-label">Margin Lift</div>
  <div style="font-size:20px;font-weight:900">+{margin_lift:.1f}%</div>
  <div style="height:8px"></div>
  <div class="metric-label">Time Saved</div>
  <div style="font-size:20px;font-weight:900">{time_saved_min} min</div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# RUN HANDSHAKE (continuous)
# ------------------------------------------------------------



def _init_run_state(rng: random.Random):
    st.session_state.tick = 0
    st.session_state.series = []
    st.session_state.txns = []

    trust0 = 52
    risk0 = clamp(18 + int(sensitivity * 0.35))
    friction0 = clamp(22 + int(sensitivity * 0.25))

    b = persona_bias(persona)
    risk0 = clamp(risk0 + b["risk"])
    trust0 = clamp(trust0 + b["trust"])
    friction0 = clamp(friction0 + b["friction"])

    intents = [
        "Find savings leaks without sensitive identifiers",
        "Unlock rewards tiers with minimized data",
        "Debt payoff assist using categories only",
    ]
    st.session_state.intent = rng.choice(intents)
    st.session_state.base_state = {"trust": trust0, "risk": risk0, "friction": friction0}


def _live_factor(scope: str, seg: str, chs: list[str]) -> float:
    # Broader scope => more density => more volatility and faster redraw
    scope_factor = {"Global": 1.0, "Continent": 0.75, "US": 0.55, "Region": 0.35}.get(scope, 0.6)
    seg_factor = {"Corporate": 1.0, "Business": 0.75, "Personal": 0.55}.get(seg, 0.75)
    ch_factor = 1.0 if len(chs) >= 2 else 0.65
    return max(0.25, min(2.3, (scope_factor * 1.25) + (seg_factor * 0.55) + (ch_factor * 0.30)))


def _sleep_seconds(scope: str, speed_slider: int) -> float:
    # FAST loop for the live chart/tape only.
    # Global should feel like a trading desk; Region should feel calmer.
    base_by_scope = {
        "Global": 0.030,
        "Continent": 0.050,
        "US": 0.075,
        "Region": 0.110,
    }
    base = base_by_scope.get(scope, 0.070)

    # Speed slider compresses or expands the delay (higher speed = smaller sleep)
    mult = max(0.25, 1.25 - (speed_slider * 0.10))
    return max(0.012, base * mult)


def _subticks(scope: str) -> int:
    return {
        "Global": 10,
        "Continent": 7,
        "US": 5,
        "Region": 3,
    }.get(scope, 5)


def _continent_ok(txn: dict, focus: str | None) -> bool:
    if geo_scope != "Continent":
        return True
    if not focus:
        return True
    return txn.get("continent") == focus


def _one_frame():
    rng = mk_rng(mode, int(st.session_state.seed_used))

    # advance RNG based on tick so it evolves deterministically (even though Streamlit reruns)
    for _ in range(st.session_state.tick * 9):
        rng.random()

    trust = int(st.session_state.base_state["trust"])
    risk = int(st.session_state.base_state["risk"])
    friction = int(st.session_state.base_state["friction"])

    slo_ms = 250
    initial_ask = ["spending_categories", "budget", "timing_patterns", "merchant_names"]
    intent = st.session_state.intent or "Awaiting intent"

    lf = _live_factor(geo_scope, segment, channels)

    # Slow down EVERYTHING except the live chart + bottom tape.
    # This prevents the UI from flashing like a rave.
    slow_interval_map = {
        "Global": 8.0,
        "Continent": 12.0,
        "US": 16.0,
        "Region": 22.0,
    }
    st.session_state.slow_interval_s = slow_interval_map.get(geo_scope, 12.0)

    now = time.time()
    # IMPORTANT: When the run starts, we must render the "slow" panels at least once,
    # otherwise the app looks like it "disappears" while running.
    slow_update = (st.session_state.tick == 0) or (
        (now - float(st.session_state.last_slow_ts)) >= float(st.session_state.slow_interval_s)
    )
    if (st.session_state.tick == 1) or slow_update:
        st.session_state.last_slow_ts = now

    req_per_s = rng.randint(4, 12) + int(10 * lf)
    ai_load = clamp(38 + rng.randint(-14, 34) + int(20 * lf))
    latency_ms = clamp(35 + rng.randint(-20, 120) + int(55 * lf), 10, 900)

    # Policy-engine routing (with explainable reason code)
    override_enabled = bool(st.session_state.get("override_enabled", False))
    override_route = str(st.session_state.get("override_route", "auto"))

    if override_enabled and override_route in {"live", "fallback"}:
        route_name = override_route
        reason_code = f"manual_override: route={override_route}"
        fallback_used = (override_route == "fallback")
    else:
        route_name, reason_code, fallback_used = policy_engine.route(
            latency_ms=latency_ms, slo_ms=slo_ms, mode_label=mode
        )

    # If policy triggered fallback, apply deterministic mitigation
    if fallback_used:
        latency_ms = clamp(int(latency_ms * 0.65), 10, 900)
        friction = clamp(friction - 2)

    st.session_state.policy_reason = reason_code


    # Fast drift: broader scope => wilder motion
    n = lf
    risk = clamp(int(risk + rng.randint(-14, 14) * n + (52 - risk) * (0.11 * n)))
    trust = clamp(int(trust + rng.randint(-14, 14) * n + (58 - trust) * (0.11 * n)))
    friction = clamp(int(friction + rng.randint(-14, 14) * n + (36 - friction) * (0.09 * n) + int(urgency * 0.012)))

    allowed, blocked = category_gate(rng, sensitivity)
    minimized_ask = [c for c in initial_ask if c in allowed] or [allowed[0]]
    decision = decide_outcome(trust, risk, friction, urgency)
    st.session_state.last_decision = decision

    # Replay log (last 10 decisions): timestamps + deltas + reason codes
    prev = st.session_state.get("last_render", {}).get("kpis", {})
    d_trust = int(trust) - int(prev.get("trust", trust))
    d_risk = int(risk) - int(prev.get("risk", risk))
    d_friction = int(friction) - int(prev.get("friction", friction))
    d_latency = int(latency_ms) - int(prev.get("latency_ms", latency_ms))

    st.session_state.decision_log.append(
        {
            "ts": time.strftime("%H:%M:%S"),
            "decision": decision,
            "route": route_name,
            "reason": st.session_state.get("policy_reason", "—"),
            "trust": int(trust),
            "risk": int(risk),
            "friction": int(friction),
            "latency_ms": int(latency_ms),
            "d_trust": d_trust,
            "d_risk": d_risk,
            "d_friction": d_friction,
            "d_latency": d_latency,
        }
    )
    st.session_state.decision_log = st.session_state.decision_log[-250:]

    # transaction generation is heavy and makes the UI flash.
    # Only refresh the feed on the slow cadence.
    if (st.session_state.tick == 1) or slow_update:
        n_events = rng.randint(int(10 * lf), int(30 * lf))
        for _ne in range(n_events):
            ch = rng.choice([c for c in CHANNELS if c in channels] or ["POS", "ECOM"])
            txn = mk_txn(rng=rng, segment=segment, channel=ch, geo_scope=geo_scope, sensitivity=sensitivity)
            txn["t"] = st.session_state.tick + 1
            if _continent_ok(txn, continent_focus):
                st.session_state.txns.append(txn)

        # cap buffers
        st.session_state.txns = st.session_state.txns[-2500:]

    latency_ms = clamp(int(latency_ms + rng.randint(-45, 110) * lf), 10, 900)

    # ------------------------------------------------------------
    # REAL per-tick KPI deltas for the tape (▲▼ and +/-)
    # These must reflect the actual values *this* tick.
    # ------------------------------------------------------------
    prev_k = st.session_state.get("prev_kpis", {"trust": None, "risk": None, "friction": None, "latency_ms": None})
    if prev_k.get("trust") is None:
        st.session_state.kpi_deltas = {"trust": 0, "risk": 0, "friction": 0, "latency_ms": 0}
    else:
        st.session_state.kpi_deltas = {
            "trust": int(trust) - int(prev_k.get("trust", trust)),
            "risk": int(risk) - int(prev_k.get("risk", risk)),
            "friction": int(friction) - int(prev_k.get("friction", friction)),
            "latency_ms": int(latency_ms) - int(prev_k.get("latency_ms", latency_ms)),
        }
    st.session_state.prev_kpis = {
        "trust": int(trust),
        "risk": int(risk),
        "friction": int(friction),
        "latency_ms": int(latency_ms),
    }

    # ------------------------------------------------------------
    # COUNTERFACTUAL OUTCOMES (deterministic, derived from real tick values)
    # ------------------------------------------------------------
    # Simple, believable business math (not finance cosplay):
    # - Loss proxy grows with latency breach, request rate, and risk
    # - Exposure proxy grows with breach duration
    breach_over = max(0, int(latency_ms) - int(slo_ms))
    per_req_loss = 0.02 + (int(risk) / 5000.0)  # deterministic
    no_fallback_loss = int(breach_over * int(req_per_s) * per_req_loss)

    # If fallback used, show the implied avoided loss as the counterfactual.
    if fallback_used:
        no_fallback_note = "Fallback reduced latency and suppressed exposure. Counterfactual shows avoided loss." 
    else:
        no_fallback_note = "No fallback occurred. Counterfactual shows hypothetical loss if latency had breached without mitigation." 

    # Persisted 30s exposure
    latency_30s_exposure = int((breach_over * 30) * (0.04 + int(risk) / 6000.0))

    st.session_state.counterfactual = {
        "no_fallback_loss": max(0, no_fallback_loss),
        "no_fallback_note": no_fallback_note,
        "latency_30s_exposure": max(0, latency_30s_exposure),
        "latency_note": "Exposure scales with breach-over-SLO and risk posture.",
    }

    # ------------------------------------------------------------
    # INCIDENT STATE (tiering + SLA breach timer)
    # ------------------------------------------------------------
    now_ts = time.time()
    breach = int(latency_ms) > int(slo_ms)
    if breach:
        if st.session_state.breach_started_ts is None:
            st.session_state.breach_started_ts = now_ts
        breach_seconds = int(now_ts - float(st.session_state.breach_started_ts))
    else:
        st.session_state.breach_started_ts = None
        breach_seconds = 0

    st.session_state.breach_seconds = breach_seconds

    # Escalation tiers
    ratio = float(latency_ms) / float(slo_ms)
    if ratio <= 0.90:
        tier = "OK"
    elif ratio <= 1.00:
        tier = "WARN"
    elif ratio <= 1.50:
        tier = "BREACH"
    else:
        tier = "CRITICAL"

    # Risk can bump the tier in extreme cases
    if int(risk) >= 86 and tier in {"WARN", "BREACH"}:
        tier = "CRITICAL"

    st.session_state.incident_tier = tier

    st.session_state.tick += 1
    st.session_state.series.append({"t": st.session_state.tick, "trust": trust, "risk": risk, "friction": friction, "latency_ms": latency_ms})
    st.session_state.series = st.session_state.series[-600:]

    df_series = pd.DataFrame(st.session_state.series)
    df_tx = pd.DataFrame(st.session_state.txns) if st.session_state.txns else pd.DataFrame()

    # FAST: always redraw the live chart (this is the part that should dance).
    render_market_chart(df_series)

    # Update the render cache only on the slow cadence (prevents UI flashing)
    if slow_update:
        # Negotiation/outcome + exec impact calculations
        conditions: list[str] = []
        counteroffer: list[str] = []
        stage = "Consent requested"

        if decision == "ACCEPT":
            stage = "Accepted minimal ask"
            counteroffer = allowed[:3]
            conditions = ["on-device", "no-retention", "one-time consent"]
        elif decision == "DEFER":
            stage = "Counteroffer issued"
            preferred = ["spending_categories", "budget", "device"]
            counteroffer = [c for c in preferred if c in allowed][:2] or [allowed[0]]
            conditions = ["on-device", "no-retention", "transparency panel"]
            trust = clamp(trust - rng.randint(0, 2))
            risk = clamp(risk - rng.randint(3, 8))
            friction = clamp(friction + rng.randint(0, 3))
        else:
            stage = "Blocked"
            counteroffer = ["device"]
            conditions = ["on-device", "no-pii", "aggregate-only"]
            trust = clamp(trust - rng.randint(2, 6))
            friction = clamp(friction + rng.randint(3, 8))

        compliance = "PASS" if ("account_number" not in initial_ask and "location" not in initial_ask) else "FAIL"

        est_savings = max(0, int(20 + (trust * 1.2) - (risk * 0.4) + rng.randint(-5, 12)))
        margin_lift = max(0.0, (trust - friction) * 0.08)
        time_saved_min = max(0, int((trust * 0.6) - (friction * 0.3) + rng.randint(-3, 8)))

        st.session_state.last_render = {
            "kpis": {"trust": trust, "risk": risk, "friction": friction, "latency_ms": latency_ms},
            "incoming": {"req_per_s": req_per_s, "intent": intent},
            "processing": {"ai_load": ai_load, "slo_ms": slo_ms, "latency_ms": latency_ms, "fallback_used": fallback_used, "reason": st.session_state.get("policy_reason", "—")},
            "gate": {"allowed": allowed, "blocked": blocked, "decision": decision},
            "negotiate": {"stage": stage, "ask": minimized_ask, "counter": counteroffer, "conditions": conditions},
            "outcome": {"final": decision, "est_savings": est_savings, "margin_lift": margin_lift, "time_saved_min": time_saved_min, "compliance": compliance},
            "before_after": {
                "before_trust": 52,
                "before_risk": 78,
                "before_latency": 4200,
                "after_trust": trust,
                "after_risk": risk,
                "after_latency": latency_ms,
                "savings": est_savings,
            },
        }

        # Transaction feed updates only on slow cadence
        if not df_tx.empty:
            render_tx_feed(df_tx)

    # Render *static* panels using the cached snapshot.
    # We only refresh the snapshot on `slow_update` to avoid UI flashing.
    lr = st.session_state.last_render

    if slow_update:
        # KPI + fraud rollup + before/after should animate at ~half the ticker speed.
        render_exec_panels_animated(
            trust=lr["kpis"]["trust"],
            risk=lr["kpis"]["risk"],
            friction=lr["kpis"]["friction"],
            latency_ms=lr["kpis"]["latency_ms"],
            before_trust=lr["before_after"]["before_trust"],
            before_risk=lr["before_after"]["before_risk"],
            before_latency=lr["before_after"]["before_latency"],
            after_trust=lr["before_after"]["after_trust"],
            after_risk=lr["before_after"]["after_risk"],
            after_latency=lr["before_after"]["after_latency"],
            savings=lr["before_after"]["savings"],
            scope=geo_scope,
            speed_slider=speed,
        )
        render_frame_incoming(req_per_s=lr["incoming"]["req_per_s"], intent=lr["incoming"]["intent"])
        render_frame_processing(
            ai_load=lr["processing"]["ai_load"],
            slo_ms=lr["processing"]["slo_ms"],
            latency_ms=lr["processing"]["latency_ms"],
            fallback_used=lr["processing"]["fallback_used"],
        )
        render_frame_gate(allowed=lr["gate"]["allowed"], blocked=lr["gate"]["blocked"], decision=lr["gate"]["decision"])
        render_frame_negotiate(
            stage=lr["negotiate"]["stage"],
            ask=lr["negotiate"]["ask"],
            counter=lr["negotiate"]["counter"],
            conditions=lr["negotiate"]["conditions"],
        )
        render_frame_outcome(**lr["outcome"])
        render_replay_log()
        render_counterfactual()
        render_incident_panel()
        render_audit_exports()

        # Bottom tape and transaction feed are also slow-updated.
        if st.session_state.txns:
            df_tx = pd.DataFrame(st.session_state.txns)
            render_tx_feed(df_tx)

        # KPI header with ▲▼ and +/- deltas (finance-tape vibe)
        lr = st.session_state.last_render
        kpi_head = _kpi_ticker_head(
            trust=int(lr["kpis"]["trust"]),
            risk=int(lr["kpis"]["risk"]),
            friction=int(lr["kpis"]["friction"]),
            latency_ms=int(lr["kpis"]["latency_ms"]),
        )

        pos_lane = [kpi_head] + [
            f"{x['country']} ${x['amount']} {x['mcc']} R{x['risk']}"
            for x in st.session_state.txns[-14:]
            if x.get("channel") == "POS"
        ]
        ecom_lane = [kpi_head] + [
            f"{x['country']} ${x['amount']} {x['mcc']} R{x['risk']}"
            for x in st.session_state.txns[-14:]
            if x.get("channel") == "ECOM"
        ]
        fraud_lane = [kpi_head] + [
            f"FLAG {x['country']} ${x['amount']} {x['mcc']} IP {x['ip']} ({x['reason']})"
            for x in st.session_state.txns[-18:]
            if x.get("fraud") is True
        ]

        render_ticker(
            pos_events=(pos_lane[:1] + (pos_lane[-7:] if len(pos_lane) > 7 else pos_lane[1:])) or ["POS — awaiting live feed"],
            ecom_events=(ecom_lane[:1] + (ecom_lane[-7:] if len(ecom_lane) > 7 else ecom_lane[1:])) or ["ECOM — awaiting live feed"],
            fraud_events=(fraud_lane[:1] + (fraud_lane[-7:] if len(fraud_lane) > 7 else fraud_lane[1:])) or ["FRAUD — flags appear here (IP masked)"],
        )

    st.session_state.base_state = {"trust": trust, "risk": risk, "friction": friction}


if run:
    st.session_state.running = True
    # Use persisted values to keep determinism truly deterministic
    _mode = st.session_state.get("mode", mode if "mode" in locals() else "Simulation (seeded)")
    _seed = int(st.session_state.get("seed", seed if "seed" in locals() else 1337))
    _reroll = bool(st.session_state.get("reroll", reroll if "reroll" in locals() else False))

    st.session_state.seed_used = _seed if not _reroll else (int(time.time() * 1000) % 1_000_000)
    rng0 = mk_rng(_mode, int(st.session_state.seed_used))
    _init_run_state(rng0)

if st.session_state.running:
    # Run a single server tick per render. The ticker chart itself animates client-side.
    _one_frame()

    # NOTE:
    # We intentionally do NOT auto-reload the page.
    # The Live Signals chart (canvas) and Exec panels animate client-side (JS) continuously.
    # Auto-reloading fights those JS loops and causes the UI to shrink/flash/disappear.
    # If you want new synthetic scenarios, click "Run Handshake" again (or enable reroll).
else:
    # stopped: show the last captured snapshot (don't wipe the UI)
    if st.session_state.series:
        df_series = pd.DataFrame(st.session_state.series)
        render_market_chart(df_series)
    else:
        demo_df = pd.DataFrame(
            [
                {"t": 1, "trust": 52, "risk": 42, "friction": 28, "latency_ms": 120},
                {"t": 2, "trust": 59, "risk": 48, "friction": 34, "latency_ms": 155},
                {"t": 3, "trust": 54, "risk": 40, "friction": 29, "latency_ms": 110},
            ]
        )
        render_market_chart(demo_df)

    lr = st.session_state.last_render
    render_kpis(**lr["kpis"])
    render_before_after(**lr["before_after"])

    render_frame_incoming(req_per_s=lr["incoming"]["req_per_s"], intent=lr["incoming"]["intent"])
    render_frame_processing(
        ai_load=lr["processing"]["ai_load"],
        slo_ms=lr["processing"]["slo_ms"],
        latency_ms=lr["processing"]["latency_ms"],
        fallback_used=lr["processing"]["fallback_used"],
    )
    render_frame_gate(allowed=lr["gate"]["allowed"], blocked=lr["gate"]["blocked"], decision=lr["gate"]["decision"])
    render_frame_negotiate(
        stage=lr["negotiate"]["stage"],
        ask=lr["negotiate"]["ask"],
        counter=lr["negotiate"]["counter"],
        conditions=lr["negotiate"]["conditions"],
    )
    render_frame_outcome(**lr["outcome"])
    render_replay_log()
    render_counterfactual()
    render_incident_panel()
    render_audit_exports()

    if st.session_state.txns:
        render_tx_feed(pd.DataFrame(st.session_state.txns))

    # Tape should still run visually, even if data isn't updating
    # Even when stopped, show a stable KPI header so the ▲▼ UI is visible in screenshots.
    lr = st.session_state.last_render
    kpi_head = _kpi_ticker_head(
        trust=int(lr["kpis"]["trust"]),
        risk=int(lr["kpis"]["risk"]),
        friction=int(lr["kpis"]["friction"]),
        latency_ms=int(lr["kpis"]["latency_ms"]),
    )
    render_ticker(
        pos_events=[kpi_head, "POS — awaiting live feed"],
        ecom_events=[kpi_head, "ECOM — awaiting live feed"],
        fraud_events=[kpi_head, "FRAUD — flags appear here (IP masked)"],
    )

    md(f"<div class='decision defer'>READY</div>")