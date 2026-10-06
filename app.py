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





def _theme_type():

    try:

        return st.context.theme.type  # "light" / "dark" (newer Streamlit)

    except Exception:

        return None





_t = _theme_type()

if _t == "light":

    LIGHT_OPEN, LIGHT_CLOSE = "", ""                                    # always apply

elif _t == "dark":

    LIGHT_OPEN, LIGHT_CLOSE = "@media not all {", "}"                   # never apply

else:

    LIGHT_OPEN, LIGHT_CLOSE = "@media (prefers-color-scheme: light) {", "}"  # follow system



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

.card, .total-bar {{ animation: fadeUp .45s ease both;

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

.stApp h2 {{ font-size: 30px; }}



@media (prefers-reduced-motion: reduce) {{

    .stApp::before, .stApp::after, [data-testid="stAppViewContainer"]::before,

    section[data-testid="stSidebar"]::before, section[data-testid="stSidebar"]::after,

    .card, .total-bar, .side-foot .dot {{ animation: none !important; }}

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

/* ===== LIGHT MODE ONLY: swap orange for soft light blue (dark mode untouched) ===== */

{LIGHT_OPEN}

.stApp::before {{ background: radial-gradient(circle, rgba(96,165,250,.22), rgba(96,165,250,0) 68%); }}

.stApp::after {{ background: radial-gradient(circle, rgba(125,211,252,.24), rgba(125,211,252,0) 68%); }}

[data-testid="stAppViewContainer"]::before {{ background: radial-gradient(circle, rgba(147,197,253,.20), rgba(147,197,253,0) 68%); }}



.card::before {{ background: linear-gradient(90deg, #3B82F6, #7DD3FC); }}

.card:hover {{ box-shadow: 0 14px 30px rgba(59,130,246,.16); }}

.badge-orange {{ background: rgba(59,130,246,.14); color: #2563EB; }}

.area-row b {{ color: #2563EB; }}

.total-bar {{ background: rgba(59,130,246,.10); border-color: rgba(59,130,246,.32); }}

.total-bar .t-amount {{ color: #2563EB; }}



[data-testid="stMain"] .stButton > button, [data-testid="stMain"] .stFormSubmitButton > button {{

    background: #3B82F6; border-color: #3B82F6; }}

[data-testid="stMain"] .stButton > button:hover, [data-testid="stMain"] .stFormSubmitButton > button:hover {{

    background: #2563EB; border-color: #2563EB; }}



/* Charts: recolor orange -> sky blue */

div[data-testid="stVegaLiteChart"] {{ filter: hue-rotate(180deg); }}



/* Sidebar + logo */

.brand-logo {{ background-image: url("{LOGO_URI_BLUE}"); box-shadow: 0 4px 12px rgba(59,130,246,.30); }}

section[data-testid="stSidebar"] {{

    background: linear-gradient(180deg, #10141c 0%, #141b29 55%, #0f2038 100%) !important; }}

section[data-testid="stSidebar"]::before {{

    background: radial-gradient(circle, rgba(59,130,246,.42), rgba(59,130,246,0) 70%); }}

section[data-testid="stSidebar"]::after {{

    background: radial-gradient(circle, rgba(125,211,252,.22), rgba(125,211,252,0) 70%); }}

section[data-testid="stSidebar"] .stButton > button[kind="primary"],

section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {{

    background: linear-gradient(90deg, #3B82F6, #60A5FA); box-shadow: 0 8px 20px rgba(59,130,246,.35); }}

{LIGHT_CLOSE}

</style>

""", unsafe_allow_html=True)





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





@st.cache_resource(show_spinner=False)

def init_db():

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

    return True





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

    st.cache_data.clear()  # refresh data immediately





@st.cache_data(ttl=300, show_spinner=False)

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

            st.markdown("<div class='card-label'>Analytics</div>"

                        "<div class='section-title'>Value by Category</div>", unsafe_allow_html=True)

            base = alt.Chart(agg).encode(

                x=alt.X("category:N", sort=None, title=None, axis=alt.Axis(labelAngle=0, labelLimit=120)),

                y=alt.Y("value:Q", title=None, axis=alt.Axis(format="~s", gridDash=[4, 4])),

            )

            bars = base.mark_bar(color=ORANGE, cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=48)

            labels = base.mark_text(color="white", fontWeight="bold", dy=14).encode(text="label:N")

            st.altair_chart((bars + labels).properties(height=340, background="transparent"), use_container_width=True)



        with right.container(border=True):

            st.markdown("<div class='section-title'>Stock by Category</div>", unsafe_allow_html=True)

            donut = alt.Chart(agg).mark_arc(innerRadius=62, outerRadius=95).encode(

                theta="value:Q",

                color=alt.Color("category:N", legend=None,

                                scale=alt.Scale(range=PALETTE)),

                tooltip=["category", alt.Tooltip("value:Q", format=",.2f")],

            ).properties(height=210, background="transparent")

            st.altair_chart(donut, use_container_width=True)



            rows = ""

            for _, r in agg.sort_values("value", ascending=False).head(4).iterrows():

                rows += (f"<div class='area-row'><span><b>{r['pct']:.0f}%</b>{r['category']}</span>"

                         f"<span>₱{r['value']:,.0f}</span></div>")

            st.markdown(f"<div class='card-label' style='margin-top:6px'>Top 4 Categories</div>{rows}",

                        unsafe_allow_html=True)



        # Top valued items

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Top Items by Value</div>", unsafe_allow_html=True)

        top = df.sort_values("value", asceending=False).head(5).copy()

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

                    "Update quantities when shipments arrive or items are issued to personnel.")

        show_flash()

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





if __name__ == "__main__":

    main() 



