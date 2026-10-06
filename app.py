import base64
import psycopg2  # noqa: F401  (driver used by SQLAlchemy)
from sqlalchemy import create_engine
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

SEARCH_ICON = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAD1mlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyI+CiAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICAgICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIj4KICAgICAgPGRjOmNyZWF0b3I+PHJkZjpTZXE+PHJkZjpsaT5GcmVlaWNvbjwvcmRmLmxpPjwvcmRmOlNlcT48L2RjOmNyZWF0b3I+CiAgICAgIDxkYzpyaWdodHM+PHJkZjpBbHQ+PHJkZjpsaSB4bWw6bGFuZz0ieC1kZWZhdWx0Ij5GcmVlIGZvciBwZXJzb25hbCBhbmQgY29tbWVyY2lhbCB1c2UgLSBmcmVlaWNvbi5jb208L3JkZjpsaT48L3JkZjpBbHQ+PC9kYzpyaWdodHM+CiAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICAgICAgeG1sbnM6SXB0YzR4bXBDb3JlPSJodHRwOi8vaXB0Yy5vcmcvc3RkL0lwdGM0eG1wQ29yZS8xLjAveG1sbnMvIj4KICAgICAgPElwdGM0eG1wQ29yZTpDcmVkaXRMaW5lPmZyZWVpY29uLmNvbTwvSXB0YzR4bXBDb3JlOkNyZWRpdExpbmU+CiAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICAgICAgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIj4KICAgICAgPHBob3Rvc2hvcDpDcmVkaXQ+ZnJlZWljb24uY29tPC9waG90b3Nob3A6Q3JlZGl0PgogICAgICA8cGhvdG9zaG9wOlNvdXJjZT5mcmVlaWNvbi5jb208L3Bob3Rvc2hvcDpTb3VyY2U+CiAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgo8P3hwYWNrZXQgZW5kPSJ3Ij8+W1BtjgAAC0VJREFUeAHc2wWMpUkRB/C3EDjc9YDD3Q5CsMOdIMEtuLsE1xDcEpzgLsHd/TjcDrfDDjhcLtgBAe7/6339Xc23b2bnzXtvd2cnVa+quvur7q6vpbr6m+NN9o2/g9KMWwefHnxH8AvB7wd/GvxekCz9GeFvE1Q+ZHHYmwY4f5r/pKAO/jz0jcGHBW8cvExQ/jlCLxAkS39o+DcElffck8OfJ7hl2BsGuHJi+8GgDjw6VAdD5gbNPSpP/TD4oeAhwblhTxrg3Gnd+4KfCl4nuCO4HvwnGX8I/iL4x+C/g+sBPddO5mHB9wbVE7I52BMG0MD7pznfDF4vOIb/J+HzwScGdeRsoQcETx80108XeqKg6XCtUOWsCf8LP4brJ+HbwQcEN9W3TRWKsq3CyfKgxeu5oScJVvhTBJ05Z+jlg48LfiT4yyCjhAxANu8/mhTlLhfqTeONlIgDMNZzIr09ePLghrBKA3iDn0ntNwpW+EeERwa9XR3QsYhzw8/yBAMaGY8J/7dgBfV+OglnCK4LqzKASj+XWg8OVvhkhAsGnxb8e3AWnDGJVwjeNHjg8EyiJVAKvJzVepK7eZ1wY48nZq6cIeUaABiN7E40P4+7b+rQ36l1qgU1G+wGfX0b7L/qX7fXfX/fHwQ956QGg0eWbT/wQx4r0C2Q7+O5B9bL105KkYl6V/l17qD8K+qfE5lU6G9B00sO1zXF6cE165KzH2jL3o62Yy+mK4q5N+zWq0g/m760Kj+1+H7+lD+fL2/b/61f9/h8NfX08l95lXvR8GvW30bKffDfv3F71rO3O4e9B27vNl7D3+6N8W6D9O65aI2l31n+/U2t958uF8e4aNfUef+b3tX4N2vN6t+wN59L6lC55/Jz+wTj6+8mBv7c/7P8B/l/v5z7//Wj5B3K/0T+t/3P85fN3P648/2v7f4u+ff8/wH8//v14A3gE/3+l33X+4O//XWv9/gN3f3//3f1e5O//1rP3+/v7+v8H9rNrf6S/vf9/vf2+0X8T177/X7v9v+7fv9/f/33t7P3+/r7vf38n+L/v3b8//8f5v4F6b7/vf3/tf9/vX//v38X/gX///1b//v8P/+1v/9/sWb+9f+H3f79/sf/n///+8P//t6Nf///v////+w87D2r9v78P6v9u4f6f7r/+vf4f8f7v/+Pv9/v9/f8///9f7sPu/3+/+78r8v///v7/7r////8A6f////v7u7u7v////7vv8f/u+u///7///vf7f///vu/f///v////9//////9vv//////v///v///////7v//////v///v//v///7/////fv//v///v////v/////v///////////////////7////////3////3//v///v//////7//v///v////////vvv//v///////3////7//v///v///////vv///////v///////3////7//v///v///////7v//////v////////////////////////////////////////////////7////////v///////v///////7f//////v//////77f//v///v//vv///v//vv///v//////7v//////7v//////7v//////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v-------v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v-------v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v///////v-------530x530.png",
LOGO_SVG = """<svg xmlns="http://v3.org/2000/svg" viewBox="0 0 48 48">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#FF9A3D"/><stop offset="1" stop-color="#FF5A00"/></linearGradient></defs>
<rect width="48" height="48" rx="13" fill="url(#g)"/>
<path d="M24 11.5 35 17.75v12.5L24 36.5 13 30.25v-12.5z" fill="#fff" fill-opacity=".16" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/>
<path d="M13 17.75 24 24l11-6.25" fill="#fff" fill-opacity=".95" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/>
<path d="M24 24v12.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>
</svg>"""
LOGO_URI = "data:image/svg+xml;base64," + base64.b64encode(LOGO_SVG.encode()).decode()

