"""Theme and responsive layout styles for the Symbiosis decision cockpit."""

from __future__ import annotations

import streamlit as st


def inject_theme() -> None:
    """Install the single visual language used by every application surface."""

    st.markdown(
        """
<style>
:root {
  --sym-bg: #f4f6f8;
  --sym-bg-deep: #eaf1f6;
  --sym-surface: rgba(255, 255, 255, .94);
  --sym-surface-2: rgba(247, 251, 255, .92);
  --sym-line: rgba(45, 88, 126, .14);
  --sym-line-strong: rgba(47, 128, 237, .28);
  --sym-text: #102a43;
  --sym-muted: #627d98;
  --sym-dim: #829ab1;
  --sym-blue: #2f80ed;
  --sym-green: #12b886;
  --sym-amber: #f2994a;
  --sym-red: #eb5757;
  --sym-purple: #7567e7;
  --sym-cyan: #00d2ff;
  --sym-shadow: 0 18px 44px rgba(51, 91, 128, .13);
}

html, body, [class*="css"] {
  color: var(--sym-text);
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

div[data-testid="stAppViewContainer"] {
  background:
    linear-gradient(rgba(61, 117, 160, .045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(61, 117, 160, .045) 1px, transparent 1px),
    radial-gradient(circle at 12% -3%, rgba(0, 210, 255, .18), transparent 30rem),
    radial-gradient(circle at 92% 15%, rgba(47, 128, 237, .14), transparent 28rem),
    radial-gradient(circle at 50% 85%, rgba(117, 103, 231, .08), transparent 33rem),
    linear-gradient(160deg, var(--sym-bg) 0%, var(--sym-bg-deep) 100%);
  background-size: 28px 28px, 28px 28px, auto, auto, auto, auto;
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
  background: #f8fbfe !important;
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
  background: rgba(255, 255, 255, .96);
  color: var(--sym-text);
  font-weight: 720;
  transition: transform .16s ease, border-color .16s ease, background .16s ease;
}

button[kind="secondary"]:hover, button[kind="primary"]:hover {
  transform: translateY(-1px);
  border-color: rgba(133, 171, 255, .76);
  background: #eff7ff;
}

button[kind="primary"] {
  background: linear-gradient(135deg, #2f80ed 0%, #00bfe8 100%);
  border-color: rgba(47, 128, 237, .52);
  color: white;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
  background: rgba(255, 255, 255, .92);
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
  color: #2f80ed;
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

/* Daylight ambient system -------------------------------------------------------
   The live scene carries the motion. Every detail panel stays quiet enough to
   read in direct daylight on a phone. */
.sym-kicker { color: #2f80ed; }
.sym-disclosure { color: #627d98; }
.sym-title, .sym-event-name, .sym-section-title { color: #102a43 !important; }
.sym-subtitle, .sym-event-context, .sym-section-note { color: #627d98; }

.sym-logo, .sym-compact-mark {
  background: linear-gradient(145deg, #2f80ed, #00c6f7);
  box-shadow: 0 8px 20px rgba(47, 128, 237, .22);
}
.sym-compact-title { color: #153550; }
.sym-compact-title span { color: #2f80ed; }

.sym-glance {
  border-color: rgba(47, 128, 237, .2);
  background:
    linear-gradient(148deg, rgba(255,255,255,.98), rgba(247,252,255,.94) 54%, rgba(239,249,255,.92)),
    var(--sym-surface);
  box-shadow: 0 24px 54px rgba(56, 97, 133, .15), inset 0 1px 0 rgba(255,255,255,.9);
}
.sym-glance-status { background: rgba(255,255,255,.55); }
.sym-status { color: #4f6d85; }
.sym-glance-queue { color: #5c7890; }
.sym-dot { background: var(--sym-blue); box-shadow: 0 0 0 4px rgba(47,128,237,.11); }
.sym-dot.green { background: #12b886; box-shadow: 0 0 0 4px rgba(18,184,134,.11); }
.sym-dot.amber { background: #f2994a; box-shadow: 0 0 0 4px rgba(242,153,74,.13); }
.sym-dot.red { background: #eb5757; box-shadow: 0 0 0 4px rgba(235,87,87,.13); }

.sym-ticker {
  border-top-color: rgba(47, 128, 237, .13);
  background: linear-gradient(90deg, rgba(0,210,255,.11), rgba(255,255,255,.52), rgba(47,128,237,.08));
}
.sym-ticker-track span { color: #35719b; }

.sym-live-scene:before {
  z-index: 0;
  background: radial-gradient(circle, rgba(0,210,255,.17), rgba(47,128,237,.08) 42%, transparent 69%);
}
.sym-live-scene:after {
  z-index: 0;
  opacity: 1;
  background: linear-gradient(90deg, rgba(0,210,255,.10), transparent 29%, transparent 69%, rgba(47,128,237,.09));
}
.sym-scene-grid { z-index: 0; opacity: .7; background-image: linear-gradient(rgba(47,128,237,.095) 1px, transparent 1px), linear-gradient(90deg, rgba(47,128,237,.095) 1px, transparent 1px); }
.sym-flow-map { z-index: 1; }
.sym-flow-base { stroke: rgba(47,128,237,.2); }
.sym-flow-active { stroke-width: 2.5; filter: drop-shadow(0 1px 2px rgba(0, 210, 255, .25)); }
.sym-flow-node { fill: #2f80ed; stroke: rgba(255,255,255,.96); stroke-width: 1.4; }
.sym-flow-node.n-two { fill: #00c6f7; }
.sym-flow-node.n-three { fill: #12b886; }
.sym-flow-packet { fill: #fff; }

.sym-ambient-wave {
  fill: none;
  stroke: rgba(0,210,255,.26);
  stroke-width: 1.15;
  stroke-linecap: round;
  stroke-dasharray: 13 19;
  animation: sym-ambient-drift 14s cubic-bezier(.42,0,.58,1) infinite;
}
.sym-ambient-wave-b { stroke: rgba(47,128,237,.18); stroke-width: 1.55; animation-duration: 20s; animation-direction: reverse; }
.sym-ambient-wave-c { stroke: rgba(18,184,134,.17); stroke-width: .95; animation-duration: 17s; animation-delay: -4s; }

.sym-scene-node {
  z-index: 3;
  border-color: rgba(47,128,237,.18);
  background: rgba(255,255,255,.72);
  box-shadow: 0 8px 20px rgba(65, 111, 150, .09);
}
.sym-scene-node span { color: #6f8ba2; }
.sym-scene-node b { color: #163a57; }

.sym-orbit {
  position: absolute;
  z-index: 2;
  left: 50%;
  top: 52%;
  border: 1px dashed rgba(0,210,255,.34);
  border-radius: 50%;
  pointer-events: none;
  transform: translate(-50%, -50%);
}
.sym-orbit-one { width: 188px; height: 188px; animation: sym-orbit-clockwise 11s linear infinite; }
.sym-orbit-two { width: 232px; height: 232px; border-color: rgba(47,128,237,.2); animation: sym-orbit-counter 17s linear infinite; }
.sym-orbit i {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00d2ff;
  box-shadow: 0 0 0 4px rgba(0,210,255,.11), 0 0 12px rgba(0,210,255,.52);
  animation: sym-particle-burst 2.8s ease-in-out infinite;
}
.sym-orbit i:nth-child(1) { top: -4px; left: 48%; }
.sym-orbit i:nth-child(2) { right: 5%; bottom: 13%; width: 4px; height: 4px; animation-delay: -.85s; }
.sym-orbit i:nth-child(3) { left: 7%; top: 62%; width: 3px; height: 3px; animation-delay: -1.7s; }
.sym-orbit-two i { background: #2f80ed; box-shadow: 0 0 0 3px rgba(47,128,237,.1), 0 0 9px rgba(47,128,237,.3); }
.sym-orbit-two i:nth-child(1) { top: 18%; left: 5%; }
.sym-orbit-two i:nth-child(2) { right: 13%; bottom: 5%; animation-delay: -1.25s; }
.sym-risk-elevated .sym-orbit-one { animation-duration: 7s; }
.sym-risk-elevated .sym-orbit-two { animation-duration: 11s; }

.sym-decision-orb {
  z-index: 4;
  background: radial-gradient(circle at 38% 28%, #ffffff 0%, #eef9ff 48%, #deeffb 76%);
  box-shadow: 0 0 0 1px rgba(47,128,237,.21), 0 13px 34px rgba(47,128,237,.17), inset 0 0 24px rgba(0,210,255,.13);
}
.sym-orb-halo { border-color: rgba(0,210,255,.48); }
.sym-ring-track { stroke: rgba(47,128,237,.14); }
.sym-ring-value { filter: drop-shadow(0 0 4px rgba(0, 210, 255, .58)); }
.sym-orb-core span { color: #5d7e98; }
.sym-orb-core strong { color: #153855; }
.sym-orb-core small { color: #58758e; }

.sym-glance-type { color: #2f80ed; }
.sym-glance-title-row h2 { color: #102a43 !important; }
.sym-glance-value span { color: #7590a5; }
.sym-glance-value b { color: #173955; }
.sym-action-signal {
  border-color: rgba(47,128,237,.25);
  background: linear-gradient(105deg, rgba(47,128,237,.105), rgba(0,210,255,.08) 64%, rgba(18,184,134,.055));
  box-shadow: inset 0 1px 0 rgba(255,255,255,.9);
}
.sym-action-label { color: #2f80ed; }
.sym-action-value { color: #123856; }
.sym-action-signal p { color: #547189; }

.sym-glance-metrics { border-color: rgba(47,128,237,.16); background: rgba(47,128,237,.1); }
.sym-glance-metric { background: rgba(255,255,255,.78); }
.sym-glance-metric b { color: #153854; }
.sym-glance-metric span { color: #6a869d; }
.sym-glance-metric i { background: #2f80ed; }
.sym-glance-metric.verified i { background: #12b886; }
.sym-glance-metric.conflict i, .sym-glance-metric.missing i { background: #f2994a; }
.sym-glance-metric.value i { background: linear-gradient(90deg, #2f80ed, #00d2ff); }
.sym-glance-metric.trust i { background: #12b886; }
.sym-glance-metric.risk i { background: #eb5757; }
.sym-glance-metric.friction i { background: #f2994a; }
.sym-glance-metric.evidence i { background: linear-gradient(90deg, #2f80ed, #00d2ff); }
.sym-blocker-strip { color: #617c93; }
.sym-blocker-strip strong, .sym-blocker-arrow { color: #bd741f; }

.sym-scan-head span { color: #173955; }
.sym-scan-head small { color: #6c879d; }
.sym-future-scan { border-color: rgba(47,128,237,.16); background: rgba(255,255,255,.78); box-shadow: 0 8px 22px rgba(66, 108, 143, .07); }
.sym-future-scan.recommended { border-color: rgba(47,128,237,.42); background: linear-gradient(145deg, rgba(47,128,237,.12), rgba(242,252,255,.94)); box-shadow: 0 10px 25px rgba(47,128,237,.11); }
.sym-future-scan.hold { background: linear-gradient(145deg, rgba(242,153,74,.09), rgba(255,255,255,.9)); }
.sym-future-scan-top span { color: #5f7d95; }
.sym-future-scan-top em { color: #2f80ed; }
.sym-future-scan > b { color: #173955; }
.sym-scan-bar { background: rgba(75,118,153,.13); }
.sym-scan-bar i { background: #2f80ed; }
.sym-future-scan.hold .sym-scan-bar i, .sym-future-scan.authorize .sym-scan-bar i { background: #f2994a; }
.sym-future-scan small, .sym-glance-footnote, .sym-detail-kicker { color: #617d95; }

/* Formal Symbiosis board: familiar analytical DNA underneath the mobile cockpit. */
.sym-formal-board {
  position: relative;
  overflow: hidden;
  margin: .88rem 0 1rem;
  padding: .95rem;
  border: 1px solid rgba(47,128,237,.2);
  border-radius: 18px;
  background:
    linear-gradient(rgba(66,126,172,.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(66,126,172,.055) 1px, transparent 1px),
    linear-gradient(145deg, rgba(255,255,255,.98), rgba(246,251,255,.92));
  background-size: 22px 22px, 22px 22px, auto;
  box-shadow: 0 13px 32px rgba(53,95,129,.1);
}
.sym-formal-head { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; }
.sym-formal-overline { color:#2f80ed; font-size:.57rem; font-weight:840; letter-spacing:.115em; text-transform:uppercase; }
.sym-formal-head h3 { margin:.18rem 0 .2rem; color:#173955 !important; font-size:1.08rem; letter-spacing:-.025em; }
.sym-formal-head p { max-width:40rem; margin:0; color:#607c93; font-size:.72rem; line-height:1.35; }
.sym-formal-now { display:inline-flex; align-items:center; gap:.35rem; flex:0 0 auto; padding:.38rem .5rem; border:1px solid rgba(47,128,237,.14); border-radius:9px; background:rgba(255,255,255,.76); color:#55738b; font-size:.57rem; font-weight:780; letter-spacing:.06em; text-transform:uppercase; white-space:nowrap; }
.sym-formal-now .sym-dot { width:6px; height:6px; box-shadow:none; }
.sym-formal-metrics { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1px; margin:.78rem 0 .64rem; overflow:hidden; border:1px solid rgba(47,128,237,.16); border-radius:11px; background:rgba(47,128,237,.12); }
.sym-formal-metrics > div { position:relative; min-width:0; padding:.54rem .62rem .5rem; background:rgba(255,255,255,.82); }
.sym-formal-metrics span { display:block; color:#6a859b; font-size:.55rem; font-weight:820; letter-spacing:.09em; text-transform:uppercase; }
.sym-formal-metrics b { display:block; margin-top:.08rem; color:#173955; font-size:1.04rem; font-weight:820; letter-spacing:-.04em; }
.sym-formal-metrics i { display:block; width:100%; height:2px; margin-top:.36rem; border-radius:999px; background:#2f80ed; }
.sym-formal-metrics .trust i { background:#12a575; }.sym-formal-metrics .risk i { background:#d75d68; }.sym-formal-metrics .friction i { background:#f2994a; }.sym-formal-metrics .latency i { background:#2f80ed; }
.sym-formal-chart-wrap { position:relative; overflow:hidden; min-height:220px; border:1px solid rgba(47,128,237,.15); border-radius:12px; background:rgba(255,255,255,.52); }
.sym-formal-chart { display:block; width:100%; height:220px; }
.sym-formal-grid-line { stroke:rgba(48,108,153,.13); stroke-width:1; stroke-dasharray:3 5; }.sym-formal-axis { fill:#7d95a7; font-size:8px; font-weight:720; }
.sym-formal-load { fill:url(#sym-formal-load); }.sym-formal-line { fill:none; stroke-width:2.35; stroke-linecap:round; stroke-linejoin:round; }.sym-formal-line.trust,.sym-formal-dot.trust { stroke:#12a575; fill:#12a575; }.sym-formal-line.risk,.sym-formal-dot.risk { stroke:#d75d68; fill:#d75d68; }.sym-formal-line.friction,.sym-formal-dot.friction { stroke:#2f80ed; fill:#2f80ed; }
.sym-formal-dot { stroke:#fff; stroke-width:1.8px; filter:drop-shadow(0 1px 2px rgba(47,128,237,.3)); }
.sym-formal-legend { position:absolute; right:.5rem; bottom:.42rem; display:flex; gap:.38rem; padding:.3rem .4rem; border:1px solid rgba(47,128,237,.12); border-radius:8px; background:rgba(255,255,255,.8); color:#668197; font-size:.52rem; font-weight:800; letter-spacing:.05em; text-transform:uppercase; }.sym-formal-legend span:before { content:""; display:inline-block; width:5px; height:5px; margin-right:3px; border-radius:50%; background:#2f80ed; }.sym-formal-legend .trust:before { background:#12a575; }.sym-formal-legend .risk:before { background:#d75d68; }.sym-formal-legend .friction:before { background:#2f80ed; }.sym-formal-legend .load:before { background:#48b8e8; }

.sym-projection-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.45rem; }.sym-projection-card { min-width:0; padding:.65rem; border:1px solid rgba(47,128,237,.15); border-radius:12px; background:rgba(255,255,255,.78); }.sym-projection-card span { display:block; color:#668197; font-size:.56rem; font-weight:820; letter-spacing:.075em; text-transform:uppercase; }.sym-projection-card b { display:block; margin:.17rem 0 .12rem; color:#173955; font-size:1.05rem; letter-spacing:-.04em; }.sym-projection-card small { color:#71899d; font-size:.61rem; }
.sym-histogram-card { margin-top:.55rem; padding:.66rem; border:1px solid rgba(47,128,237,.15); border-radius:12px; background:rgba(255,255,255,.72); }.sym-histogram-head { display:flex; justify-content:space-between; gap:.5rem; color:#55758f; font-size:.63rem; font-weight:800; }.sym-histogram-head small { color:#7890a2; font-size:.57rem; font-weight:700; }.sym-histogram { display:flex; align-items:flex-end; gap:3px; height:94px; margin-top:.52rem; padding:.2rem .12rem 0; border-bottom:1px solid rgba(47,128,237,.15); background:linear-gradient(to top, rgba(47,128,237,.04) 1px, transparent 1px); background-size:100% 24px; }.sym-histogram i { display:block; flex:1; min-width:2px; border-radius:3px 3px 0 0; background:linear-gradient(to top,#2f80ed,#00c6f7); opacity:.9; }
.sym-ledger-wrap { overflow-x:auto; border:1px solid rgba(47,128,237,.14); border-radius:12px; background:rgba(255,255,255,.75); }.sym-ledger { width:100%; min-width:650px; border-collapse:collapse; color:#46667e; font-size:.66rem; }.sym-ledger th { padding:.56rem .62rem; color:#6b8497; font-size:.53rem; font-weight:840; letter-spacing:.075em; text-align:left; text-transform:uppercase; background:rgba(47,128,237,.055); }.sym-ledger td { padding:.53rem .62rem; border-top:1px solid rgba(47,128,237,.1); white-space:nowrap; }.sym-ledger-state { display:inline-block; padding:.18rem .33rem; border-radius:999px; font-size:.52rem; font-weight:830; letter-spacing:.055em; text-transform:uppercase; }.sym-ledger-state.verified { color:#118466; background:rgba(18,184,134,.12); }.sym-ledger-state.attention { color:#a36518; background:rgba(242,153,74,.15); }.sym-ledger-state.critical { color:#ba4954; background:rgba(215,93,104,.12); }.sym-ledger-state.neutral { color:#59748a; background:rgba(89,116,138,.1); }

.sym-entry h1 { color: #102a43 !important; }
.sym-entry p { color: #4e6b84; }
.sym-entry-mark { background: radial-gradient(circle at 36% 30%, #a3f0ff, #00bfe8 48%, #2f80ed); box-shadow: 0 0 0 12px rgba(0,210,255,.075), 0 0 55px rgba(0,210,255,.2); }
.sym-entry-mark i { border-color: rgba(0,210,255,.28); }
.sym-entry-signal { border-color: rgba(47,128,237,.16); color: #54728a; background: rgba(255,255,255,.75); }
.sym-entry-note { color: #6d879b; }

.sym-card { background: linear-gradient(145deg, rgba(255,255,255,.97), rgba(247,251,255,.94)); border-color: rgba(45,88,126,.15); box-shadow: 0 14px 32px rgba(55, 95, 131, .1); color: #102a43; }
.sym-recommendation { background: linear-gradient(135deg, rgba(47,128,237,.12), rgba(0,210,255,.055)), #fafdff; border-color: rgba(47,128,237,.28); }
.sym-recommendation-title { color: #2f80ed; }
.sym-recommendation-action { color: #102a43; }
.sym-recommendation-copy { color: #526f87; }
.sym-confidence strong { color: #102a43; }
.sym-confidence span { color: #627d98; }
.sym-global, .sym-region, .sym-evidence { background: rgba(255,255,255,.78); border-color: rgba(45,88,126,.14); }
.sym-global-world strong, .sym-region-time, .sym-evidence-source { color: #173955; }
.sym-global-world span, .sym-region-head, .sym-evidence-claim { color: #627d98; }
.sym-global-metric, .sym-evidence-meta { color: #6c879d; }
.sym-global-metric b { color: #173955; }
.sym-region-state { color: #118466; }
.sym-region-state.handoff, .sym-region-state.watch { color: #c57922; }
.sym-region-state.quiet { color: #718798; }
.sym-challenge { border-color: rgba(242,153,74,.35); background: linear-gradient(130deg, rgba(242,153,74,.13), rgba(255,255,255,.86)); }
.sym-challenge h3 { color: #9a5b13; }
.sym-challenge p { color: #6e542e; }
.sym-future { border-color: rgba(45,88,126,.15); background: rgba(255,255,255,.8); }
.sym-future.recommended { border-color: rgba(47,128,237,.42); background: linear-gradient(145deg, rgba(47,128,237,.13), rgba(250,253,255,.96)); }
.sym-impact-grid { display:grid; grid-template-columns:1fr 1fr; gap:.56rem; margin-bottom:.68rem; }.sym-impact { padding:.72rem; border:1px solid rgba(45,88,126,.14); border-radius:12px; }.sym-impact span { display:block; color:#70889a; font-size:.57rem; font-weight:830; letter-spacing:.085em; text-transform:uppercase; }.sym-impact b { display:block; margin:.2rem 0; color:#173955; font-size:.95rem; letter-spacing:-.025em; }.sym-impact p { margin:0; color:#607b91; font-size:.68rem; line-height:1.35; }.sym-impact.before { background:linear-gradient(145deg, rgba(242,153,74,.1), rgba(255,255,255,.85)); border-color:rgba(242,153,74,.26); }.sym-impact.after { background:linear-gradient(145deg, rgba(18,184,134,.11), rgba(255,255,255,.85)); border-color:rgba(18,184,134,.25); }
.sym-future-risk { border-color: rgba(242,153,74,.32); }
.sym-future-label, .sym-future-v { color: #173955; }
.sym-future-summary { color: #5b768d; }
.sym-badge { color: #52718a; border-color: rgba(45,88,126,.14); background: rgba(247,251,255,.88); }
.sym-confirm { border-color: rgba(18,184,134,.3); background: linear-gradient(125deg, rgba(18,184,134,.12), rgba(255,255,255,.88)); }
.sym-confirm span { color: #39725f; }
.sym-timeline-time, .sym-timeline-copy { color: #6b859a; }
.sym-timeline-action, .sym-outcome-cell b { color: #173955; }
.sym-outcome-cell { border-color: rgba(45,88,126,.13); background: rgba(248,252,255,.82); }
.sym-empty { color: #627d98; border-color: rgba(47,128,237,.28); background: rgba(255,255,255,.48); }
div[data-testid="stAlert"] { background: rgba(255,255,255,.88); border-color: rgba(47,128,237,.22); }

@keyframes sym-ambient-drift { from { stroke-dashoffset: 0; } 50% { stroke-dashoffset: -92; } to { stroke-dashoffset: -186; } }
@keyframes sym-orbit-clockwise { from { transform: translate(-50%, -50%) rotate(0deg); } to { transform: translate(-50%, -50%) rotate(360deg); } }
@keyframes sym-orbit-counter { from { transform: translate(-50%, -50%) rotate(360deg); } to { transform: translate(-50%, -50%) rotate(0deg); } }
@keyframes sym-particle-burst { 0%,100% { opacity: .4; transform: scale(.7); } 45% { opacity: 1; transform: scale(1.55); } 65% { opacity: .36; transform: scale(.84); } }

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
  .sym-orbit-one { width: 172px; height: 172px; }
  .sym-orbit-two { width: 212px; height: 212px; }
  .sym-glance-title-row { padding-left: .78rem; padding-right: .78rem; }
  .sym-glance-title-row h2 { font-size: 1.28rem; }
  .sym-glance-value b { font-size: 1rem; }
  .sym-action-signal { margin-left: .68rem; margin-right: .68rem; }
  .sym-glance-metrics { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-left: .68rem; margin-right: .68rem; }
  .sym-glance-metric { min-height: 61px; padding: .5rem .56rem .45rem; }
  .sym-glance-metric.evidence { display: none; }
  .sym-glance-metric.friction { grid-column: auto; }
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
    border: 1px solid rgba(47, 128, 237, .24);
    border-radius: 17px;
    background: rgba(255, 255, 255, .9);
    box-shadow: 0 12px 34px rgba(57, 97, 132, .18), 0 0 0 1px rgba(255,255,255,.9) inset;
    backdrop-filter: blur(16px);
  }
  div[data-testid="stHorizontalBlock"]:has([class*="open-review"]) button[kind="primary"] {
    box-shadow: 0 0 22px rgba(0, 210, 255, .3);
  }
  .sym-glance-footnote { padding-bottom: 3.95rem; }
  .sym-formal-board { margin-top: .68rem; padding: .72rem; border-radius:15px; }
  .sym-formal-head { flex-direction:column; gap:.48rem; }
  .sym-formal-head h3 { font-size:1rem; }
  .sym-formal-head p { font-size:.68rem; }
  .sym-formal-now { align-self:flex-start; }
  .sym-formal-metrics { grid-template-columns:1fr 1fr; }
  .sym-formal-chart-wrap { min-height:190px; }
  .sym-formal-chart { height:190px; }
  .sym-formal-legend { font-size:.47rem; gap:.25rem; }
  .sym-projection-grid { grid-template-columns:1fr 1fr; }
  .sym-projection-card b { font-size:.96rem; }
  .sym-histogram-head { align-items:flex-start; flex-direction:column; }
  .sym-global { grid-template-columns: 1fr; padding: .68rem .74rem; }
  .sym-global-metrics { justify-content: flex-start; gap: .5rem .85rem; }
  .sym-region-grid { display: flex; overflow-x: auto; margin-left: -.1rem; margin-right: -.1rem; padding: 0 .1rem .24rem; }
  .sym-region { flex: 0 0 122px; }
  .sym-value-grid, .sym-outcome-grid { grid-template-columns: 1fr 1fr; }
  .sym-value-grid > :last-child, .sym-outcome-grid > :last-child { grid-column: 1 / -1; }
  .sym-impact-grid { grid-template-columns: 1fr; }
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
  .sym-orbit-one { width: 160px; height: 160px; }
  .sym-orbit-two { width: 198px; height: 198px; }
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
