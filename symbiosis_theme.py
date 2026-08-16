"""Theme and responsive layout styles for the Symbiosis decision cockpit."""

from __future__ import annotations

import streamlit as st


def inject_theme() -> None:
    """Install the single visual language used by every application surface."""

    st.markdown(
        """
<style>
:root {
  --sym-bg: #071019;
  --sym-bg-deep: #04090f;
  --sym-surface: rgba(15, 27, 40, .90);
  --sym-surface-2: rgba(20, 36, 52, .86);
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
    radial-gradient(circle at 14% -2%, rgba(92, 141, 255, .18), transparent 31rem),
    radial-gradient(circle at 90% 16%, rgba(66, 215, 161, .09), transparent 26rem),
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
  .sym-brand { gap: .55rem; }
  .sym-logo { width: 31px; height: 31px; }
  .sym-title { font-size: 1.47rem; }
  .sym-subtitle { font-size: .82rem; }
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

@media (prefers-reduced-motion: reduce) {
  *, *:before, *:after { scroll-behavior: auto !important; transition: none !important; animation: none !important; }
}
</style>
        """,
        unsafe_allow_html=True,
    )