# --- 2. CUSTOM CSS ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Plus Jakarta Sans', 'Helvetica Neue', sans-serif;
}}
.block-container {{ padding-top: 4.5rem; max-width: 1400px; }}
h1, h2, h3 {{ font-weight: 700; letter-spacing: -0.02em; }}

/* Sidebar brand */
.brand {{ display:flex; align-items:center; gap:12px; margin: 4px 0 28px; }}
.brand-logo {{ width:44px; height:44px; display:block; border-radius:12px;
    box-shadow: 0 4px 12px rgba(255,106,0,.28); }}
.brand-name {{ font-size:22px; font-weight:700; line-height:1.1; }}
.brand-sub {{ font-size:12px; opacity:.65; }}
.menu-label {{ font-size:14px; opacity:.65; margin-bottom:6px; }}

/* ===== SIDEBAR ===== */
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
    backdrop-filter: blur(6px);
}}
.side-foot .live {{ display:flex; align-items:center; gap:8px; font-size:12px; color:#86efac; font-weight:600; }}
.side-foot .dot {{ width:8px; height:8px; border-radius:50%; background:#22c55e;
    box-shadow: 0 0 0 0 rgba(34,197,94,.6); animation: pulse 2s infinite; }}
@keyframes pulse {{ 70% {{ box-shadow: 0 0 0 8px rgba(34,197,94,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(34,197,94,0); }} }}
.side-foot .foot-title {{ margin-top:10px; font-size:13px; font-weight:600; color:#f1f5f9; }}
.side-foot .foot-sub {{ font-size:12px; color:#8b94a5; }}

/* ===== MAIN AREA ===== */
.stApp {{
    isolation: isolate;
    background-image: radial-gradient(rgba(128,128,128,.16) 1px, transparent 1px);
    background-size: 26px 26px;
}}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {{ background: transparent !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; backdrop-filter: blur(8px); }}

.stApp::before, .stApp::after, [data-testid="stAppViewContainer"]::before {{
    content: ""; position: fixed; border-radius: 50%; z-index: -1; pointer-events: none;
}}
.stApp::before {{
    width: 58vw; height: 58vw; top: -20vw; left: -12vw;
    background: radial-gradient(circle, rgba(255,106,0,.30), rgba(255,106,0,0) 68%);
    animation: blobA 20s ease-in-out infinite alternate;
}}
.stApp::after {{
    width: 52vw; height: 52vw; right: -14vw; bottom: -22vw;
    background: radial-gradient(circle, rgba(255,176,59,.28), rgba(255,176,59,0) 68%);
    animation: blobB 24s ease-in-out infinite alternate;
}}
[data-testid="stAppViewContainer"]::before {{
    width: 38vw; height: 38vw; top: 34vh; left: 46vw;
    background: radial-gradient(circle, rgba(255,90,60,.17), rgba(255,90,60,0) 68%);
    animation: blobC 28s ease-in-out infinite alternate;
}}
@keyframes blobA {{ from {{ transform: translate(0,0) scale(1); }} to {{ transform: translate(16vw,12vh) scale(1.18); }} }}
@keyframes blobB {{ from {{ transform: translate(0,0) scale(1); }} to {{ transform: translate(-14vw,-10vh) scale(1.22); }} }}
@keyframes blobC {{ from {{ transform: translate(0,0) scale(.9); }} to {{ transform: translate(-18vw,14vh) scale(1.1); }} }}

.card, .total-bar {{ backdrop-filter: blur(10px); animation: fadeUp .5s ease both;
    transition: transform .2s ease, box-shadow .2s ease; }}
.card:hover {{ transform: translateY(-4px); box-shadow: 0 14px 30px rgba(255,106,0,.16); }}
@keyframes fadeUp {{ from {{ opacity:0; transform: translateY(12px); }} to {{ opacity:1; transform: translateY(0); }} }}

@media (prefers-reduced-motion: reduce) {{
    .stApp::before, .stApp::after, [data-testid="stAppViewContainer"]::before,
    section[data-testid="stSidebar"]::before, section[data-testid="stSidebar"]::after,
    .card, .total-bar, .side-foot .dot {{ animation: none !important; }}
}}

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

[data-testid="stTextInput"]:has(input[placeholder="Search item name..."]) div[data-baseweb="input"] {{ position: relative; }}
[data-testid="stTextInput"]:has(input[placeholder="Search item name..."]) div[data-baseweb="input"]::before {{
    content: ""; position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
    width: 18px; height: 18px; opacity: .65; pointer-events: none; z-index: 2;
    background-color: currentColor;
    -webkit-mask: url({SEARCH_ICON}) center / contain no-repeat;
    mask: url({SEARCH_ICON}) center / contain no-repeat;
}}
[data-testid="stTextInput"]:has(input[placeholder="Search item name..."]) input {{ padding-left: 44px !important; }}

.total-bar {{
    display:flex; justify-content:space-between; align-items:center;
    margin-top:8px; padding:14px 20px; border-radius:12px;
    background: rgba(255,106,0,.12); border:1px solid rgba(255,106,0,.35);
}}
.total-bar .t-label {{ font-weight:700; letter-spacing:.04em; }}
.total-bar .t-sub {{ font-size:12px; opacity:.65; }}
.total-bar .t-amount {{ font-size:24px; font-weight:700; color:{ORANGE}; }}

[data-testid="stMain"] .stButton > button, [data-testid="stMain"] .stFormSubmitButton > button {{
    background:{ORANGE}; color:#fff; border:1px solid {ORANGE};
    border-radius:8px; font-weight:600; padding: 0.5rem 1rem;
}}
[data-testid="stMain"] .stButton > button:hover, [data-testid="stMain"] .stFormSubmitButton > button:hover {{
    background:#e65f00; border-color:#e65f00; color:#fff;
}}
[data-testid="stMain"] .stButton > button p, [data-testid="stMain"] .stFormSubmitButton > button p {{ color:#fff; }}

div[data-baseweb="input"], div[data-baseweb="select"] > div {{ border-radius: 8px !important; }}
div[data-testid="stDataFrame"] {{ border:1px solid rgba(128,128,128,.28); border-radius:12px; overflow:hidden; }}
.stAlert {{ border-radius: 10px; }}
</style>
""", unsafe_allow_html=True)


# --- 3. DATABASE (PostgreSQL) ---
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

    return create_engine(db_url)


def init_db():
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


UNITS = ["Reams", "Pcs.", "Boxes", "Packs", "Bottles", "Gallons", "Rolls",
         "Sets", "Pairs", "Cartridges", "Units"]


def add_item(name, category, quantity, price, min_threshold, unit="Pcs.", description=""):
    engine = get_engine()
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO items (name, category, quantity, price, min_threshold, unit, description) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, category, quantity, price, min_threshold, unit, description),
        )
    st.cache_data.clear()


@st.cache_data(ttl=60)
def get_inventory():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM items ORDER BY id ASC", engine)
    df["unit"] = df["unit"].fillna("Pcs.")
    df["description"] = df["description"].fillna("")
    df["amount"] = df["quantity"] * df["price"]
    return df


def update_quantity(item_id, new_quantity):
    engine = get_engine()
    with engine.begin() as conn:
        conn.exec_driver_sql("UPDATE items SET quantity = %s WHERE id = %s", (new_quantity, item_id))
    st.cache_data.clear()


def delete_item(item_id):
    engine = get_engine()
    with engine.begin() as conn:
        conn.exec_driver_sql("DELETE FROM items WHERE id = %s", (item_id,))
    st.cache_data.clear()


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


PAGES = ["Dashboard", "Add Item", "Restock / Adjust", "Remove Item"]


def page_header(title, subtitle=None):
    st.markdown(f"<h2 style='margin-bottom:0'>{title}</h2>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-sub'>{subtitle}</div>", unsafe_allow_html=True)


# --- 5. MAIN APP ---
def main():
    init_db()

    # Sidebar
    st.sidebar.markdown(f"""
        <div class="brand">
            <img class="brand-logo" src="{LOGO_URI}" alt="DICT NIR logo">
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
    }
    choice = st.session_state["nav"]
    for p, (label, icon) in nav_items.items():
        kwargs = dict(key=f"nav_{p}", use_container_width=True,
                      type="primary" if choice == p else "secondary",
                      on_click=go_to, args=(p,))
        try:
            st.sidebar.button(label, icon=icon, **kwargs)
        except TypeError:
            st.sidebar.button(label, **kwargs)

    st.sidebar.markdown("""
        <div class="side-foot">
            <div class="live"><span class="dot"></span>System online</div>
            <div class="foot-title">DICT · Negros Island Region</div>
            <div class="foot-sub">Inventory Management System</div>
        </div>
    """, unsafe_allow_html=True)

    df = get_inventory()

    # ================= DASHBOARD =================
    if choice == "Dashboard":
        top_search, top_btn = st.columns([6, 1.2])
        with top_search:
            search_query = st.text_input("Search", placeholder="Search item name...",
                                         label_visibility="collapsed")
        with top_btn:
            try:
                st.button("Add New Item", icon=":material/add:", use_container_width=True,
                          on_click=go_to, args=("Add Item",))
            except TypeError:
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

        agg = (df.groupby("category", dropna=True)["value"].sum().reset_index()
                 .sort_values("value"))
        agg["pct"] = agg["value"] / agg["value"].sum() * 100
        agg["label"] = agg["pct"].round().astype(int).astype(str) + "%"

        left, right = st.columns([2, 1])
        with left:
            st.markdown("<div class='card-label'>Analytics</div>"
                        "<div class='section-title'>Value by Category</div>", unsafe_allow_html=True)
            base = alt.Chart(agg).encode(
                x=alt.X("category:N", sort=None, title=None, axis=alt.Axis(labelAngle=0, labelLimit=120)),
                y=alt.Y("value:Q", title=None, axis=alt.Axis(format="~s", gridDash=[4, 4])),
            )
            bars = base.mark_bar(color=ORANGE, cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=48)
            labels = base.mark_text(color="white", fontWeight="bold", dy=14).encode(text="label:N")
            st.altair_chart((bars + labels).properties(height=340), use_container_width=True)

        with right:
            st.markdown("<div class='section-title'>Stock by Category</div>", unsafe_allow_html=True)
            donut = alt.Chart(agg).mark_arc(innerRadius=62, outerRadius=95).encode(
                theta="value:Q",
                color=alt.Color("category:N", legend=None,
                                scale=alt.Scale(range=PALETTE)),
                tooltip=["category", alt.Tooltip("value:Q", format=",.2f")],
            ).properties(height=210)
            st.altair_chart(donut, use_container_width=True)

            rows = ""
            for _, r in agg.sort_values("value", ascending=False).head(4).iterrows():
                rows += (f"<div class='area-row'><span><b>{r['pct']:.0f}%</b>{r['category']}</span>"
                         f"<span>₱{r['value']:,.0f}</span></div>")
            st.markdown(f"<div class='card-label' style='margin-top:6px'>Top 4 Categories</div>{rows}",
                        unsafe_allow_html=True)

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

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Inventory Records</div>", unsafe_allow_html=True)
        f1, f2 = st.columns([2, 1])
        with f1:
            name_filter = st.text_input("Filter by name", search_query, placeholder="Item name")
        with f2:
            cats = ["All"] + list(df["category"].dropna().unique())
            cat_filter = st.selectbox("Category", cats)

        view = df.copy()
        if name_filter:
            view = view[view["name"].str.contains(name_filter, case=False, na=False)]
        if cat_filter != "All":
            view = view[view["category"] == cat_filter]
        view["status"] = view.apply(
            lambda r: "🔴 Low stock" if r["quantity"] <= r["min_threshold"] else "🟢 In stock", axis=1)
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

    # ================= RESTOCK / ADJUST =================
    elif choice == "Restock / Adjust":
        page_header("Restock / Adjust Stock",
                    "Update quantities when shipments arrive or items are issued to personnel.")
        if df.empty:
            st.info("No items available to update.")
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
            col1, col2 = st.columns(2)
            with col1:
                item_id = st.selectbox("Select item ID", df["id"].tolist())
                selected = df[df["id"] == item_id].iloc[0]
                st.markdown(f"**Selected:** {selected['name']} (Current Qty: {selected['quantity']} {selected['unit']})")
            with col2:
                new_qty = st.number_input("New total quantity", min_value=0, value=int(selected["quantity"]), step=1)
                if st.button("Update Quantity", use_container_width=True):
                    update_quantity(item_id, new_qty)
                    st.success(f"Updated **{selected['name']}** quantity to {new_qty} {selected['unit']}.")
                    st.rerun()

    # ================= REMOVE ITEM =================
    elif choice == "Remove Item":
        page_header("Remove Item",
                    "Permanently delete discontinued or incorrect inventory items.")
        if df.empty:
            st.info("No items available to remove.")
        else:
            st.dataframe(
                df[["id", "quantity", "unit", "name", "category", "price"]],
                use_container_width=True, hide_index=True,
            )
            item_id_del = st.selectbox("Select item ID to delete", df["id"].tolist(), key="del_select")
            selected_del = df[df["id"] == item_id_del].iloc[0]
            st.warning(f"You are about to delete **{selected_del['name']}** (ID: {item_id_del}). This action cannot be undone.")
            if st.button("Permanently Delete Item", type="primary"):
                delete_item(item_id_del)
                st.success(f"Deleted item **{selected_del['name']}** successfully.")
                st.rerun()

if __name__ == "__main__":
    main()
