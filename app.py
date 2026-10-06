import streamlit as st
import psycopg2  # noqa: F401
from sqlalchemy import create_engine
import altair as alt
import pandas as pd

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="DICT NIR - Inventory System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

ORANGE = "#FF6A00"
PALETTE = ["#FF6A00", "#FF8A1F", "#FFA826", "#FFC53D", "#FFE08A"]

# --- 2. CLEAN & LIGHTWEIGHT CSS ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Plus Jakarta Sans', sans-serif;
}}
.block-container {{ padding-top: 3.5rem; max-width: 1400px; }}
h1, h2, h3 {{ font-weight: 700; letter-spacing: -0.02em; }}

/* Sidebar styling */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #12141a 0%, #181b24 100%) !important;
    border-right: 1px solid rgba(255,255,255,.07);
}}
section[data-testid="stSidebar"] .stButton > button {{
    background: transparent; border: none; color: #cbd2de;
    justify-content: flex-start; text-align: left;
    padding: 10px 14px; border-radius: 8px; font-weight: 500;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,.08); color: #ffffff;
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(90deg, #FF6A00, #FF8A1F); color: #ffffff; font-weight: 600;
}}

/* Cards */
.card {{
    background: rgba(128,128,128,.07);
    border: 1px solid rgba(128,128,128,.28);
    border-radius:12px; padding:16px 18px;
}}
.card-label {{ font-size:13px; font-weight:500; opacity:.65; }}
.card-value {{ font-size:26px; font-weight:700; margin:4px 0 6px; }}
.badge {{ display:inline-block; font-size:11px; font-weight:600; padding:3px 8px; border-radius:6px; }}
.badge-green {{ background:rgba(34,197,94,.18); color:#22a559; }}
.badge-red {{ background:rgba(239,68,68,.18); color:#ef4444; }}
.badge-orange {{ background:rgba(255,106,0,.18); color:{ORANGE}; }}

.section-title {{ font-size:18px; font-weight:700; margin: 6px 0 2px; }}
.section-sub {{ font-size:13px; opacity:.65; margin-bottom: 8px; }}

.total-bar {{
    display:flex; justify-content:space-between; align-items:center;
    margin-top:8px; padding:12px 18px; border-radius:10px;
    background: rgba(255,106,0,.12); border:1px solid rgba(255,106,0,.35);
}}
.total-bar .t-label {{ font-weight:700; letter-spacing:.04em; }}
.total-bar .t-amount {{ font-size:22px; font-weight:700; color:{ORANGE}; }}

[data-testid="stMain"] .stButton > button, [data-testid="stMain"] .stFormSubmitButton > button {{
    background:{ORANGE}; color:#fff; border:1px solid {ORANGE};
    border-radius:8px; font-weight:600; padding: 0.4rem 1rem;
}}
[data-testid="stMain"] .stButton > button:hover {{ background:#e65f00; color:#fff; }}
</style>
""", unsafe_allow_html=True)


# --- 3. DATABASE CONNECTION & CACHING ---
@st.cache_resource
def get_engine():
    if "DATABASE_URL" not in st.secrets:
        st.error("🚨 **DATABASE_URL is missing!** Please add it in your Streamlit Cloud Settings -> Secrets.")
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


@st.cache_data(ttl=30)
def get_inventory():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM items ORDER BY id ASC", engine)
    df["unit"] = df["unit"].fillna("Pcs.")
    df["description"] = df["description"].fillna("")
    df["amount"] = df["quantity"] * df["price"]
    return df


def add_item(name, category, quantity, price, min_threshold, unit, description):
    engine = get_engine()
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO items (name, category, quantity, price, min_threshold, unit, description) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, category, quantity, price, min_threshold, unit, description),
        )
    st.cache_data.clear()


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
                 <div style="font-size:12px; opacity:.65;">{len(df_view)} item(s) · {qty:,} total quantity</div></div>
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

    # Sidebar Navigation
    st.sidebar.markdown("### 📦 DICT NIR")
    st.sidebar.markdown("<div style='font-size:12px; opacity:.65; margin-bottom:20px;'>Office Property & Supplies</div>", unsafe_allow_html=True)

    if "nav" not in st.session_state:
        st.session_state["nav"] = PAGES[0]

    choice = st.session_state["nav"]
    for p in PAGES:
        is_primary = (choice == p)
        if st.sidebar.button(p, use_container_width=True, type="primary" if is_primary else "secondary"):
            go_to(p)
            st.rerun()

    df = get_inventory()

    # ================= DASHBOARD =================
    if choice == "Dashboard":
        col_s, col_b = st.columns([5, 1.2])
        with col_s:
            search_query = st.text_input("Search", placeholder="🔍 Search items...", label_visibility="collapsed")
        with col_b:
            if st.button("＋ Add Item", use_container_width=True):
                go_to("Add Item")
                st.rerun()

        page_header("Key Metrics", "DICT Negros Island Region · Inventory Dashboard")

        if df.empty:
            st.info("No inventory records yet. Click **Add Item** to get started.")
            return

        total_qty = int(df["quantity"].sum())
        total_value = df["amount"].sum()
        low_df = df[df["quantity"] <= df["min_threshold"]]

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Total Stock Quantity", f"{total_qty:,} units", f"{len(df)} item types", "badge-green")
        with c2:
            metric_card("Total Asset Valuation", f"₱{total_value:,.2f}", f"{df['category'].nunique()} categories", "badge-orange")
        with c3:
            cls = "badge-red" if len(low_df) else "badge-green"
            txt = "Needs restocking" if len(low_df) else "All stocked"
            metric_card("Low Stock Items", f"{len(low_df)}", txt, cls)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # Lightweight single chart
        agg = df.groupby("category", dropna=True)["amount"].sum().reset_index().sort_values("amount", ascending=False)
        if not agg.empty:
            st.markdown("<div class='section-title'>Asset Valuation by Category</div>", unsafe_allow_html=True)
            chart = alt.Chart(agg).mark_bar(color=ORANGE, cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("category:N", sort=None, title=None),
                y=alt.Y("amount:Q", title=None, axis=alt.Axis(format="~s")),
                tooltip=["category", alt.Tooltip("amount:Q", format=",.2f")]
            ).properties(height=260)
            st.altair_chart(chart, use_container_width=True)

        st.markdown("<div class='section-title'>Inventory Records</div>", unsafe_allow_html=True)
        f1, f2 = st.columns([2, 1])
        with f1:
            name_filter = st.text_input("Filter by name", search_query, placeholder="Item name", key="filter_name")
        with f2:
            cats = ["All"] + list(df["category"].dropna().unique())
            cat_filter = st.selectbox("Category filter", cats)

        view = df.copy()
        if name_filter:
            view = view[view["name"].str.contains(name_filter, case=False, na=False)]
        if cat_filter != "All":
            view = view[view["category"] == cat_filter]

        view["status"] = view.apply(lambda r: "🔴 Low stock" if r["quantity"] <= r["min_threshold"] else "🟢 In stock", axis=1)
        display_df = view[["id", "quantity", "unit", "name", "description", "category", "price", "amount", "status"]]
        
        st.dataframe(
            display_df, use_container_width=True, hide_index=True,
            column_config={
                "id": "ID", "quantity": "Qty", "unit": "Unit", "name": "Item",
                "description": "Description", "category": "Category",
                "price": st.column_config.NumberColumn("Unit Price", format="₱%.2f"),
                "amount": st.column_config.NumberColumn("Amount", format="₱%.2f"),
                "status": "Status",
            },
        )
        total_bar(view)

    # ================= ADD ITEM =================
    elif choice == "Add Item":
        page_header("Register New Item", "Add supplies or equipment to the inventory.")
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item name", placeholder="e.g., Copy Paper A4")
                category = st.selectbox("Category", ["Hardware / Peripherals", "Office Supplies",
                                                     "Networking Equipment", "Furniture & Fixtures",
                                                     "ICT Equipment"])
                quantity = st.number_input("Initial quantity", min_value=0, step=1)
                description = st.text_area("Description (optional)", height=80)
            with col2:
                unit = st.selectbox("Unit", UNITS)
                custom_unit = st.text_input("Other unit (optional)")
                price = st.number_input("Unit price (₱)", min_value=0.0, format="%.2f")
                min_threshold = st.number_input("Low stock threshold", min_value=1, value=5, step=1)
            
            if st.form_submit_button("Save Item to Database", use_container_width=True):
                if not name.strip():
                    st.error("Item name is required.")
                else:
                    final_unit = custom_unit.strip() or unit
                    add_item(name.strip(), category, quantity, price, min_threshold, final_unit, description.strip())
                    st.success(f"Successfully saved **{name}**!")

    # ================= RESTOCK / ADJUST =================
    elif choice == "Restock / Adjust":
        page_header("Restock / Adjust Stock", "Update quantities for incoming shipments or issued items.")
        if df.empty:
            st.info("No items available.")
        else:
            st.dataframe(df[["id", "quantity", "unit", "name", "category", "price", "amount"]], use_container_width=True, hide_index=True)
            total_bar(df)
            
            col1, col2 = st.columns(2)
            with col1:
                item_id = st.selectbox("Select Item ID", df["id"].tolist())
                selected = df[df["id"] == item_id].iloc[0]
            with col2:
                st.markdown(f"**Item:** {selected['name']}  \n**Current Qty:** {selected['quantity']} {selected['unit']}")
                new_qty = st.number_input("New total quantity", min_value=0, value=int(selected["quantity"]), step=1)
                if st.button("Update Quantity", use_container_width=True):
                    update_quantity(item_id, new_qty)
                    st.success(f"Updated quantity for **{selected['name']}**!")
                    st.rerun()

    # ================= REMOVE ITEM =================
    elif choice == "Remove Item":
        page_header("Remove Item", "Permanently delete items from the inventory.")
        if df.empty:
            st.info("No items available.")
        else:
            st.dataframe(df[["id", "quantity", "unit", "name", "category"]], use_container_width=True, hide_index=True)
            item_id_del = st.selectbox("Select Item ID to Delete", df["id"].tolist())
            selected_del = df[df["id"] == item_id_del].iloc[0]
            st.warning(f"You are about to delete **{selected_del['name']}**. This cannot be undone.")
            if st.button("Permanently Delete", type="primary"):
                delete_item(item_id_del)
                st.success("Item deleted successfully.")
                st.rerun()


if __name__ == "__main__":
    main()
