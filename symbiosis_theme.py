"""Theme and responsive layout styles for the Symbiosis decision cockpit."""

from __future__ import annotations

import streamlit as st


def inject_theme() -> None:
    """Install the single visual language used by every application surface."""

    st.markdown(
        """
<style>
:root {
  --sym-bg: #0a1422;
  --sym-bg-deep: #050a12;
  --sym-surface: rgba(15, 30, 47, .90);
  --sym-surface-2: rgba(24, 44, 66, .86);
  --sym-line: rgba(170, 194, 218, .16);
  --sym-line-strong: rgba(158, 188, 221, .32);
  --sym-text: #f3f7fb;
  --sym-muted: #93a7bb;
  --sym-dim: #65798e;
  --sym-blue: #5c8dff;
  --sym-green: #42d7a1;
  --sym-amber: #ffbd65;
  --sym-red: #ff777c;
  --sym-purple: #b58cff;
  --sym-shadow: 0 18px 44px rgba(0, 0, 0, .26);
}

html, body, [class*="css"] {
  color: var(--sym-text);
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

div[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 14% -2%, rgba(92, 141, 255, .29), transparent 31rem),
    radial-gradient(circle at 88% 18%, rgba(66, 215, 161, .14), transparent 28rem),
    radial-gradient(circle at 55% 80%, rgba(181, 140, 255, .10), transparent 33rem),
    linear-gradient(160deg, var(--sym-bg) 0%, var(--sym-bg-deep) 100%);
}

div[data-testid="stHeader"] {
  background: transparent;
}

div[data-testid="stToolbar"] { opacity: .55; }

.block-container {
  max-width: 1440px;
  padding: 1.05rem 1.15rem 5.6rem;
}

section[data-testid="stSidebar"],
div[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
div[data-testid="stSidebar"] > div {
  background: #08121d !important;
  border-right: 1px solid var(--sym-line) !important;
}

div[data-testid="stSidebar"] > div:first-child {
  padding-top: 1rem;
}

section[data-testid="stSidebar"] *,
div[data-testid="stSidebar"] * {
  color: var(--sym-text);
}

section[data-testid="stSidebar"] .sym-kicker,
section[data-testid="stSidebar"] .sym-disclosure,
div[data-testid="stSidebar"] .sym-kicker,
div[data-testid="stSidebar"] .sym-disclosure {
  color: var(--sym-muted) !important;
}

h1, h2, h3, h4, p, label, span, div {
  color: inherit;
}

button[kind="secondary"], button[kind="primary"] {
  min-height: 43px;
  border-radius: 12px;
  border: 1px solid var(--sym-line-strong);
  background: rgba(25, 44, 63, .94);
  color: var(--sym-text);
  font-weight: 720;
  transition: transform .16s ease, border-color .16s ease, background .16s ease;
}

button[kind="secondary"]:hover, button[kind="primary"]:hover {
  transform: translateY(-1px);
  border-color: rgba(133, 171, 255, .76);
  background: rgba(35, 59, 82, .98);
}

button[kind="primary"] {
  background: linear-gradient(135deg, #5c8dff 0%, #7e71ff 100%);
  border-color: rgba(151, 179, 255, .82);
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
  background: rgba(22, 40, 58, .94);
  border-color: var(--sym-line-strong);
  color: var(--sym-text);
  border-radius: 11px;
}

div[role="radiogroup"] {
  gap: .35rem;
}

div[role="radiogroup"] label {
  padding: .42rem .2rem;
}

div[data-testid="stMarkdownContainer"] a {
  color: #9dbaff;
}

.sym-disclosure {
  color: var(--sym-muted);
  font-size: .68rem;
  letter-spacing: .105em;
  text-transform: uppercase;
  line-height: 1.35;
}

.sym-kicker {
  color: #a4bcff;
  font-size: .70rem;
  font-weight: 800;
  letter-spacing: .13em;
  text-transform: uppercase;
}

.sym-brand {
  display: flex;
  align-items: center;
  gap: .72rem;
  margin: .2rem 0 .35rem;
}

.sym-logo {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  color: white;
  font-size: 1rem;
  font-weight: 850;
  border-radius: 11px;
  background: linear-gradient(135deg, #6e9bff, #786eff);
  box-shadow: 0 8px 20px rgba(92, 141, 255, .28);
}

.sym-title {
  font-size: clamp(1.6rem, 3vw, 2.55rem);
  font-weight: 820;
  letter-spacing: -.045em;
  line-height: 1.02;
  margin: 0;
  color: var(--sym-text) !important;
}

/* Glance-first live decision layer ------------------------------------------------ */
.sym-compact-header {
  display: flex;
  align-items: center;
  gap: .58rem;
  margin: .72rem 0 .42rem;
}

.sym-compact-mark {
  width: 29px;
  height: 29px;
  display: grid;
  place-items: center;
  flex: 0 0 29px;
  border-radius: 9px;
  color: white;
  background: linear-gradient(145deg, #6d9cff, #716aff);
  font-size: .86rem;
  font-weight: 850;
  box-shadow: 0 6px 18px rgba(92, 141, 255, .34);
}

.sym-compact-title {
  color: #f3f7fb;
  font-size: 1.02rem;
  font-weight: 790;
  letter-spacing: -.03em;
  line-height: 1.05;
}

.sym-compact-title span { color: #9ebcff; font-weight: 720; }

.sym-glance {
  position: relative;
  overflow: hidden;
  margin-top: .62rem;
  border: 1px solid rgba(141, 179, 225, .24);
  border-radius: 22px;
  background:
    linear-gradient(140deg, rgba(22, 48, 78, .92), rgba(10, 22, 38, .94) 46%, rgba(9, 28, 41, .93)),
    var(--sym-surface);
  box-shadow: 0 24px 70px rgba(0, 0, 0, .34), inset 0 1px 0 rgba(255, 255, 255, .035);
}

.sym-glance-status {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .65rem;
  padding: .82rem .92rem 0;
}

.sym-glance-queue {
  color: #b4c5d7;
  font-size: .63rem;
  font-weight: 700;
  letter-spacing: .055em;
  text-align: right;
  text-transform: uppercase;
}

.sym-live-scene {
  position: relative;
  min-height: 258px;
  overflow: hidden;
  isolation: isolate;
}

.sym-live-scene:before,
.sym-live-scene:after {
  content: "";
  position: absolute;
  pointer-events: none;
}

.sym-live-scene:before {
  width: 18rem;
  height: 18rem;
  left: 50%;
  top: 49%;
  z-index: -1;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(73, 136, 255, .22), rgba(60, 95, 166, .08) 42%, transparent 68%);
  filter: blur(3px);
}

.sym-live-scene:after {
  inset: 0;
  z-index: -1;
  opacity: .88;
  background: linear-gradient(90deg, rgba(92, 141, 255, .08), transparent 27%, transparent 72%, rgba(66, 215, 161, .055));
}

.sym-scene-grid {
  position: absolute;
  inset: 0;
  z-index: -1;
  opacity: .45;
  background-image: linear-gradient(rgba(145, 174, 208, .11) 1px, transparent 1px), linear-gradient(90deg, rgba(145, 174, 208, .11) 1px, transparent 1px);
  background-size: 26px 26px;
  mask-image: linear-gradient(to bottom, transparent, #000 22%, #000 78%, transparent);
}

.sym-flow-map {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
}

.sym-flow-base {
  fill: none;
  stroke: rgba(151, 180, 214, .18);
  stroke-width: 1.25;
}

.sym-flow-active {
  fill: none;
  stroke: url(#sym-flow-gradient);
  stroke-width: 2.2;
  stroke-dasharray: 10 10;
  stroke-linecap: round;
  animation: sym-flow-shift 5.5s linear infinite;
}

.sym-flow-node { fill: #6e99ff; stroke: rgba(216, 236, 255, .85); stroke-width: 1; }
.sym-flow-node.n-two { fill: #ffbd65; }
.sym-flow-node.n-three { fill: #42d7a1; }
.sym-flow-packet { fill: #f3fbff; }

.sym-scene-node {
  position: absolute;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: .05rem;
  padding: .42rem .5rem;
  border: 1px solid rgba(164, 195, 228, .2);
  border-radius: 10px;
  background: rgba(5, 17, 30, .58);
  backdrop-filter: blur(7px);
  animation: sym-node-arrive .72s both;
}

.sym-scene-node span { color: #879daf; font-size: .52rem; font-weight: 800; letter-spacing: .105em; }
.sym-scene-node b { color: #eff7ff; font-size: .72rem; letter-spacing: .04em; }
.sym-scene-node-a { top: 25%; left: 7%; }
.sym-scene-node-b { right: 7%; bottom: 27%; animation-delay: .18s; }

.sym-decision-orb {
  position: absolute;
  z-index: 2;
  left: 50%;
  top: 52%;
  width: 148px;
  height: 148px;
  transform: translate(-50%, -50%);
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: radial-gradient(circle at 38% 28%, rgba(176, 207, 255, .26), rgba(26, 53, 91, .94) 48%, rgba(7, 21, 36, .98) 76%);
  box-shadow: 0 0 0 1px rgba(186, 214, 255, .2), 0 0 42px rgba(86, 137, 255, .32), inset 0 0 28px rgba(169, 208, 255, .12);
  animation: sym-orb-arrive .8s cubic-bezier(.2,.9,.2,1) both;
}

.sym-orb-halo {
  position: absolute;
  inset: -19px;
  border: 1px solid rgba(119, 166, 255, .34);
  border-radius: 50%;
  animation: sym-orb-pulse 2.6s ease-out infinite;
}

.sym-confidence-ring {
  position: absolute;
  inset: 9px;
  width: calc(100% - 18px);
  height: calc(100% - 18px);
  transform: rotate(-90deg);
}

.sym-confidence-ring circle { fill: none; stroke-width: 4; }
.sym-ring-track { stroke: rgba(216, 235, 255, .11); }
.sym-ring-value { stroke: var(--world-accent, #5c8dff); stroke-linecap: round; stroke-dasharray: var(--ring-length) 289; animation: sym-ring-reveal .95s .12s both; filter: drop-shadow(0 0 4px rgba(117, 164, 255, .66)); }

.sym-orb-core { position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; gap: .04rem; text-align: center; }
.sym-orb-core span { color: #a7bddd; font-size: .52rem; font-weight: 820; letter-spacing: .12em; }
.sym-orb-core strong { color: white; font-size: 1.82rem; font-weight: 830; letter-spacing: -.07em; line-height: 1; }
.sym-orb-core small { color: #c8d9e9; font-size: .61rem; font-weight: 700; }

.sym-glance-title-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: .8rem;
  padding: .08rem .95rem .78rem;
}

.sym-glance-type { color: #a9c0eb; font-size: .62rem; font-weight: 800; letter-spacing: .105em; text-transform: uppercase; }
.sym-glance-title-row h2 { margin: .22rem 0 0; color: white !important; font-size: clamp(1.28rem, 3.1vw, 1.72rem); line-height: 1.03; letter-spacing: -.045em; }
.sym-glance-value { flex: 0 0 auto; padding-bottom: .08rem; text-align: right; }
.sym-glance-value span { display: block; color: #7f97ae; font-size: .56rem; font-weight: 800; letter-spacing: .09em; }
.sym-glance-value b { display: block; color: #f2f7ff; font-size: 1.1rem; letter-spacing: -.035em; }

.sym-action-signal {
  margin: 0 .82rem;
  padding: .78rem .84rem .82rem;
  border: 1px solid rgba(119, 157, 255, .42);
  border-radius: 15px;
  background: linear-gradient(105deg, rgba(92, 141, 255, .23), rgba(92, 141, 255, .055) 64%, rgba(66, 215, 161, .075));
  animation: sym-action-appear .65s .2s both;
}

.sym-action-label { color: #b4c7ff; font-size: .59rem; font-weight: 830; letter-spacing: .11em; text-transform: uppercase; }
.sym-action-value { margin-top: .18rem; color: #fff; font-size: 1.08rem; font-weight: 800; letter-spacing: -.03em; }
.sym-action-signal p { margin: .22rem 0 0; color: #c0d1e4; font-size: .73rem; line-height: 1.34; }

.sym-glance-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1.4fr;
  gap: 1px;
  margin: .76rem .82rem .68rem;
  overflow: hidden;
  border: 1px solid rgba(157, 186, 218, .16);
  border-radius: 14px;
  background: rgba(157, 186, 218, .13);
}

.sym-glance-metric { position: relative; min-width: 0; min-height: 72px; padding: .58rem .64rem .52rem; overflow: hidden; background: rgba(8, 22, 36, .76); }
.sym-glance-metric b { position: relative; z-index: 1; display: block; overflow: hidden; color: #eef8ff; font-size: .97rem; font-weight: 790; letter-spacing: -.04em; text-overflow: ellipsis; white-space: nowrap; }
.sym-glance-metric span { position: relative; z-index: 1; display: block; margin-top: .1rem; color: #93aabd; font-size: .57rem; font-weight: 760; letter-spacing: .065em; text-transform: uppercase; }
.sym-glance-metric i { position: absolute; left: .62rem; right: .62rem; bottom: .45rem; height: 2px; border-radius: 999px; background: var(--sym-blue); animation: sym-bar-reveal .85s .35s both; transform-origin: left; }
.sym-glance-metric.verified i { background: var(--sym-green); }
.sym-glance-metric.conflict i { background: var(--sym-amber); }
.sym-glance-metric.missing i { background: var(--sym-red); }
.sym-glance-metric.value i { background: linear-gradient(90deg, var(--sym-blue), #a88cff); }

.sym-blocker-strip {
  display: flex;
  align-items: center;
  gap: .42rem;
  min-width: 0;
  padding: 0 .9rem .76rem;
  color: #b6c7d9;
  font-size: .69rem;
}

.sym-blocker-strip strong { flex: 0 0 auto; color: #ffe0ac; font-size: .7rem; }
.sym-blocker-strip > span:nth-child(3) { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sym-blocker-arrow { margin-left: auto; color: #ffcd87; font-size: 1rem; }

.sym-ticker {
  overflow: hidden;
  height: 32px;
  border-top: 1px solid rgba(157, 186, 218, .14);
  background: rgba(3, 12, 21, .42);
}

.sym-ticker-track {
  display: flex;
  width: max-content;
  min-width: 200%;
  align-items: center;
  height: 100%;
  animation: sym-ticker 30s linear infinite;
}

.sym-ticker-track span { padding-right: 2.8rem; color: #92acc4; font-size: .57rem; font-weight: 800; letter-spacing: .105em; white-space: nowrap; }

.sym-scan-head { display: flex; justify-content: space-between; align-items: center; margin: .98rem 0 .48rem; padding: 0 .12rem; }
.sym-scan-head span { color: #dceaff; font-size: .75rem; font-weight: 780; letter-spacing: .01em; }
.sym-scan-head small { color: #8197ad; font-size: .64rem; }

.sym-future-scan-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .48rem; }
.sym-future-scan { position: relative; min-width: 0; min-height: 112px; overflow: hidden; padding: .67rem .67rem .58rem; border: 1px solid rgba(154, 183, 215, .18); border-radius: 14px; background: rgba(9, 23, 37, .68); }
.sym-future-scan.recommended { border-color: rgba(112, 153, 255, .58); background: linear-gradient(145deg, rgba(70, 113, 221, .28), rgba(9, 23, 37, .84)); box-shadow: 0 7px 23px rgba(44, 94, 200, .12); }
.sym-future-scan.hold { background: linear-gradient(145deg, rgba(255, 189, 101, .09), rgba(9, 23, 37, .8)); }
.sym-future-scan-top { display: flex; align-items: center; justify-content: space-between; gap: .2rem; }
.sym-future-scan-top span { color: #a7bacd; font-size: .56rem; font-weight: 820; letter-spacing: .095em; }
.sym-future-scan-top em { color: #cbd9ff; font-size: .49rem; font-style: normal; font-weight: 850; letter-spacing: .08em; }
.sym-future-scan > b { display: block; min-height: 2.25rem; margin-top: .38rem; overflow: hidden; color: #f3f7fb; font-size: .76rem; font-weight: 740; letter-spacing: -.02em; line-height: 1.22; }
.sym-scan-bar { position: absolute; left: .67rem; right: .67rem; bottom: 1.62rem; height: 3px; overflow: hidden; border-radius: 99px; background: rgba(181, 204, 228, .16); }
.sym-scan-bar i { display: block; width: var(--scan); height: 100%; border-radius: inherit; background: #6f9aff; animation: sym-scan-reveal .72s .4s both; transform-origin: left; }
.sym-future-scan.hold .sym-scan-bar i { background: var(--sym-amber); }
.sym-future-scan.authorize .sym-scan-bar i { background: var(--sym-red); }
.sym-future-scan small { position: absolute; bottom: .58rem; color: #8fa5ba; font-size: .56rem; font-weight: 700; }

.sym-glance-footnote { margin: .46rem 0 0; color: #8fa5bb; font-size: .65rem; text-align: center; }
.sym-detail-kicker { padding: .42rem 0; color: #a7b9cd; font-size: .66rem; font-weight: 750; letter-spacing: .075em; text-transform: uppercase; }

.sym-entry { max-width: 590px; margin: 0 auto 1rem; padding: 1.1rem 1rem .25rem; text-align: center; }
.sym-entry-mark { position: relative; display: grid; place-items: center; width: 70px; height: 70px; margin: 0 auto .88rem; border-radius: 50%; color: white; background: radial-gradient(circle at 36% 30%, #9fc1ff, #5c8dff 48%, #4638a2); box-shadow: 0 0 0 12px rgba(92, 141, 255, .07), 0 0 55px rgba(92, 141, 255, .35); font-size: 1.75rem; font-weight: 850; animation: sym-entry-pulse 2.8s ease-in-out infinite; }
.sym-entry-mark i { position: absolute; border: 1px solid rgba(130, 170, 255, .34); border-radius: 50%; animation: sym-entry-ripple 2.8s ease-out infinite; }
.sym-entry-mark i:nth-child(2) { inset: -15px; }
.sym-entry-mark i:nth-child(3) { inset: -29px; animation-delay: .65s; }
.sym-entry-mark i:nth-child(4) { inset: -45px; animation-delay: 1.3s; }
.sym-entry h1 { margin: .26rem 0 .18rem; color: white !important; font-size: clamp(2.3rem, 7vw, 3.8rem); letter-spacing: -.075em; line-height: .98; }
.sym-entry p { margin: 0; color: #c5d4e4; font-size: 1rem; font-weight: 600; }
.sym-entry-signal { display: inline-flex; align-items: center; gap: .4rem; margin-top: 1.15rem; padding: .42rem .62rem; border: 1px solid rgba(156, 187, 220, .18); border-radius: 999px; color: #adc1d5; background: rgba(8, 22, 36, .5); font-size: .63rem; font-weight: 750; letter-spacing: .055em; text-transform: uppercase; }
.sym-entry-note { margin-top: .65rem; color: #8095a9; font-size: .62rem; font-weight: 700; letter-spacing: .075em; text-align: center; text-transform: uppercase; }

@keyframes sym-flow-shift { to { stroke-dashoffset: -126; } }
@keyframes sym-orb-arrive { from { opacity: 0; transform: translate(-50%, -42%) scale(.78); } to { opacity: 1; transform: translate(-50%, -50%) scale(1); } }
@keyframes sym-orb-pulse { 0%, 100% { transform: scale(.88); opacity: .72; } 50% { transform: scale(1.16); opacity: 0; } }
@keyframes sym-ring-reveal { from { opacity: 0; stroke-dashoffset: 289; } to { opacity: 1; stroke-dashoffset: 0; } }
@keyframes sym-node-arrive { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes sym-action-appear { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes sym-bar-reveal { from { transform: scaleX(0); opacity: 0; } to { transform: scaleX(1); opacity: 1; } }
@keyframes sym-ticker { to { transform: translateX(-50%); } }
@keyframes sym-scan-reveal { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes sym-entry-pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.04); } }
@keyframes sym-entry-ripple { 0%, 100% { opacity: 0; transform: scale(.76); } 28% { opacity: .72; } 60% { opacity: 0; transform: scale(1.08); } }

.sym-subtitle {
  color: var(--sym-muted);
  font-size: .92rem;
  line-height: 1.5;
  max-width: 770px;
  margin: .35rem 0 0;
}

.sym-card {
  background: linear-gradient(145deg, rgba(22, 39, 57, .92), rgba(11, 23, 35, .92));
  border: 1px solid var(--sym-line);
  border-radius: 18px;
  box-shadow: var(--sym-shadow);
  overflow: hidden;
  color: var(--sym-text);
}

.sym-card-inner {
  padding: 1.05rem;
}

.sym-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: .8rem;
}

.sym-status {
  display: inline-flex;
  align-items: center;
  gap: .38rem;
  color: #b9c9da;
  font-size: .68rem;
  letter-spacing: .11em;
  text-transform: uppercase;
  font-weight: 800;
}

.sym-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--sym-blue);
  box-shadow: 0 0 0 4px rgba(92, 141, 255, .12);
}

.sym-dot.green { background: var(--sym-green); box-shadow: 0 0 0 4px rgba(66, 215, 161, .12); }
.sym-dot.amber { background: var(--sym-amber); box-shadow: 0 0 0 4px rgba(255, 189, 101, .12); }
.sym-dot.red { background: var(--sym-red); box-shadow: 0 0 0 4px rgba(255, 119, 124, .12); }

.sym-badge {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  padding: .32rem .52rem;
  border-radius: 999px;
  color: #c5d2df;
  border: 1px solid var(--sym-line);
  background: rgba(6, 15, 23, .34);
  font-size: .65rem;
  letter-spacing: .08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.sym-event-name {
  font-size: clamp(1.3rem, 2.6vw, 1.95rem);
  line-height: 1.13;
  letter-spacing: -.035em;
  font-weight: 780;
  margin: .58rem 0 .38rem;
  color: var(--sym-text) !important;
}

.sym-event-context {
  color: var(--sym-muted);
  font-size: .84rem;
  line-height: 1.5;
}

.sym-value-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: .55rem;
  padding-top: .9rem;
  margin-top: .9rem;
  border-top: 1px solid var(--sym-line);
}

.sym-value-cell {
  min-width: 0;
}

.sym-value-label {
  color: var(--sym-dim);
  font-size: .62rem;
  letter-spacing: .09em;
  text-transform: uppercase;
  font-weight: 750;
}

.sym-value {
  margin-top: .25rem;
  font-size: 1.06rem;
  font-weight: 730;
  letter-spacing: -.02em;
  color: var(--sym-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sym-recommendation {
  position: relative;
  padding: 1.1rem;
  background:
    linear-gradient(135deg, rgba(92, 141, 255, .18), rgba(92, 141, 255, .035)),
    rgba(14, 29, 46, .84);
  border: 1px solid rgba(119, 157, 255, .38);
  border-radius: 18px;
  overflow: hidden;
  min-height: 100%;
}

.sym-recommendation:after {
  content: "";
  position: absolute;
  width: 10rem;
  height: 10rem;
  border-radius: 50%;
  right: -4.5rem;
  top: -5rem;
  background: rgba(106, 146, 255, .14);
  filter: blur(8px);
}

.sym-recommendation-title {
  position: relative;
  color: #bdccff;
  font-size: .68rem;
  letter-spacing: .11em;
  text-transform: uppercase;
  font-weight: 800;
}

.sym-recommendation-action {
  position: relative;
  color: #fff;
  font-size: clamp(1.2rem, 2.2vw, 1.7rem);
  letter-spacing: -.03em;
  line-height: 1.13;
  font-weight: 780;
  margin: .48rem 0 .5rem;
}

.sym-recommendation-copy {
  position: relative;
  color: #c9d6e5;
  font-size: .84rem;
  line-height: 1.47;
}

.sym-confidence {
  position: relative;
  display: flex;
  gap: .45rem;
  align-items: baseline;
  margin-top: .9rem;
}

.sym-confidence strong {
  font-size: 1.45rem;
  letter-spacing: -.04em;
}

.sym-confidence span {
  color: #bac8d8;
  font-size: .74rem;
}

.sym-global {
  display: grid;
  grid-template-columns: 1.4fr .9fr;
  gap: .75rem;
  padding: .74rem .9rem;
  margin: .85rem 0 1rem;
  border: 1px solid var(--sym-line);
  background: rgba(9, 20, 31, .75);
  border-radius: 15px;
}

.sym-global-world {
  min-width: 0;
}

.sym-global-world strong {
  display: block;
  font-size: .79rem;
  letter-spacing: .065em;
  text-transform: uppercase;
}

.sym-global-world span {
  color: var(--sym-muted);
  display: block;
  margin-top: .14rem;
  font-size: .73rem;
}

.sym-global-metrics {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-wrap: wrap;
  gap: .5rem 1rem;
}

.sym-global-metric {
  color: #d5e2ee;
  font-size: .72rem;
}

.sym-global-metric b {
  display: block;
  color: white;
  font-size: .98rem;
  letter-spacing: -.02em;
}

.sym-region-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: .55rem;
  margin: .8rem 0 1.05rem;
}

.sym-region {
  position: relative;
  padding: .72rem;
  min-width: 0;
  border-radius: 14px;
  border: 1px solid var(--sym-line);
  background: rgba(10, 23, 35, .64);
  overflow: hidden;
}

.sym-region:after {
  content: "";
  position: absolute;
  inset: auto 0 0;
  height: 2px;
  background: linear-gradient(90deg, var(--sym-blue), transparent);
  opacity: var(--pulse-opacity, .3);
}

.sym-region-head {
  color: var(--sym-muted);
  font-size: .64rem;
  letter-spacing: .10em;
  text-transform: uppercase;
  font-weight: 760;
}

.sym-region-time {
  margin-top: .28rem;
  color: #eff6ff;
  font-size: 1.05rem;
  font-weight: 740;
  letter-spacing: -.025em;
}

.sym-region-state {
  margin-top: .26rem;
  color: var(--sym-green);
  font-size: .66rem;
  font-weight: 720;
}

.sym-region-state.watch { color: var(--sym-amber); }

.sym-section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: .8rem;
  margin: 1.18rem 0 .66rem;
}

.sym-section-title {
  font-size: 1.02rem;
  letter-spacing: -.018em;
  font-weight: 730;
  color: var(--sym-text);
}

.sym-section-note {
  color: var(--sym-muted);
  font-size: .72rem;
  text-align: right;
}

.sym-evidence-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: .58rem;
}

.sym-evidence {
  border: 1px solid var(--sym-line);
  background: rgba(12, 27, 40, .64);
  border-radius: 14px;
  padding: .82rem;
}

.sym-evidence-top {
  display: flex;
  justify-content: space-between;
  gap: .45rem;
  align-items: center;
}

.sym-evidence-source {
  min-width: 0;
  color: #f2f6fb;
  font-weight: 700;
  font-size: .81rem;
}

.sym-evidence-state {
  padding: .22rem .38rem;
  border-radius: 999px;
  font-size: .58rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .08em;
  white-space: nowrap;
}

.sym-evidence-state.verified { color: #6ee5bb; background: rgba(66, 215, 161, .10); }
.sym-evidence-state.conflicting { color: #ffd093; background: rgba(255, 189, 101, .10); }
.sym-evidence-state.missing { color: #ff9ba0; background: rgba(255, 119, 124, .10); }

.sym-evidence-claim {
  color: #b7c6d5;
  font-size: .76rem;
  line-height: 1.47;
  margin: .5rem 0 .56rem;
}

.sym-evidence-meta {
  display: flex;
  flex-wrap: wrap;
  gap: .35rem .56rem;
  color: var(--sym-dim);
  font-size: .63rem;
}

.sym-challenge {
  padding: .95rem 1rem;
  border: 1px solid rgba(255, 189, 101, .3);
  border-radius: 16px;
  background: linear-gradient(130deg, rgba(255, 189, 101, .12), rgba(255, 189, 101, .035));
}

.sym-challenge h3 {
  color: #ffe1b2;
  margin: 0 0 .3rem;
  font-size: .93rem;
  letter-spacing: -.015em;
}

.sym-challenge p {
  color: #e7d2b4;
  margin: 0;
  font-size: .81rem;
  line-height: 1.5;
}

.sym-future {
  height: 100%;
  padding: .94rem;
  border: 1px solid var(--sym-line);
  border-radius: 16px;
  background: rgba(12, 26, 39, .70);
}

.sym-future.recommended {
  border-color: rgba(112, 153, 255, .58);
  background: linear-gradient(145deg, rgba(59, 101, 207, .22), rgba(12, 26, 39, .88));
}

.sym-future-risk { border-color: rgba(255, 119, 124, .28); }

.sym-future-label {
  color: #edf4ff;
  font-size: .96rem;
  font-weight: 740;
  letter-spacing: -.02em;
}

.sym-future-summary {
  min-height: 3.3rem;
  color: #aebfd0;
  font-size: .75rem;
  line-height: 1.45;
  margin: .45rem 0 .72rem;
}

.sym-future-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: .37rem;
  padding-top: .58rem;
  border-top: 1px solid var(--sym-line);
}

.sym-future-k {
  color: var(--sym-dim);
  font-size: .58rem;
  letter-spacing: .08em;
  text-transform: uppercase;
  font-weight: 750;
}

.sym-future-v {
  color: #d6e2ee;
  font-size: .71rem;
  line-height: 1.35;
  margin-top: .1rem;
}

.sym-action-caption {
  color: var(--sym-muted);
  font-size: .73rem;
  margin: .54rem 0 .52rem;
}

.sym-confirm {
  border-radius: 15px;
  border: 1px solid rgba(66, 215, 161, .34);
  background: linear-gradient(125deg, rgba(66, 215, 161, .14), rgba(66, 215, 161, .035));
  padding: .92rem 1rem;
  margin: .82rem 0;
}

.sym-confirm strong { display: block; font-size: .96rem; }
.sym-confirm span { display: block; color: #b9d8cc; font-size: .78rem; margin-top: .25rem; line-height: 1.45; }

.sym-timeline {
  position: relative;
  padding-left: 1.1rem;
  margin: .12rem 0;
}

.sym-timeline:before {
  content: "";
  position: absolute;
  width: 1px;
  top: .3rem;
  bottom: .3rem;
  left: .3rem;
  background: var(--sym-line-strong);
}

.sym-timeline-entry {
  position: relative;
  padding: .28rem 0 .92rem;
}

.sym-timeline-entry:before {
  content: "";
  position: absolute;
  left: -1.1rem;
  top: .48rem;
  width: .55rem;
  height: .55rem;
  border-radius: 50%;
  background: var(--sym-green);
  box-shadow: 0 0 0 4px rgba(66, 215, 161, .11);
}

.sym-timeline-time {
  color: var(--sym-dim);
  font-size: .62rem;
  letter-spacing: .065em;
  text-transform: uppercase;
}

.sym-timeline-action {
  color: #eef6ff;
  font-size: .84rem;
  font-weight: 720;
  margin-top: .18rem;
}

.sym-timeline-copy {
  color: #a8bacb;
  font-size: .73rem;
  line-height: 1.45;
  margin-top: .16rem;
}

.sym-outcome-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: .5rem;
  margin-top: .7rem;
}

.sym-outcome-cell {
  border: 1px solid var(--sym-line);
  background: rgba(7, 17, 26, .34);
  border-radius: 12px;
  padding: .68rem;
}

.sym-outcome-cell b {
  display: block;
  color: #eef5ff;
  font-size: .8rem;
  margin-top: .22rem;
}

.sym-divider {
  height: 1px;
  background: var(--sym-line);
  margin: 1.18rem 0;
}

.sym-empty {
  padding: 1rem;
  color: var(--sym-muted);
  font-size: .82rem;
  border: 1px dashed var(--sym-line-strong);
  border-radius: 14px;
}

div[data-testid="stAlert"] {
  border-radius: 14px;
  background: rgba(15, 39, 52, .88);
  border-color: var(--sym-line-strong);
}

@media (max-width: 960px) {
  .block-container { padding-left: .85rem; padding-right: .85rem; }
  .sym-region-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .sym-evidence-grid { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .block-container { padding: .72rem .7rem 6.4rem; }
  .sym-compact-header { display: none; }
  .sym-brand { gap: .55rem; }
  .sym-logo { width: 31px; height: 31px; }
  .sym-title { font-size: 1.47rem; }
  .sym-subtitle { font-size: .82rem; }
  .sym-live-scene { min-height: 205px; }
  .sym-decision-orb { width: 136px; height: 136px; }
  .sym-glance-title-row { padding-left: .78rem; padding-right: .78rem; }
  .sym-glance-title-row h2 { font-size: 1.28rem; }
  .sym-glance-value b { font-size: 1rem; }
  .sym-action-signal { margin-left: .68rem; margin-right: .68rem; }
  .sym-glance-metrics { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-left: .68rem; margin-right: .68rem; }
  .sym-glance-metric { min-height: 61px; padding: .5rem .56rem .45rem; }
  .sym-glance-metric.missing { display: none; }
  .sym-glance-metric.value { grid-column: auto; }
  .sym-blocker-strip { padding-left: .75rem; padding-right: .75rem; }
  .sym-future-scan-grid { gap: .36rem; }
  .sym-future-scan { min-height: 108px; padding: .58rem .53rem .52rem; border-radius: 12px; }
  .sym-future-scan > b { font-size: .67rem; }
  .sym-future-scan small { font-size: .51rem; }
  .sym-entry { padding-left: .45rem; padding-right: .45rem; }
  /* The choice stays in thumb reach while the live scene keeps moving. */
  div[data-testid="stHorizontalBlock"]:has([class*="open-review"]) {
    position: fixed;
    z-index: 120;
    left: .68rem;
    right: .68rem;
    bottom: max(.68rem, env(safe-area-inset-bottom));
    width: auto;
    margin: 0 !important;
    padding: .42rem;
    border: 1px solid rgba(146, 181, 230, .34);
    border-radius: 17px;
    background: rgba(7, 18, 31, .88);
    box-shadow: 0 12px 34px rgba(0, 0, 0, .44), 0 0 0 1px rgba(255,255,255,.025) inset;
    backdrop-filter: blur(16px);
  }
  div[data-testid="stHorizontalBlock"]:has([class*="open-review"]) button[kind="primary"] {
    box-shadow: 0 0 22px rgba(92, 141, 255, .4);
  }
  .sym-glance-footnote { padding-bottom: 3.95rem; }
  .sym-global { grid-template-columns: 1fr; padding: .68rem .74rem; }
  .sym-global-metrics { justify-content: flex-start; gap: .5rem .85rem; }
  .sym-region-grid { display: flex; overflow-x: auto; margin-left: -.1rem; margin-right: -.1rem; padding: 0 .1rem .24rem; }
  .sym-region { flex: 0 0 122px; }
  .sym-value-grid, .sym-outcome-grid { grid-template-columns: 1fr 1fr; }
  .sym-value-grid > :last-child, .sym-outcome-grid > :last-child { grid-column: 1 / -1; }
  .sym-card-inner, .sym-recommendation { padding: .9rem; }
  .sym-future-summary { min-height: auto; }
  div[data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: .5rem; }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { min-width: calc(50% - .3rem); flex: 1 1 calc(50% - .3rem); }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:only-child { min-width: 100%; flex-basis: 100%; }
  button[kind="secondary"], button[kind="primary"] { min-height: 48px; font-size: .86rem; }
  div[data-testid="stSidebar"] { min-width: min(80vw, 300px); }
}

@media (max-width: 390px) {
  .sym-glance-status { padding-left: .72rem; padding-right: .72rem; }
  .sym-glance-queue { max-width: 142px; font-size: .57rem; }
  .sym-live-scene { min-height: 196px; }
  .sym-decision-orb { width: 126px; height: 126px; }
  .sym-scene-node { transform: scale(.9); }
  .sym-scene-node-a { left: 2%; }
  .sym-scene-node-b { right: 2%; }
  .sym-glance-value { display: none; }
  .sym-glance-title-row { align-items: flex-start; }
  .sym-action-value { font-size: 1rem; }
}

@media (prefers-reduced-motion: reduce) {
  *, *:before, *:after { scroll-behavior: auto !important; transition: none !important; animation: none !important; }
}
</style>
        """,
        unsafe_allow_html=True,
    )
