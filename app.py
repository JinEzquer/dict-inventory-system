import streamlit as st
import pandas as pd
import altair as alt
import psycopg2
from sqlalchemy import create_engine

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
.brand-logo {{
    width:44px; height:44px; border-radius:12px; background:{ORANGE};
    display:flex; align-items:center; justify-content:center; font-size:22px;
}}
.brand-name {{ font-size:22px; font-weight:700; line-height:1.1; }}
.brand-sub {{ font-size:12px; opacity:.65; }}
.menu-label {{ font-size:14px; opacity:.65; margin-bottom:6px; }}

section[data-testid="stSidebar"] .stButton > button {{
    background: transparent; border: none; box-shadow: none;
    justify-content: flex-start; text-align: left;
    padding: 10px 12px; border-radius: 8px; font-weight: 500;
}}
section[data-testid="stSidebar"] .stButton > button > div {{ justify-content: flex-start; width: 100%; }}
section[data-testid="stSidebar"] .stButton > button p {{ font-size: 15px; text-align: left; }}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(128,128,128,.14); border: none; color: inherit;
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {{
    background: rgba(255,106,0,.15); color: {ORANGE}; font-weight: 600;
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] p {{ color: {ORANGE}; }}

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
    # Clear cache so data updates immediately
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
        conn.exec_driver_sql(
            "UPDATE items SET quantity = %s WHERE id = %s",
            (new_quantity, item_id)
        )
    st.cache_data.clear()


def delete_item(item_id):
    engine = get_engine()
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "DELETE FROM items WHERE id = %s",
            (item_id,)
        )
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
    st.sidebar.markdown("""
        <div class="brand">
            <div class="brand-logo">📦</div>
            <div>
                <div class="brand-name">DICT NIR</div>
                <div class="brand-sub">Office Property & Supplies</div>
            </div>
        </div>
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

    df = get_inventory()

    # ================= DASHBOARD =================
    if choice == "Dashboard":
        top_search, top_btn = st.columns([6, 1.2])
        with top_search:
            search_query = st.text_input("Search", placeholder="🔍  Search item name...",
                                         label_visibility="collapsed")
        with top_btn:
            st.button("＋ Add New Item", use_container_width=True, on_click=go_to, args=("Add Item",))

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

    # ================= RESTOCK =================
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
            with col2:
                st.markdown(f"**Item:** {selected['name']}  \n**Current quantity:** {selected['quantity']} {selected['unit']}")
                new_qty = st.number_input("New total quantity", min_value=0,
                                          value=int(selected["quantity"]), step=1)
            if st.button("Update quantity", use_container_width=True):
                update_quantity(item_id, new_qty)
                st.success(f"Updated stock for **{selected['name']}**.")
                st.rerun()

    # ================= REMOVE =================
    elif choice == "Remove Item":
        page_header("Remove Item", "Permanently remove outdated or damaged items from the inventory.")
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
            if st.button("Delete item", use_container_width=True):
                delete_item(item_id)
                st.success("Item deleted.")
                st.rerun()


if __name__ == "__main__":
    main()
