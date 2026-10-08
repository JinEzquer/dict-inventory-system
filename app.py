import base64
import hashlib
import importlib.util
import io
import json
import hmac
import html
import os
import re
import secrets
import tempfile
import time
from datetime import datetime, timedelta, timezone
from functools import partial
from pathlib import Path
from xml.sax.saxutils import escape
import psycopg2  # noqa: F401  (driver used by SQLAlchemy)
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
import altair as alt
import pandas as pd
import streamlit as st

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="DICT NIR - Inventory System",
    page_icon="analytics-512x512.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ORANGE = "#FF6A00"
INK = "#141414"
MUTED = "#6b7280"
LINE = "#e5e7eb"
PALETTE = ["#FF6A00", "#FF8A1F", "#FFA826", "#FFC53D", "#FFE08A"]

SEARCH_ICON = "data:image/png;base64,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"

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#FF9A3D"/><stop offset="1" stop-color="#FF5A00"/></linearGradient></defs>
<rect width="48" height="48" rx="13" fill="url(#g)"/>
<path d="M24 11.5 35 17.75v12.5L24 36.5 13 30.25v-12.5z" fill="#fff" fill-opacity=".16" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/>
<path d="M13 17.75 24 24l11-6.25" fill="#fff" fill-opacity=".95" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/>
<path d="M24 24v12.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>
</svg>"""
LOGO_URI = "data:image/svg+xml;base64," + base64.b64encode(LOGO_SVG.encode()).decode()

LOGO_URI_BLUE = "data:image/svg+xml;base64," + base64.b64encode(
    LOGO_SVG.replace("#FF9A3D", "#7DB8FF").replace("#FF5A00", "#2F7BF5").encode()).decode()


_LIGHT_RAW = """
.stApp { background-color: #eaf4ff; }
.stApp::before { background: radial-gradient(circle, rgba(59,130,246,.26), rgba(59,130,246,0) 68%); }
.stApp::after { background: radial-gradient(circle, rgba(56,189,248,.28), rgba(56,189,248,0) 68%); }
[data-testid="stAppViewContainer"]::before { background: radial-gradient(circle, rgba(125,211,252,.32), rgba(125,211,252,0) 68%); }

.card { background: rgba(255,255,255,.75); border-color: rgba(59,130,246,.22); }
.card::before { background: linear-gradient(90deg, #3B82F6, #7DD3FC); }
.card:hover { box-shadow: 0 14px 30px rgba(59,130,246,.18); }
div[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255,255,255,.65); border-color: rgba(59,130,246,.22) !important; }
div[data-testid="stDataFrame"] { border-color: rgba(59,130,246,.22); }
.badge-orange { background: rgba(59,130,246,.14); color: #2563EB; }
.area-row b { color: #2563EB; }
.total-bar { background: rgba(59,130,246,.10); border-color: rgba(59,130,246,.32); }
.total-bar .t-amount { color: #2563EB; }

[data-testid="stMain"] .stButton > button, [data-testid="stMain"] .stFormSubmitButton > button { background: #3B82F6; border-color: #3B82F6; }
[data-testid="stMain"] .stButton > button:hover, [data-testid="stMain"] .stFormSubmitButton > button:hover { background: #2563EB; border-color: #2563EB; }

div[data-testid="stVegaLiteChart"] { filter: hue-rotate(180deg); }
button[data-baseweb="tab"][aria-selected="true"] { color: #2563EB !important; }
div[data-baseweb="tab-highlight"] { background-color: #3B82F6 !important; }
button[data-testid="stBaseButton-segmented_controlActive"] { background: rgba(59,130,246,.16) !important; border-color: #3B82F6 !important; color: #2563EB !important; }
[data-testid="stMain"] .stDownloadButton > button { color: #2563EB; border-color: #3B82F6; }
[data-testid="stMain"] .stDownloadButton > button:hover { background: #3B82F6; color: #fff; }

.login-bg { --acc: 59,130,246; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.login-marker) { background: rgba(255,255,255,.74); box-shadow: 0 24px 60px rgba(37,99,235,.16); }
.brand-logo { background-image: url("__LOGO_BLUE__"); box-shadow: 0 4px 12px rgba(59,130,246,.30); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #10141c 0%, #141b29 55%, #0f2038 100%) !important; }
section[data-testid="stSidebar"]::before { background: radial-gradient(circle, rgba(59,130,246,.42), rgba(59,130,246,0) 70%); }
section[data-testid="stSidebar"]::after { background: radial-gradient(circle, rgba(125,211,252,.22), rgba(125,211,252,0) 70%); }
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] { background: linear-gradient(90deg, #3B82F6, #60A5FA); box-shadow: 0 8px 20px rgba(59,130,246,.35); }
""".replace("__LOGO_BLUE__", LOGO_URI_BLUE)


def _scope(css, prefix):
    """Prefix every selector so the rules only apply under `prefix`."""
    return re.sub(r"([^{}]+)\{([^{}]*)\}",
                  lambda m: ",".join(prefix + " " + x.strip() for x in m.group(1).split(",")) + "{" + m.group(2) + "}",
                  css)


# Light mode = whatever theme Streamlit is ACTUALLY showing (detected by the script below),
# with the browser's light setting as a fallback until detection runs.
LIGHT_CSS = (_scope(_LIGHT_RAW, 'html[data-app-theme="light"]')
             + "@media (prefers-color-scheme: light) {"
             + _scope(_LIGHT_RAW, "html:not([data-app-theme])") + "}")

THEME_JS = r"""<script>
(function () {
  try {
    var P = window.parent, d = P.document;
    if (P.__themeCleanup) P.__themeCleanup();          // remove the previous instance
    if (P.location.hash) {                              // old "#key-metrics" links made the page auto-scroll
      P.history.replaceState(null, '', P.location.pathname + P.location.search);
      var mn = d.querySelector('[data-testid="stMain"]'); if (mn) mn.scrollTo(0, 0);
    }

    function rgbOf(el) { var m = P.getComputedStyle(el).color.match(/[\d.]+/g) || [0, 0, 0]; return [+m[0], +m[1], +m[2]]; }
    function neutral(c) { return Math.max(c[0], c[1], c[2]) - Math.min(c[0], c[1], c[2]) < 40; }
    function detect() {
      // Streamlit's body TEXT colour: light text = dark theme.
      // Coloured text (red tab labels, links...) is ignored; only grey/black/white text counts.
      var host = d.querySelector('[data-testid="stMain"]') || d.querySelector('.stApp') || d.body;
      var probe = d.getElementById('__theme_probe');
      if (!probe || !host.contains(probe)) {
        probe = d.createElement('div');
        probe.id = '__theme_probe';
        probe.style.cssText = 'position:fixed;left:-9999px;top:0;width:1px;height:1px;visibility:hidden;pointer-events:none';
        host.appendChild(probe);
      }
      var els = [probe], ps = host.querySelectorAll('p');
      for (var i = 0; i < ps.length && i < 30; i++) els.push(ps[i]);
      els.push(d.querySelector('.stApp') || d.body);
      for (var j = 0; j < els.length; j++) {
        var c = rgbOf(els[j]);
        if (neutral(c)) return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255 > 0.5 ? 'dark' : 'light';
      }
      return d.documentElement.getAttribute('data-app-theme') || 'light';
    }
    function apply() {
      var t = detect();
      if (d.documentElement.getAttribute('data-app-theme') !== t) d.documentElement.setAttribute('data-app-theme', t);
    }

    // 1) react in the next frame when the app root changes (= theme switch). Cheap: root element only.
    var pending = false;
    function schedule() { if (pending) return; pending = true; P.requestAnimationFrame(function () { pending = false; apply(); }); }
    var mo = new P.MutationObserver(schedule);
    mo.observe(d.documentElement, { attributes: true, attributeFilter: ['class', 'style'] });
    var app = d.querySelector('.stApp');
    if (app) mo.observe(app, { attributes: true, attributeFilter: ['class', 'style'] });

    // 2) clicks INSIDE the settings menu: re-check for ~0.8 s (ignored everywhere else)
    function burst(e) {
      if (!e.target || !e.target.closest || !e.target.closest('[data-baseweb="popover"],[role="dialog"],[role="menu"]')) return;
      var n = 0, h = P.setInterval(function () { apply(); if (++n > 20) P.clearInterval(h); }, 40);
    }
    d.addEventListener('click', burst, true);

    // 3) system light/dark change + slow safety net
    var mq = P.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener('change', burst);
    var timer = P.setInterval(apply, 1000);

    P.__themeCleanup = function () {
      mo.disconnect(); d.removeEventListener('click', burst, true);
      mq.removeEventListener('change', burst); P.clearInterval(timer);
    };
    apply();
  } catch (e) {}
})();
</script>"""


# --- 2. CUSTOM CSS (Stockpile-style: white, orange accent, black buttons) ---
st.markdown(f"""
<style>

/* Theme-aware: no hard-coded backgrounds or text colors.
   Streamlit's own light/dark theme supplies those; we only add
   translucent greys (work on both) and the orange accent. */
html, body, [class*="css"], .stApp {{
    font-family: 'Segoe UI', system-ui, -apple-system, Roboto, 'Helvetica Neue', sans-serif;
}}
.block-container {{ padding-top: 4.5rem; max-width: 1400px; }}
h1, h2, h3 {{ font-weight: 700; letter-spacing: -0.02em; }}

/* Sidebar brand */
.brand {{ display:flex; align-items:center; gap:12px; margin: 4px 0 28px; }}
.brand-logo {{ width:44px; height:44px; flex:none; border-radius:12px;
    background: url("{LOGO_URI}") center / cover no-repeat;
    box-shadow: 0 4px 12px rgba(255,106,0,.28); }}
.brand-name {{ font-size:22px; font-weight:700; line-height:1.1; }}
.brand-sub {{ font-size:12px; opacity:.65; }}
.menu-label {{ font-size:14px; opacity:.65; margin-bottom:6px; }}

/* ===== SIDEBAR: dark navy panel with animated orange glow ===== */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #12141a 0%, #181b24 55%, #26170a 100%) !important;
    border-right: 1px solid rgba(255,255,255,.07);
    isolation: isolate;
}}
section[data-testid="stSidebar"] > div {{ background: transparent !important; }}
section[data-testid="stSidebar"]::before {{
    content: ""; position: absolute; width: 340px; height: 340px; left: -100px; bottom: -130px;
    border-radius: 50%; z-index: -1; pointer-events: none;
    background: radial-gradient(circle, rgba(255,106,0,.42), rgba(255,106,0,0) 70%);
    animation: sideGlow 9s ease-in-out infinite alternate;
}}
section[data-testid="stSidebar"]::after {{
    content: ""; position: absolute; width: 220px; height: 220px; right: -90px; top: 120px;
    border-radius: 50%; z-index: -1; pointer-events: none;
    background: radial-gradient(circle, rgba(255,176,59,.20), rgba(255,176,59,0) 70%);
    animation: sideGlow2 12s ease-in-out infinite alternate;
}}
@keyframes sideGlow {{ from {{ transform: translate(0,0) scale(1); }} to {{ transform: translate(60px,-70px) scale(1.2); }} }}
@keyframes sideGlow2 {{ from {{ transform: translate(0,0); }} to {{ transform: translate(-40px,80px); }} }}

section[data-testid="stSidebar"] .brand-name {{ color: #ffffff; letter-spacing: -0.01em; }}
section[data-testid="stSidebar"] .brand-sub {{ color: #9aa3b2; opacity: 1; }}
section[data-testid="stSidebar"] .menu-label {{
    color: #7d8696; opacity: 1; font-size: 11px; font-weight: 600;
    letter-spacing: .16em; text-transform: uppercase; margin: 0 0 10px 4px;
}}
.side-divider {{ height: 1px; margin: -10px 0 18px;
    background: linear-gradient(90deg, rgba(255,255,255,.18), rgba(255,255,255,0)); }}

section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {{ color: #cbd2de; }}

/* Nav buttons */
section[data-testid="stSidebar"] .stButton > button {{
    background: transparent; border: 1px solid transparent; box-shadow: none; color: #cbd2de;
    justify-content: flex-start; text-align: left;
    padding: 11px 14px; border-radius: 10px; font-weight: 500;
    transition: background .18s ease, transform .18s ease, color .18s ease;
}}
section[data-testid="stSidebar"] .stButton > button > div {{ justify-content: flex-start; width: 100%; }}
section[data-testid="stSidebar"] .stButton > button p {{ color: inherit; font-size: 15px; text-align: left; }}
section[data-testid="stSidebar"] .stButton > button span {{ color: inherit; }}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,.08); color: #ffffff; border-color: rgba(255,255,255,.07);
    transform: translateX(4px);
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(90deg, #FF6A00, #FF8A1F); color: #ffffff; font-weight: 600;
    box-shadow: 0 8px 20px rgba(255,106,0,.35);
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] p {{ color: #ffffff; }}

/* Sidebar footer card */
.side-foot {{
    margin-top: 34px; padding: 14px 16px; border-radius: 12px;
    background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.09);
}}
.side-foot .live {{ display:flex; align-items:center; gap:8px; font-size:12px; color:#86efac; font-weight:600; }}
.side-foot .dot {{ width:8px; height:8px; border-radius:50%; background:#22c55e;
    box-shadow: 0 0 0 0 rgba(34,197,94,.6); animation: pulse 2s infinite; }}
@keyframes pulse {{ 70% {{ box-shadow: 0 0 0 8px rgba(34,197,94,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(34,197,94,0); }} }}
.side-foot .foot-title {{ margin-top:10px; font-size:13px; font-weight:600; color:#f1f5f9; }}
.side-foot .foot-sub {{ font-size:12px; color:#8b94a5; }}

/* ===== MAIN AREA: animated background ===== */
.stApp {{
    isolation: isolate;
    background-image: radial-gradient(rgba(128,128,128,.16) 1px, transparent 1px);
    background-size: 26px 26px;
}}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {{ background: transparent !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}

.stApp::before, .stApp::after, [data-testid="stAppViewContainer"]::before {{
    content: ""; position: fixed; border-radius: 50%; z-index: -1; pointer-events: none;
}}
.stApp::before {{
    width: 58vw; height: 58vw; top: -20vw; left: -12vw;
    background: radial-gradient(circle, rgba(255,106,0,.22), rgba(255,106,0,0) 68%);
    animation: blobA 20s ease-in-out infinite alternate;
}}
.stApp::after {{
    width: 52vw; height: 52vw; right: -14vw; bottom: -22vw;
    background: radial-gradient(circle, rgba(255,176,59,.20), rgba(255,176,59,0) 68%);
    animation: blobB 24s ease-in-out infinite alternate;
}}
[data-testid="stAppViewContainer"]::before {{
    width: 38vw; height: 38vw; top: 34vh; left: 46vw;
    background: radial-gradient(circle, rgba(255,90,60,.12), rgba(255,90,60,0) 68%);
    animation: blobC 28s ease-in-out infinite alternate;
}}
@keyframes blobA {{ from {{ transform: translate(0,0) scale(1); }} to {{ transform: translate(16vw,12vh) scale(1.18); }} }}
@keyframes blobB {{ from {{ transform: translate(0,0) scale(1); }} to {{ transform: translate(-14vw,-10vh) scale(1.22); }} }}
@keyframes blobC {{ from {{ transform: translate(0,0) scale(.9); }} to {{ transform: translate(-18vw,14vh) scale(1.1); }} }}

/* Cards: glass look, soft entrance, hover lift */
.card, .total-bar {{
    transition: transform .2s ease, box-shadow .2s ease; }}
.card:hover {{ transform: translateY(-4px); box-shadow: 0 14px 30px rgba(255,106,0,.16); }}
@keyframes fadeUp {{ from {{ opacity:0; transform: translateY(12px); }} to {{ opacity:1; transform: translateY(0); }} }}

.stApp::before, .stApp::after, [data-testid="stAppViewContainer"]::before,
section[data-testid="stSidebar"]::before, section[data-testid="stSidebar"]::after {{ will-change: transform; }}

/* Panels (bordered containers + forms) and card accent */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 14px; border-color: rgba(128,128,128,.28) !important;
    background: rgba(128,128,128,.06);
}}
.card {{ position: relative; overflow: hidden; }}
.card::before {{ content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background: linear-gradient(90deg, #FF6A00, #FFB03B); }}
.page-title {{ font-size: 30px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.2; margin: 0 0 2px; }}

@media (prefers-reduced-motion: reduce) {{
    .stApp::before, .stApp::after, [data-testid="stAppViewContainer"]::before,
    section[data-testid="stSidebar"]::before, section[data-testid="stSidebar"]::after,
    .card, .total-bar, .side-foot .dot, .login-bg .ring, .login-bg .orb {{ animation: none !important; }}
}}

/* Cards */
.card {{
    background: rgba(128,128,128,.07);
    border: 1px solid rgba(128,128,128,.28);
    border-radius:14px; padding:18px 20px;
}}
.card-label {{ font-size:13px; font-weight:500; opacity:.65; }}
.card-value {{ font-size:28px; font-weight:700; margin:4px 0 8px; }}
.badge {{ display:inline-block; font-size:11px; font-weight:600; padding:3px 10px; border-radius:6px; }}
.badge-green {{ background:rgba(34,197,94,.18); color:#22a559; }}
.badge-red {{ background:rgba(239,68,68,.18); color:#ef4444; }}
.badge-orange {{ background:rgba(255,106,0,.18); color:{ORANGE}; }}

.section-title {{ font-size:18px; font-weight:700; margin: 6px 0 2px; }}
.section-sub {{ font-size:13px; opacity:.65; margin-bottom: 8px; }}

.area-row {{
    display:flex; justify-content:space-between; font-size:13px;
    padding:8px 0; border-bottom:1px solid rgba(128,128,128,.22);
}}
.area-row b {{ color:{ORANGE}; font-weight:600; width:44px; display:inline-block; }}

/* Search box icon */
input[placeholder="Search item name..."] {{
    background-image: url("{SEARCH_ICON}"); background-repeat: no-repeat;
    background-position: 14px center; background-size: 18px 18px;
    padding-left: 44px !important;
}}

/* Total bar under tables */
.total-bar {{
    display:flex; justify-content:space-between; align-items:center;
    margin-top:8px; padding:14px 20px; border-radius:12px;
    background: rgba(255,106,0,.12); border:1px solid rgba(255,106,0,.35);
}}
.total-bar .t-label {{ font-weight:700; letter-spacing:.04em; }}
.total-bar .t-sub {{ font-size:12px; opacity:.65; }}
.total-bar .t-amount {{ font-size:24px; font-weight:700; color:{ORANGE}; }}

/* Buttons in the main area: orange accent, white text */
[data-testid="stMain"] .stButton > button, [data-testid="stMain"] .stFormSubmitButton > button {{
    background:{ORANGE}; color:#fff; border:1px solid {ORANGE};
    border-radius:8px; font-weight:600; padding: 0.5rem 1rem;
}}
[data-testid="stMain"] .stButton > button:hover, [data-testid="stMain"] .stFormSubmitButton > button:hover {{
    background:#e65f00; border-color:#e65f00; color:#fff;
}}
[data-testid="stMain"] .stButton > button p, [data-testid="stMain"] .stFormSubmitButton > button p {{ color:#fff; }}

/* Inputs & tables: keep rounded corners, let theme set colors */
div[data-baseweb="input"], div[data-baseweb="select"] > div {{ border-radius: 8px !important; }}
div[data-testid="stDataFrame"] {{ border:1px solid rgba(128,128,128,.28); border-radius:12px; overflow:hidden; }}
.stAlert {{ border-radius: 10px; }}
/* ===== LOGIN PAGE: minimal moving background ===== */
.login-bg {{ position: fixed; inset: 0; z-index: -1; pointer-events: none; overflow: hidden; --acc: 255,106,0; }}
.login-bg .ring {{ position: absolute; left: 50%; top: 47%; border-radius: 50%;
    border: 1px solid rgba(var(--acc), .22); transform: translate(-50%, -50%);
    animation: breathe 10s ease-in-out infinite; will-change: transform; }}
.login-bg .r1 {{ width: 520px; height: 520px; }}
.login-bg .r2 {{ width: 800px; height: 800px; border-color: rgba(var(--acc), .14); animation-delay: -3.3s; }}
.login-bg .r3 {{ width: 1100px; height: 1100px; border-color: rgba(var(--acc), .09); animation-delay: -6.6s; }}
.login-bg .orb {{ position: absolute; border-radius: 50%; background: rgba(var(--acc), .55);
    box-shadow: 0 0 18px rgba(var(--acc), .55); will-change: transform; }}
.login-bg .o1 {{ width: 9px; height: 9px; left: 21%; top: 32%; animation: drift 12s ease-in-out infinite alternate; }}
.login-bg .o2 {{ width: 6px; height: 6px; left: 79%; top: 64%; animation: drift 15s ease-in-out infinite alternate-reverse; }}
.login-bg .o3 {{ width: 7px; height: 7px; left: 70%; top: 24%; animation: drift 13s ease-in-out infinite alternate; }}
.login-bg .o4 {{ width: 5px; height: 5px; left: 28%; top: 72%; animation: drift 17s ease-in-out infinite alternate-reverse; }}
@keyframes breathe {{
    0%, 100% {{ transform: translate(-50%, -50%) scale(1); opacity: .95; }}
    50% {{ transform: translate(-50%, -50%) scale(1.07); opacity: .45; }}
}}
@keyframes drift {{ from {{ transform: translate(0, 0); }} to {{ transform: translate(26px, -48px); }} }}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.login-marker) {{
    background: rgba(128,128,128,.10); backdrop-filter: blur(14px); border-radius: 18px;
    box-shadow: 0 24px 60px rgba(0,0,0,.28); padding: 14px 16px 6px;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.login-marker) .section-title,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.login-marker) .section-sub {{ text-align: center; }}
.login-marker {{ height: 0; }}

/* Charts: hide the hover toolbar (its "Show data" button can leave a chart stuck on the data table) */
[data-testid="stElementContainer"]:has([data-testid="stVegaLiteChart"]) [data-testid="stElementToolbar"],
.stElementContainer:has([data-testid="stVegaLiteChart"]) [data-testid="stElementToolbar"] {{ display: none !important; }}

/* Tabs (Chart / Data) */
button[data-baseweb="tab"][aria-selected="true"] {{ color: #FF6A00 !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: #FF6A00 !important; }}

/* Chart/Data toggle + download buttons */
button[data-testid="stBaseButton-segmented_controlActive"] {{
    background: rgba(255,106,0,.18) !important; border-color: #FF6A00 !important; color: #FF6A00 !important; }}
[data-testid="stMain"] .stDownloadButton > button {{
    background: transparent; color: #FF6A00; border: 1px solid #FF6A00; border-radius: 8px; font-weight: 600; }}
[data-testid="stMain"] .stDownloadButton > button:hover {{ background: #FF6A00; color: #fff; }}
[data-testid="stMain"] .stDownloadButton > button:hover p {{ color: #fff; }}
[data-testid="stMain"] .stDownloadButton > button p {{ color: inherit; }}
[data-testid="stPopover"] > div > button {{ border-radius: 8px; font-weight: 600; }}

/* hide the 0-height theme-detector iframe */
.stElementContainer:has(iframe[height="0"]), div[data-testid="stElementContainer"]:has(iframe[height="0"]) {{
    position: absolute; height: 0; width: 0; overflow: hidden; margin: 0; padding: 0;
}}

/* ===== LIGHT MODE ONLY: soft sky-blue theme (dark mode untouched) ===== */
{LIGHT_CSS}
</style>
""", unsafe_allow_html=True)

try:
    import streamlit.components.v1 as _components
    _components.html(THEME_JS, height=0)
except Exception:
    pass  # falls back to the browser's light/dark setting


# --- 3. DATABASE (PostgreSQL) ---
@st.cache_resource(show_spinner=False)
def _make_engine(db_url):
    # One shared connection pool for the whole server (no new SSL handshake per click)
    return create_engine(db_url, pool_size=5, max_overflow=5, pool_pre_ping=True, pool_recycle=300)


def get_engine():
    if "DATABASE_URL" not in st.secrets:
        st.error("🚨 **DATABASE_URL is missing!** Please add it in your Streamlit Cloud App Settings -> Secrets.")
        st.stop()

    db_url = st.secrets["DATABASE_URL"]
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    if "?" not in db_url:
        db_url += "?sslmode=require"
    elif "sslmode" not in db_url:
        db_url += "&sslmode=require"

    return _make_engine(db_url)


SCHEMA_VERSION = 4  # bump this whenever tables/columns change so setup re-runs


@st.cache_resource(show_spinner=False)
def init_db(schema_version=None):
    # Runs ONCE per server process instead of on every click
    engine = get_engine()
    with engine.begin() as conn:
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER,
                price REAL,
                min_threshold INTEGER DEFAULT 5,
                unit TEXT DEFAULT 'Pcs.',
                description TEXT DEFAULT ''
            )
        """)
        conn.exec_driver_sql("ALTER TABLE items ADD COLUMN IF NOT EXISTS unit TEXT DEFAULT 'Pcs.'")
        conn.exec_driver_sql("ALTER TABLE items ADD COLUMN IF NOT EXISTS description TEXT DEFAULT ''")
        conn.exec_driver_sql("ALTER TABLE items ADD COLUMN IF NOT EXISTS min_threshold INTEGER DEFAULT 5")
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id SERIAL PRIMARY KEY,
                ts TIMESTAMPTZ DEFAULT NOW(),
                username TEXT,
                action TEXT,
                item_id INTEGER,
                item_name TEXT,
                details TEXT
            )
        """)
        conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                expires_at TIMESTAMPTZ NOT NULL
            )
        """)
    return True


CATEGORIES = ["Hardware / Peripherals", "Office Supplies", "Networking Equipment",
              "Furniture & Fixtures", "ICT Equipment"]
FIELD_LABELS = {"name": "Item", "category": "Category", "quantity": "Qty", "unit": "Unit",
                "price": "Price", "min_threshold": "Min", "description": "Description"}
NUMERIC_FIELDS = {"quantity", "price", "min_threshold"}
UNITS = ["Reams", "Pcs.", "Boxes", "Packs", "Bottles", "Gallons", "Rolls",
         "Sets", "Pairs", "Cartridges", "Units"]


def _log(conn, action, item_id=None, item_name=None, details="", username=None):
    conn.exec_driver_sql(
        "INSERT INTO activity_log (username, action, item_id, item_name, details) VALUES (%s, %s, %s, %s, %s)",
        (username or st.session_state.get("user", "system"), action, item_id, item_name, details),
    )


def log_activity(action, **kw):
    with get_engine().begin() as conn:
        _log(conn, action, **kw)


def add_item(name, category, quantity, price, min_threshold, unit="Pcs.", description=""):
    with get_engine().begin() as conn:
        new_id = conn.exec_driver_sql(
            "INSERT INTO items (name, category, quantity, price, min_threshold, unit, description) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (name, category, quantity, price, min_threshold, unit, description),
        ).scalar()
        _log(conn, "ADD_ITEM", new_id, name, f"{quantity} {unit} @ ₱{price:,.2f} · {category}")
    st.cache_data.clear()


@st.cache_data(ttl=300, show_spinner=False)
def get_inventory():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM items ORDER BY id ASC", engine)
    df["unit"] = df["unit"].fillna("Pcs.")
    df["description"] = df["description"].fillna("")
    df["amount"] = df["quantity"] * df["price"]
    return df


def update_quantity(item_id, new_quantity):
    with get_engine().begin() as conn:
        row = conn.exec_driver_sql("SELECT name, quantity, unit FROM items WHERE id = %s", (item_id,)).fetchone()
        conn.exec_driver_sql("UPDATE items SET quantity = %s WHERE id = %s", (new_quantity, item_id))
        if row:
            _log(conn, "UPDATE_STOCK", item_id, row[0], f"{row[1]} → {new_quantity} {row[2]}")
    st.cache_data.clear()


def delete_item(item_id):
    with get_engine().begin() as conn:
        row = conn.exec_driver_sql("SELECT name, quantity, unit FROM items WHERE id = %s", (item_id,)).fetchone()
        conn.exec_driver_sql("DELETE FROM items WHERE id = %s", (item_id,))
        if row:
            _log(conn, "DELETE_ITEM", item_id, row[0], f"Removed {row[1]} {row[2]} from inventory")
    st.cache_data.clear()


def _same(col, a, b):
    if col in NUMERIC_FIELDS:
        try:
            return float(a) == float(b)
        except (TypeError, ValueError):
            return False
    return str(_clean(a)).strip() == str(_clean(b)).strip()


def validate_edits(edited):
    errs = []
    for _, r in edited.iterrows():
        tag = f"Item #{int(r['id'])}"
        if not str(_clean(r["name"])).strip():
            errs.append(f"{tag}: the item name cannot be empty.")
        for c in ("quantity", "price", "min_threshold"):
            if pd.isna(r[c]) or float(r[c]) < 0:
                errs.append(f"{tag}: {FIELD_LABELS[c]} must be a number of 0 or more.")
    return errs


def save_item_edits(orig, edited):
    """Save every row that was changed and write one activity-log line per item."""
    n = 0
    with get_engine().begin() as conn:
        for _, new in edited.iterrows():
            old = orig[orig["id"] == new["id"]]
            if old.empty:
                continue
            old = old.iloc[0]
            diffs = [f"{FIELD_LABELS[c]}: {_clean(old[c])} → {_clean(new[c])}"
                     for c in FIELD_LABELS if not _same(c, old[c], new[c])]
            if not diffs:
                continue
            conn.exec_driver_sql(
                "UPDATE items SET name=%s, category=%s, quantity=%s, unit=%s, price=%s, "
                "min_threshold=%s, description=%s WHERE id=%s",
                (str(new["name"]).strip(), _clean(new["category"]) or None, int(new["quantity"]),
                 str(_clean(new["unit"])).strip() or "Pcs.", float(new["price"]), int(new["min_threshold"]),
                 str(_clean(new["description"])).strip(), int(new["id"])))
            _log(conn, "EDIT_ITEM", int(new["id"]), str(new["name"]).strip(), "; ".join(diffs)[:500])
            n += 1
    if n:
        st.cache_data.clear()
    return n


# --- 3b. SECURITY: accounts, login, lockout, activity log ---
REMEMBER_DAYS = 30        # a device stays signed in this long (renewed each time it is used)
COOKIE_NAME = "dictnir_session"
MAX_ATTEMPTS = 5          # wrong passwords before the account is locked
LOCK_MINUTES = 5
USERNAME_RE = re.compile(r"^[a-z0-9._-]{3,30}$")

ACTION_LABELS = {
    "LOGIN": "Signed in", "LOGOUT": "Signed out", "SESSION_EXPIRED": "Session expired",
    "LOGIN_FAILED": "Failed sign-in", "LOGIN_BLOCKED": "Blocked (locked account)",
    "ADD_ITEM": "Added item", "UPDATE_STOCK": "Changed stock", "DELETE_ITEM": "Deleted item",
    "EDIT_ITEM": "Edited item", "CREATE_USER": "Created account", "DELETE_USER": "Deleted account", "CHANGE_PASSWORD": "Changed password",
}


def hash_password(password, iterations=310_000):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"


def verify_password(password, stored):
    try:
        _, iters, salt, digest = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iters))
        return hmac.compare_digest(dk.hex(), digest)
    except Exception:
        return False


@st.cache_resource(show_spinner=False)
def dummy_hash():
    return hash_password("not-a-real-password")


def count_users():
    with get_engine().begin() as conn:
        return conn.exec_driver_sql("SELECT COUNT(*) FROM users").scalar()


def get_user(username):
    with get_engine().begin() as conn:
        r = conn.exec_driver_sql(
            "SELECT username, full_name, password_hash, failed_attempts, locked_until FROM users WHERE username = %s",
            (username,)).fetchone()
    return dict(r._mapping) if r else None


def set_attempts(username, attempts, locked_until):
    with get_engine().begin() as conn:
        conn.exec_driver_sql("UPDATE users SET failed_attempts = %s, locked_until = %s WHERE username = %s",
                             (attempts, locked_until, username))


def create_user(username, full_name, password):
    with get_engine().begin() as conn:
        conn.exec_driver_sql("INSERT INTO users (username, full_name, password_hash) VALUES (%s, %s, %s)",
                             (username, full_name, hash_password(password)))


def list_users():
    return pd.read_sql("SELECT username, full_name, created_at, locked_until FROM users ORDER BY created_at", get_engine())


def get_activity(limit=500):
    df = pd.read_sql(
        f"SELECT ts, username, action, item_name, details FROM activity_log ORDER BY id DESC LIMIT {int(limit)}",
        get_engine())
    if not df.empty:
        df["ts"] = (pd.to_datetime(df["ts"], utc=True).dt.tz_convert("Asia/Manila")
                    .dt.strftime("%b %d, %Y  %I:%M %p"))
        df["action"] = df["action"].map(lambda a: ACTION_LABELS.get(a, a))
    return df


def _th(token):
    return hashlib.sha256(token.encode()).hexdigest()  # only the hash is stored in the database


def create_session(username):
    token = secrets.token_urlsafe(32)
    with get_engine().begin() as conn:
        conn.exec_driver_sql("DELETE FROM sessions WHERE expires_at < NOW()")
        conn.exec_driver_sql(
            "INSERT INTO sessions (token_hash, username, expires_at) VALUES (%s, %s, NOW() + make_interval(days => %s))",
            (_th(token), username, REMEMBER_DAYS))
    return token


def lookup_session(token):
    with get_engine().begin() as conn:
        r = conn.exec_driver_sql(
            "SELECT u.username, u.full_name FROM sessions s JOIN users u ON u.username = s.username "
            "WHERE s.token_hash = %s AND s.expires_at > NOW()", (_th(token),)).fetchone()
        if r:  # keep an actively used device signed in (write at most about once a day)
            conn.exec_driver_sql(
                "UPDATE sessions SET expires_at = NOW() + make_interval(days => %s) "
                "WHERE token_hash = %s AND expires_at < NOW() + make_interval(days => %s)",
                (REMEMBER_DAYS, _th(token), REMEMBER_DAYS - 1))
    return dict(r._mapping) if r else None


def delete_session(token):
    with get_engine().begin() as conn:
        conn.exec_driver_sql("DELETE FROM sessions WHERE token_hash = %s", (_th(token),))


def _cookie_token():
    try:
        return st.context.cookies.get(COOKIE_NAME)
    except Exception:
        return None


SESSION_HTML = r"""<!doctype html><html><body style="margin:0"><script>
(function () {
  var KEY = 'dictnir_token', DAYS = %DAYS%, sent = false, lastNonce = null;
  function post(type, extra) {
    var m = { isStreamlitMessage: true, type: type };
    for (var k in extra) m[k] = extra[k];
    window.parent.postMessage(m, '*');
  }
  function save(t) { try { localStorage.setItem(KEY, JSON.stringify({ t: t, e: Date.now() + DAYS * 864e5 })); } catch (e) {} }
  function read() {
    try {
      var o = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (!o || !o.t || o.e < Date.now()) { localStorage.removeItem(KEY); return null; }
      save(o.t);                       // renew: an actively used device stays signed in
      return o.t;
    } catch (e) { return null; }
  }
  window.addEventListener('message', function (ev) {
    var d = ev.data;
    if (!d || d.type !== 'streamlit:render') return;
    var a = d.args || {};
    if (a.action && a.nonce !== lastNonce) {
      lastNonce = a.nonce;
      if (a.action === 'set') save(a.token);
      if (a.action === 'clear') { try { localStorage.removeItem(KEY); } catch (e) {} }
    }
    if (!sent) { sent = true; post('streamlit:setComponentValue', { value: { token: read() }, dataType: 'json' }); }
  });
  post('streamlit:componentReady', { apiVersion: 1 });
  post('streamlit:setFrameHeight', { height: 0 });
})();
</script></body></html>""".replace("%DAYS%", str(REMEMBER_DAYS))


@st.cache_resource(show_spinner=False)
def _session_component():
    """Tiny invisible component that remembers the sign-in token in THIS browser (localStorage)."""
    try:
        import streamlit.components.v1 as comps
        d = Path(tempfile.gettempdir()) / "dictnir_session_component"
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(SESSION_HTML, encoding="utf-8")
        return comps.declare_component("dictnir_session", path=str(d))
    except Exception:
        return None


def waiting_view():
    st.markdown("<div style='text-align:center; margin-top:28vh'><div class='page-title'>Loading…</div>"
                "<div class='section-sub'>Checking this device</div></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.button("Taking too long? Go to sign in", use_container_width=True,
                  on_click=lambda: st.session_state.update(skip_restore=True))


def restore_session(sess=None):
    """Page reload on a device that is already signed in: no password needed again."""
    token = (sess.get("token") if isinstance(sess, dict) else None) or _cookie_token()
    row = lookup_session(token) if token else None
    if not row:
        return False
    st.session_state.update(user=row["username"], full_name=row["full_name"], session_token=token)
    return True


def _cookie_js(action, token=None):
    secs = REMEMBER_DAYS * 86400 if action == "set" else 0
    js = ("<script>(function(){try{var P=window.parent;var s=P.location.protocol==='https:'?'; Secure':'';"
          "P.document.cookie=" + json.dumps(COOKIE_NAME) + "+'='+" + json.dumps(token or "") +
          "+'; max-age=" + str(secs) + "; path=/; SameSite=Lax'+s;}catch(e){}})();</script>")
    try:
        _components.html(js, height=0)
    except Exception:
        pass


def attempt_login(username, password):
    username = username.strip().lower()
    user = get_user(username) if USERNAME_RE.match(username) else None
    now = datetime.now(timezone.utc)
    attempts = user["failed_attempts"] if user else 0

    if user and user["locked_until"]:
        if user["locked_until"] > now:
            mins = max(1, -(-int((user["locked_until"] - now).total_seconds()) // 60))
            log_activity("LOGIN_BLOCKED", username=username, details="Account is temporarily locked")
            return False, f"Too many failed attempts. Try again in {mins} minute(s)."
        attempts = 0  # lock expired

    ok = verify_password(password, user["password_hash"] if user else dummy_hash()) and user is not None
    if ok:
        set_attempts(username, 0, None)
        token = create_session(username)
        st.session_state.update(user=username, full_name=user["full_name"], session_token=token,
                                cookie_cmd=("set", token))
        log_activity("LOGIN", username=username)
        return True, ""

    if user:
        attempts += 1
        locked = now + timedelta(minutes=LOCK_MINUTES) if attempts >= MAX_ATTEMPTS else None
        set_attempts(username, attempts, locked)
    log_activity("LOGIN_FAILED", username=username[:40] or "?", details="Wrong username or password")
    return False, "Invalid username or password."


def logout(reason="LOGOUT"):
    user = st.session_state.get("user")
    token = st.session_state.pop("session_token", None) or _cookie_token()
    if token:
        delete_session(token)
    if user:
        log_activity(reason, username=user)
    for k in ("user", "full_name", "nav"):
        st.session_state.pop(k, None)
    st.session_state["cookie_cmd"] = ("clear", None)


def password_problem(pw, confirm):
    if len(pw) < 8:
        return "Password must be at least 8 characters."
    if pw != confirm:
        return "Passwords do not match."
    return None


def _form(key):
    try:
        return st.form(key, border=False)  # no second border inside the card
    except TypeError:
        return st.form(key)


def login_view():
    try:
        first_run = count_users() == 0
    except ProgrammingError:  # tables missing (setup was cached before they existed) -> create them now
        init_db.clear()
        init_db(SCHEMA_VERSION)
        first_run = count_users() == 0
    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown(f"""
            <div class="brand" style="justify-content:center; margin-top:6vh">
                <div class="brand-logo"></div>
                <div><div class="brand-name">DICT NIR</div>
                <div class="brand-sub">Office Property & Supplies</div></div>
            </div>""", unsafe_allow_html=True)
        msg = st.session_state.pop("login_msg", None)
        st.markdown("""<div class="login-bg"><div class="ring r1"></div><div class="ring r2"></div>
            <div class="ring r3"></div><div class="orb o1"></div><div class="orb o2"></div>
            <div class="orb o3"></div><div class="orb o4"></div></div>""", unsafe_allow_html=True)
        if msg:
            getattr(st, msg[0])(msg[1])

        with st.container(border=True):
            st.markdown('<div class="login-marker"></div>', unsafe_allow_html=True)
            if first_run:
                st.markdown("<div class='section-title'>Create the first account</div>"
                            "<div class='section-sub'>No accounts exist yet. This first account will be used to sign in "
                            "and add others.</div>", unsafe_allow_html=True)
                with _form("setup_form"):
                    full_name = st.text_input("Full name")
                    username = st.text_input("Username", placeholder="letters, numbers, . _ -")
                    pw = st.text_input("Password (min. 8 characters)", type="password")
                    pw2 = st.text_input("Confirm password", type="password")
                    code = st.text_input("Setup code", type="password") if "SETUP_CODE" in st.secrets else None
                    if st.form_submit_button("Create account", use_container_width=True):
                        u = username.strip().lower()
                        if "SETUP_CODE" in st.secrets and not hmac.compare_digest(code or "", str(st.secrets["SETUP_CODE"])):
                            st.error("Incorrect setup code.")
                        elif not full_name.strip() or not USERNAME_RE.match(u):
                            st.error("Enter your name and a username of 3-30 letters, numbers, . _ -")
                        elif password_problem(pw, pw2):
                            st.error(password_problem(pw, pw2))
                        else:
                            create_user(u, full_name.strip(), pw)
                            log_activity("CREATE_USER", username=u, details="First account created")
                            st.session_state["login_msg"] = ("success", "Account created. Please sign in.")
                            st.rerun()
            else:
                st.markdown("<div class='section-title'>Sign in</div>"
                            "<div class='section-sub'>Authorized personnel only.</div>", unsafe_allow_html=True)
                with _form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Sign in", use_container_width=True):
                        ok, err = attempt_login(username, password)
                        if ok:
                            st.rerun()
                        else:
                            st.error(err)


# --- 3c. EXPORTS: Excel / PDF / Word ---
PH_TZ = timezone(timedelta(hours=8))


def _clean(v):
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return ""
    return v.item() if hasattr(v, "item") else v


def _rows(df, money_cols):
    out = []
    for rec in df.itertuples(index=False):
        row = []
        for col, v in zip(df.columns, rec):
            v = _clean(v)
            row.append(f"{v:,.2f}" if (col in money_cols and v != "") else str(v))
        out.append(row)
    return out


def build_excel(title, subtitle, df, money_cols, total=None):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Report"
    n = len(df.columns)
    ws["A1"] = title
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = subtitle
    ws["A2"].font = Font(italic=True, color="666666")
    for j, c in enumerate(df.columns, 1):
        cell = ws.cell(row=4, column=j, value=c)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="FF6A00")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for i, rec in enumerate(df.itertuples(index=False), 5):
        for j, (c, v) in enumerate(zip(df.columns, rec), 1):
            cell = ws.cell(row=i, column=j, value=_clean(v))
            if c in money_cols:
                cell.number_format = '"₱"#,##0.00'
    if total is not None:
        r = 4 + len(df) + 2
        ws.cell(row=r, column=max(n - 1, 1), value="TOTAL BALANCE").font = Font(bold=True)
        t = ws.cell(row=r, column=n, value=float(total))
        t.font = Font(bold=True)
        t.number_format = '"₱"#,##0.00'
    for j, c in enumerate(df.columns, 1):
        longest = max([len(str(c))] + [len(str(_clean(v))) for v in df.iloc[:, j - 1]])
        ws.column_dimensions[get_column_letter(j)].width = min(max(longest + 3, 8), 50)
    ws.freeze_panes = "A5"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def build_word(title, subtitle, df, money_cols, total=None):
    from docx import Document
    from docx.enum.section import WD_ORIENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor

    def shade(cell, fill):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fill)
        tcPr.append(shd)

    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = sec.page_height, sec.page_width
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Inches(0.6))
    doc.add_heading(title, level=1)
    sub = doc.add_paragraph()
    sub.add_run(subtitle).italic = True

    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"
    for j, c in enumerate(df.columns):
        cell = table.rows[0].cells[j]
        cell.text = ""
        run = cell.paragraphs[0].add_run(str(c))
        run.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(255, 255, 255)
        shade(cell, "FF6A00")
    for row in _rows(df, money_cols):
        cells = table.add_row().cells
        for j, (c, v) in enumerate(zip(df.columns, row)):
            cells[j].text = ""
            par = cells[j].paragraphs[0]
            par.add_run(v).font.size = Pt(8.5)
            if c in money_cols:
                par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if total is not None:
        par = doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = par.add_run(f"TOTAL BALANCE: ₱{total:,.2f}")
        run.bold = True
        run.font.size = Pt(12)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def build_pdf(title, subtitle, df, money_cols, total=None):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    def t(x):  # built-in PDF fonts have no peso sign
        return escape(str(x).replace("₱", "PHP "))

    ss = getSampleStyleSheet()
    cell = ParagraphStyle("c", parent=ss["Normal"], fontSize=7.5, leading=9)
    cell_r = ParagraphStyle("cr", parent=cell, alignment=2)
    head = ParagraphStyle("h", parent=cell, textColor=colors.white, fontName="Helvetica-Bold")
    page_w = landscape(A4)[0]

    rows = _rows(df, money_cols)
    data = [[Paragraph(t(c), head) for c in df.columns]]
    for row in rows:
        data.append([Paragraph(t(v), cell_r if c in money_cols else cell) for c, v in zip(df.columns, row)])
    weights = [min(max([len(str(c))] + [len(r[j]) for r in rows]), 40) + 4 for j, c in enumerate(df.columns)]
    widths = [(page_w - 56) * w / sum(weights) for w in weights]

    tbl = Table(data, colWidths=widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FF6A00")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF4EB")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story = [Paragraph(f"<b>{t(title)}</b>", ParagraphStyle("t", parent=ss["Title"], alignment=0, fontSize=18)),
             Paragraph(t(subtitle), ss["Normal"]), Spacer(1, 10), tbl]
    if total is not None:
        story += [Spacer(1, 8), Paragraph(f"<b>TOTAL BALANCE: PHP {total:,.2f}</b>",
                                          ParagraphStyle("tt", parent=ss["Normal"], alignment=2, fontSize=11))]

    def footer(canvas, d):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(28, 18, "DICT NIR - Inventory System")
        canvas.drawRightString(page_w - 28, 18, f"Page {d.page}")

    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=28, rightMargin=28, topMargin=30,
                      bottomMargin=34, title=title).build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()


def report_subtitle(extra=""):
    now = datetime.now(PH_TZ).strftime("%B %d, %Y %I:%M %p")
    who = st.session_state.get("full_name", "")
    return f"DICT Negros Island Region · Generated {now} (PH time) by {who}" + (f" · {extra}" if extra else "")


def export_menu(title, subtitle, df, money_cols, total=None, base="report", key="exp"):
    """Popover with Excel / PDF / Word downloads. Files are built only when you click a button."""
    stamp = datetime.now(PH_TZ).strftime("%Y%m%d-%H%M")
    try:
        pop = st.popover("Export report", icon=":material/download:")
    except TypeError:
        pop = st.popover("Export report")
    with pop:
        st.caption("Exports exactly what is shown in the table above.")
        formats = [
            ("Excel (.xlsx)", build_excel, "openpyxl", "xlsx",
             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("PDF (.pdf)", build_pdf, "reportlab", "pdf", "application/pdf"),
            ("Word (.docx)", build_word, "docx", "docx",
             "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ]
        for label, builder, module, ext, mime in formats:
            if importlib.util.find_spec(module) is None:
                pkg = {"docx": "python-docx"}.get(module, module)
                st.caption(f"{label}: add `{pkg}` to requirements.txt")
                continue
            make = partial(builder, title, subtitle, df, money_cols, total)
            fname, k = f"{base}-{stamp}.{ext}", f"{key}_{ext}"
            try:
                st.download_button(label, data=make, file_name=fname, mime=mime, key=k,
                                   on_click="ignore", use_container_width=True)
            except Exception:  # older Streamlit: build the file up front
                st.download_button(label, data=make(), file_name=fname, mime=mime, key=k,
                                   use_container_width=True)


# --- 4. UI HELPERS ---
def metric_card(label, value, badge_text, badge_class):
    st.markdown(f"""
        <div class="card">
            <div class="card-label">{label}</div>
            <div class="card-value">{value}</div>
            <span class="badge {badge_class}">{badge_text}</span>
        </div>
    """, unsafe_allow_html=True)


def total_bar(df_view, label="TOTAL BALANCE"):
    total = df_view["amount"].sum() if len(df_view) else 0
    qty = int(df_view["quantity"].sum()) if len(df_view) else 0
    st.markdown(f"""
        <div class="total-bar">
            <div><div class="t-label">{label}</div>
                 <div class="t-sub">{len(df_view)} item(s) · {qty:,} total quantity</div></div>
            <div class="t-amount">₱{total:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)


def go_to(page):
    st.session_state["nav"] = page


def flash(kind, msg):
    st.session_state["flash"] = (kind, msg)


def show_flash():
    f = st.session_state.pop("flash", None)
    if f:
        getattr(st, f[0])(f[1])


def do_update(item_id, qty, name):
    update_quantity(item_id, qty)
    flash("success", f"Updated stock for **{name}**.")


def do_delete(item_id, name):
    delete_item(item_id)
    flash("success", f"Deleted **{name}**.")


fragment = getattr(st, "fragment", None) or (lambda f: f)  # older Streamlit: no fragments


@fragment
def inventory_records(df, search_query):
    """Filters only rerun THIS block, not the whole dashboard."""
    low_mask = df["quantity"] <= df["min_threshold"]
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Inventory Records</div>", unsafe_allow_html=True)
    f1, f2 = st.columns([2, 1])
    with f1:
        name_filter = st.text_input("Filter by name", search_query, placeholder="Item name")
    with f2:
        cats = ["All"] + list(df["category"].dropna().unique())
        cat_filter = st.selectbox("Category", cats)

    view = df
    if name_filter:
        view = view[view["name"].str.contains(name_filter, case=False, na=False)]
    if cat_filter != "All":
        view = view[view["category"] == cat_filter]
    view = view.assign(status=low_mask.loc[view.index].map({True: "🔴 Low stock", False: "🟢 In stock"}))
    view = view[["id", "quantity", "unit", "name", "description", "category",
                 "price", "amount", "min_threshold", "status"]]
    st.dataframe(
        view, use_container_width=True, hide_index=True,
        column_config={
            "id": "ID", "quantity": "Qty", "unit": "Unit", "name": "Item",
            "description": "Description", "category": "Category",
            "price": st.column_config.NumberColumn("Unit Price", format="₱%.2f"),
            "amount": st.column_config.NumberColumn("Amount", format="₱%.2f"),
            "min_threshold": "Min", "status": "Status",
        },
    )
    total_bar(view)

    exp = view.reset_index(drop=True)[["quantity", "unit", "name", "description", "category", "price", "amount"]]
    exp.insert(0, "No.", range(1, len(exp) + 1))
    exp.columns = ["No.", "Qty", "Unit", "Item", "Description", "Category", "Unit Price (₱)", "Amount (₱)"]
    flt = " · ".join(x for x in [f"Item: {name_filter}" if name_filter else "",
                                  f"Category: {cat_filter}" if cat_filter != "All" else ""] if x)
    export_menu("Inventory Report", report_subtitle(flt), exp, {"Unit Price (₱)", "Amount (₱)"},
                total=float(view["amount"].sum()), base="inventory-report", key="exp_inv")


def data_view(agg, key):
    t = agg.sort_values("value", ascending=False)[["category", "value", "pct"]]
    st.dataframe(t, hide_index=True, use_container_width=True, height=300, column_config={
        "category": "Category",
        "value": st.column_config.NumberColumn("Value", format="₱%.2f"),
        "pct": st.column_config.NumberColumn("Share", format="%.1f%%")})
    st.download_button("Download CSV", t.to_csv(index=False).encode(), file_name="stock-by-category.csv",
                       mime="text/csv", key=f"csv_{key}", on_click="ignore")


def bar_panel(agg):
    st.markdown("<div class='card-label'>Analytics</div>"
                "<div class='section-title'>Value by Category</div>", unsafe_allow_html=True)
    tab_chart, tab_data = st.tabs(["Chart", "Data"])  # tabs switch in the browser: instant
    with tab_chart:
        base = alt.Chart(agg).encode(
            x=alt.X("category:N", sort=None, title=None, axis=alt.Axis(labelAngle=0, labelLimit=120)),
            y=alt.Y("value:Q", title=None, axis=alt.Axis(format="~s", gridDash=[4, 4])),
        )
        bars = base.mark_bar(color=ORANGE, cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=48)
        labels = base.mark_text(color="white", fontWeight="bold", dy=14).encode(text="label:N")
        st.altair_chart((bars + labels).properties(height=320, background="transparent"), use_container_width=True)
    with tab_data:
        data_view(agg, "bar")


def donut_panel(agg):
    st.markdown("<div class='section-title'>Stock by Category</div>", unsafe_allow_html=True)
    tab_chart, tab_data = st.tabs(["Chart", "Data"])
    with tab_chart:
        donut = alt.Chart(agg).mark_arc(innerRadius=62, outerRadius=95).encode(
            theta="value:Q",
            color=alt.Color("category:N", legend=None, scale=alt.Scale(range=PALETTE)),
            tooltip=["category", alt.Tooltip("value:Q", format=",.2f")],
        ).properties(height=200, background="transparent")
        st.altair_chart(donut, use_container_width=True)
        rows = ""
        for _, r in agg.sort_values("value", ascending=False).head(4).iterrows():
            rows += (f"<div class='area-row'><span><b>{r['pct']:.0f}%</b>{r['category']}</span>"
                     f"<span>₱{r['value']:,.0f}</span></div>")
        st.markdown(f"<div class='card-label' style='margin-top:6px'>Top 4 Categories</div>{rows}",
                    unsafe_allow_html=True)
    with tab_data:
        data_view(agg, "donut")


PAGES = ["Dashboard", "Add Item", "Restock / Adjust", "Remove Item", "Security"]


def page_header(title, subtitle=None):
    st.markdown(f"<div class='page-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-sub'>{subtitle}</div>", unsafe_allow_html=True)


# --- 5. MAIN APP ---
def main():
    init_db(SCHEMA_VERSION)

    # this device's "stay signed in" memory (set on sign-in, cleared on sign-out)
    comp = _session_component()
    cmd = st.session_state.pop("cookie_cmd", None) or (None, None)
    sess = None
    if comp is not None:
        sess = comp(action=cmd[0], token=cmd[1], nonce=(str(time.time()) if cmd[0] else None),
                    key="dictnir_sess", default=None)
    elif cmd[0]:
        _cookie_js(*cmd)          # fallback if the component could not start

    # ---- security gate: nothing below runs unless signed in ----
    if "user" not in st.session_state and not restore_session(sess):
        if comp is not None and sess is None and not st.session_state.get("skip_restore"):
            waiting_view()        # the browser is still reporting what it remembers (about a second)
            return
        login_view()
        return

    # Sidebar
    st.sidebar.markdown(f"""
        <div class="brand">
            <div class="brand-logo"></div>
            <div>
                <div class="brand-name">DICT NIR</div>
                <div class="brand-sub">Office Property & Supplies</div>
            </div>
        </div>
        <div class="side-divider"></div>
        <div class="menu-label">Main Menu</div>
    """, unsafe_allow_html=True)

    if "nav" not in st.session_state:
        st.session_state["nav"] = PAGES[0]
    nav_items = {
        "Dashboard": ("Dashboard", ":material/dashboard:"),
        "Add Item": ("Add Item", ":material/add_box:"),
        "Restock / Adjust": ("Restock / Adjust", ":material/inventory_2:"),
        "Remove Item": ("Remove Item", ":material/delete:"),
        "Security": ("Security", ":material/shield:"),
    }
    choice = st.session_state["nav"]
    for p, (label, icon) in nav_items.items():
        kwargs = dict(key=f"nav_{p}", use_container_width=True,
                      type="primary" if choice == p else "secondary",
                      on_click=go_to, args=(p,))
        try:
            st.sidebar.button(label, icon=icon, **kwargs)
        except TypeError:  # older Streamlit without icon support
            st.sidebar.button(label, **kwargs)

    st.sidebar.markdown(f"""
        <div class="side-foot">
            <div class="live"><span class="dot"></span>System online</div>
            <div class="foot-title">{html.escape(st.session_state.get("full_name", ""))}</div>
            <div class="foot-sub">Signed in · DICT Negros Island Region</div>
        </div>
    """, unsafe_allow_html=True)
    try:
        st.sidebar.button("Sign out", icon=":material/logout:", key="signout", use_container_width=True,
                          on_click=logout)
    except TypeError:
        st.sidebar.button("Sign out", key="signout", use_container_width=True, on_click=logout)

    df = get_inventory()

    # ================= DASHBOARD =================
    if choice == "Dashboard":
        # Top bar: search + Add New Item
        top_search, top_btn = st.columns([6, 1.2])
        with top_search:
            search_query = st.text_input("Search", placeholder="Search item name...",
                                         label_visibility="collapsed")
        with top_btn:
            try:
                st.button("Add New Item", icon=":material/add:", use_container_width=True,
                          on_click=go_to, args=("Add Item",))
            except TypeError:  # older Streamlit without icon support
                st.button("Add New Item", use_container_width=True, on_click=go_to, args=("Add Item",))

        page_header("Key Metrics", "DICT Negros Island Region · Office supply & property inventory")

        if df.empty:
            st.info("No inventory records yet. Click **Add New Item** to register supplies or hardware.")
            return

        df["value"] = df["quantity"] * df["price"]
        total_qty = int(df["quantity"].sum())
        total_value = df["value"].sum()
        low_df = df[df["quantity"] <= df["min_threshold"]]

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Total Stock Quantity", f"{total_qty:,} units",
                        f"{len(df)} item types", "badge-green")
        with c2:
            metric_card("Total Asset Valuation", f"₱{total_value:,.2f}",
                        f"{df['category'].nunique()} categories", "badge-orange")
        with c3:
            cls = "badge-red" if len(low_df) else "badge-green"
            txt = "Needs restocking" if len(low_df) else "All stocked"
            metric_card("Low Stock Items", f"{len(low_df)}", txt, cls)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        # Chart + category breakdown
        agg = (df.groupby("category", dropna=True)["value"].sum().reset_index()
                 .sort_values("value"))
        agg["pct"] = agg["value"] / agg["value"].sum() * 100
        agg["label"] = agg["pct"].round().astype(int).astype(str) + "%"

        left, right = st.columns([2, 1])
        with left.container(border=True):
            bar_panel(agg)
        with right.container(border=True):
            donut_panel(agg)

        # Top valued items
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Top Items by Value</div>", unsafe_allow_html=True)
        top = df.sort_values("value", ascending=False).head(5).copy()
        top.insert(0, "Rank", [f"Rank {i}" for i in range(1, len(top) + 1)])
        top = top[["Rank", "name", "id", "category", "quantity", "unit", "value"]]
        st.dataframe(
            top, use_container_width=True, hide_index=True,
            column_config={
                "name": "Product", "id": "Item ID", "category": "Category",
                "quantity": "Qty", "unit": "Unit",
                "value": st.column_config.NumberColumn("Value", format="₱%.2f"),
            },
        )

        inventory_records(df, search_query)
        if len(low_df):
            st.warning("**Attention:** some items are at or below their minimum level. Please arrange restocking.")

    # ================= ADD ITEM =================
    elif choice == "Add Item":
        page_header("Register New Item",
                    "Add office equipment, hardware, or consumable supplies to the inventory.")
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item name", placeholder="e.g., Copy Paper A4")
                category = st.selectbox("Category", ["Hardware / Peripherals", "Office Supplies",
                                                      "Networking Equipment", "Furniture & Fixtures",
                                                      "ICT Equipment"])
                quantity = st.number_input("Initial quantity", min_value=0, step=1)
                description = st.text_area("Description (optional)", height=100,
                                           placeholder="e.g., Legal size, 70gsm, 500 sheets per ream")
            with col2:
                unit = st.selectbox("Unit", UNITS)
                custom_unit = st.text_input("Other unit (optional)", placeholder="Type a unit not in the list")
                price = st.number_input("Unit price (₱)", min_value=0.0, format="%.2f")
                min_threshold = st.number_input("Low stock threshold", min_value=1, value=5, step=1)
            if st.form_submit_button("Save item", use_container_width=True):
                if not name.strip():
                    st.error("Item name is required.")
                else:
                    final_unit = custom_unit.strip() or unit
                    add_item(name.strip(), category, quantity, price, min_threshold,
                             final_unit, description.strip())
                    st.success(f"Saved **{name}** to the inventory.")

    # ================= RESTOCK =================
    elif choice == "Restock / Adjust":
        page_header("Restock / Adjust Stock",
                    "Correct mistakes in the table, or update quantities when shipments arrive or items are issued.")
        show_flash()
        if df.empty:
            st.info("No items available to update.")
        else:
            st.markdown("<div class='section-sub'>Made a typo? Click any cell to correct it, then press "
                        "<b>Save changes</b>.</div>", unsafe_allow_html=True)
            cols = ["id", "quantity", "unit", "name", "description", "category", "price", "min_threshold", "amount"]
            unit_opts = UNITS + sorted(set(df["unit"]) - set(UNITS))
            cat_opts = CATEGORIES + sorted(set(df["category"].dropna()) - set(CATEGORIES))
            ver = st.session_state.get("editor_v", 0)
            with _form("edit_items_form"):
                edited = st.data_editor(
                    df[cols], key=f"stock_editor_{ver}", hide_index=True, use_container_width=True,
                    num_rows="fixed", disabled=["id", "amount"],
                    column_config={
                        "id": "ID",
                        "quantity": st.column_config.NumberColumn("Qty", min_value=0, step=1, format="%d"),
                        "unit": st.column_config.SelectboxColumn("Unit", options=unit_opts, required=True),
                        "name": st.column_config.TextColumn("Item", required=True),
                        "description": st.column_config.TextColumn("Description"),
                        "category": st.column_config.SelectboxColumn("Category", options=cat_opts),
                        "price": st.column_config.NumberColumn("Unit Price", min_value=0.0, step=0.01, format="₱%.2f"),
                        "min_threshold": st.column_config.NumberColumn("Min", min_value=0, step=1, format="%d"),
                        "amount": st.column_config.NumberColumn("Amount", format="₱%.2f"),
                    })
                saved = st.form_submit_button("Save changes", use_container_width=True)
            if saved:
                errs = validate_edits(edited)
                if errs:
                    st.error("\n\n".join(errs))
                else:
                    count = save_item_edits(df, edited)
                    st.session_state["editor_v"] = ver + 1
                    flash("success" if count else "info",
                          f"Saved changes to {count} item(s)." if count else "No changes to save.")
                    st.rerun()
            total_bar(df)
            col1, col2 = st.columns(2)
            with col1:
                item_id = st.selectbox("Select item ID", df["id"].tolist())
                selected = df[df["id"] == item_id].iloc[0]
            with col2:
                st.markdown(f"**Item:** {selected['name']}  \n**Current quantity:** {selected['quantity']} {selected['unit']}")
                new_qty = st.number_input("New total quantity", min_value=0,
                                          value=int(selected["quantity"]), step=1)
            st.button("Update quantity", use_container_width=True, on_click=do_update,
                      args=(int(item_id), int(new_qty), selected["name"]))

    # ================= REMOVE =================
    elif choice == "Remove Item":
        page_header("Remove Item", "Permanently remove outdated or damaged items from the inventory.")
        show_flash()
        if df.empty:
            st.info("No items available to delete.")
        else:
            st.dataframe(
                df[["id", "quantity", "unit", "name", "description", "category", "price", "amount"]],
                use_container_width=True, hide_index=True,
                column_config={
                    "id": "ID", "quantity": "Qty", "unit": "Unit", "name": "Item",
                    "description": "Description", "category": "Category",
                    "price": st.column_config.NumberColumn("Unit Price", format="₱%.2f"),
                    "amount": st.column_config.NumberColumn("Amount", format="₱%.2f"),
                },
            )
            total_bar(df)
            item_id = st.selectbox("Select item ID to delete", df["id"].tolist())
            selected = df[df["id"] == item_id].iloc[0]
            st.warning(f"You are about to delete **{selected['name']}**. This cannot be undone.")
            st.button("Delete item", use_container_width=True, on_click=do_delete,
                      args=(int(item_id), selected["name"]))

    # ================= SECURITY =================
    elif choice == "Security":
        page_header("Security", "Accounts and a record of who did what in this system.")
        show_flash()
        tab_log, tab_users, tab_pw = st.tabs(["Activity Log", "User Accounts", "My Password"])

        with tab_log:
            act = get_activity()
            if act.empty:
                st.info("No activity recorded yet.")
            else:
                c1, c2 = st.columns(2)
                who = c1.selectbox("User", ["All"] + sorted(act["username"].dropna().unique().tolist()))
                what = c2.selectbox("Action", ["All"] + sorted(act["action"].dropna().unique().tolist()))
                if who != "All":
                    act = act[act["username"] == who]
                if what != "All":
                    act = act[act["action"] == what]
                st.dataframe(act, use_container_width=True, hide_index=True, column_config={
                    "ts": "When (PH time)", "username": "User", "action": "Action",
                    "item_name": "Item", "details": "Details"})
                st.caption("Showing the latest 500 events.")
                exp_log = act.rename(columns={"ts": "When (PH time)", "username": "User", "action": "Action",
                                              "item_name": "Item", "details": "Details"}).fillna("")
                export_menu("Activity Log", report_subtitle(), exp_log, set(), None,
                            base="activity-log", key="exp_log")

        with tab_users:
            users = list_users()
            users["status"] = users["locked_until"].map(
                lambda t: "Locked" if pd.notna(t) and t > pd.Timestamp.now(tz="UTC") else "Active")
            users["created_at"] = pd.to_datetime(users["created_at"], utc=True).dt.tz_convert(
                "Asia/Manila").dt.strftime("%b %d, %Y")
            st.dataframe(users[["username", "full_name", "status", "created_at"]], use_container_width=True,
                         hide_index=True, column_config={"username": "Username", "full_name": "Full name",
                                                         "status": "Status", "created_at": "Created"})
            with st.expander("Add a new account"):
                with st.form("new_user_form", clear_on_submit=True):
                    n_name = st.text_input("Full name")
                    n_user = st.text_input("Username", placeholder="letters, numbers, . _ -")
                    n_pw = st.text_input("Password (min. 8 characters)", type="password")
                    n_pw2 = st.text_input("Confirm password", type="password")
                    if st.form_submit_button("Create account", use_container_width=True):
                        u = n_user.strip().lower()
                        if not n_name.strip() or not USERNAME_RE.match(u):
                            st.error("Enter a name and a username of 3-30 letters, numbers, . _ -")
                        elif password_problem(n_pw, n_pw2):
                            st.error(password_problem(n_pw, n_pw2))
                        elif get_user(u):
                            st.error("That username already exists.")
                        else:
                            create_user(u, n_name.strip(), n_pw)
                            log_activity("CREATE_USER", details=f"Created account '{u}'")
                            flash("success", f"Account **{u}** created.")
                            st.rerun()
            others = [u for u in users["username"] if u != st.session_state["user"]]
            if others:
                with st.expander("Remove an account"):
                    target = st.selectbox("Account to remove", others)
                    if st.button("Remove account", key="rm_user"):
                        with get_engine().begin() as conn:
                            conn.exec_driver_sql("DELETE FROM users WHERE username = %s", (target,))
                            conn.exec_driver_sql("DELETE FROM sessions WHERE username = %s", (target,))
                            _log(conn, "DELETE_USER", details=f"Removed account '{target}'")
                        flash("success", f"Account **{target}** removed.")
                        st.rerun()

        with tab_pw:
            with st.form("pw_form", clear_on_submit=True):
                cur = st.text_input("Current password", type="password")
                new = st.text_input("New password (min. 8 characters)", type="password")
                new2 = st.text_input("Confirm new password", type="password")
                if st.form_submit_button("Change password", use_container_width=True):
                    me = get_user(st.session_state["user"])
                    if not verify_password(cur, me["password_hash"]):
                        st.error("Current password is incorrect.")
                    elif password_problem(new, new2):
                        st.error(password_problem(new, new2))
                    else:
                        with get_engine().begin() as conn:
                            conn.exec_driver_sql("UPDATE users SET password_hash = %s WHERE username = %s",
                                                 (hash_password(new), me["username"]))
                            _log(conn, "CHANGE_PASSWORD")
                            conn.exec_driver_sql("DELETE FROM sessions WHERE username = %s", (me["username"],))
                        tok = create_session(me["username"])  # other devices must sign in again
                        st.session_state.update(session_token=tok, cookie_cmd=("set", tok))
                        flash("success", "Password changed. Other devices were signed out.")
                        st.rerun()


if __name__ == "__main__":
    main()
