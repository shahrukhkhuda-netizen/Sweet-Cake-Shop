import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from database import (
    get_cakes,
    add_customer,
    add_order,
    get_orders,
    get_dashboard_data,
    add_cake,
    update_cake,
    delete_cake,
    generate_practice_orders,
)

st.set_page_config(
    page_title="Sweet Cake Shop",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# PROFESSIONAL CSS
# -----------------------------
st.markdown("""
<style>
.stApp { background: #fff8f5; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fff0f5 0%, #fff8f5 100%);
}

.hero {
    padding: 28px 32px;
    border-radius: 22px;
    background: linear-gradient(135deg, #ff7eb3 0%, #ff758c 100%);
    color: white;
    box-shadow: 0 10px 30px rgba(220, 80, 120, .18);
    margin-bottom: 24px;
}
.hero h1 { color: white; margin: 0; font-size: 2.25rem; }
.hero p { color: white; margin: 8px 0 0; font-size: 1rem; }

.section {
    background: white;
    border-radius: 16px;
    padding: 18px 20px;
    margin: 18px 0 12px;
    box-shadow: 0 5px 18px rgba(0,0,0,.06);
    border: 1px solid #f1e4df;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f1e4df;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 5px 18px rgba(0,0,0,.06);
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


def create_excel_report(orders_df):
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            orders_df.to_excel(writer, index=False, sheet_name="Sales Report")
            summary = pd.DataFrame({
                "Metric": [
                    "Total Orders",
                    "Total Sales",
                    "Total Cakes Sold",
                ],
                "Value": [
                    len(orders_df),
                    float(orders_df["Amount"].sum()),
                    int(orders_df["Quantity"].sum()),
                ],
            })
            summary.to_excel(writer, index=False, sheet_name="Summary")
        output.seek(0)
        return output
    except ModuleNotFoundError:
        return None


def orders_dataframe():
    orders = get_orders()
    if not orders:
        return pd.DataFrame(
            columns=["Order ID", "Customer", "Cake", "Quantity", "Amount", "Order Date"]
        )

    df = pd.DataFrame(
        orders,
        columns=["Order ID", "Customer", "Cake", "Quantity", "Amount", "Order Date"],
    )
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    return df


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown("## 🍰 Sweet Cake Shop")
st.sidebar.caption("Cake Shop Management System")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🍰 Cake Menu", "🛒 Order Cake", "📊 Dashboard", "🔐 Admin"],
)

st.sidebar.markdown("---")
st.sidebar.info("Python • Streamlit • SQLite • Pandas • Plotly")


# =============================
# HOME
# =============================
if page == "🏠 Home":
    st.markdown("""
    <div class="hero">
        <h1>🍰 Sweet Cake Shop</h1>
        <p>Fresh cakes for birthdays, anniversaries and every special moment.</p>
    </div>
    """, unsafe_allow_html=True)

    total_cakes, total_orders, total_customers, total_sales = get_dashboard_data()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🍰 Cake Types", total_cakes)
    c2.metric("🛒 Total Orders", total_orders)
    c3.metric("👥 Customers", total_customers)
    c4.metric("💰 Total Sales", f"₹{total_sales:,.0f}")

    st.markdown('<div class="section"><h3>✨ Why Sweet Cake Shop?</h3><p>Manage cakes, customers, orders, inventory and sales reports from one simple dashboard.</p></div>', unsafe_allow_html=True)

    st.subheader("🎂 Popular Categories")
    a, b, c, d = st.columns(4)
    a.info("🍫 Chocolate")
    b.info("🍓 Strawberry")
    c.info("❤️ Red Velvet")
    d.info("🍍 Pineapple")


# =============================
# CAKE MENU
# =============================
elif page == "🍰 Cake Menu":
    st.title("🍰 Cake Menu")
    st.caption("Live cake inventory from SQLite database.")

    cakes = get_cakes()
    if cakes:
        df = pd.DataFrame(
            cakes,
            columns=["ID", "Cake Name", "Flavor", "Price (₹)", "Stock"],
        )

        search = st.text_input("🔍 Search cake")
        flavor = st.selectbox(
            "Filter by flavor",
            ["All"] + sorted(df["Flavor"].dropna().unique().tolist()),
        )

        if search:
            df = df[df["Cake Name"].str.contains(search, case=False, na=False)]
        if flavor != "All":
            df = df[df["Flavor"] == flavor]

        st.dataframe(df, hide_index=True, width="stretch")

        st.subheader("📦 Inventory Summary")
        x, y, z = st.columns(3)
        x.metric("Cake Types", len(df))
        y.metric("Total Stock", int(df["Stock"].sum()))
        z.metric("Low Stock Items", int((df["Stock"] <= 5).sum()))
    else:
        st.warning("No cakes found in database.")


# =============================
# ORDER CAKE
# =============================
elif page == "🛒 Order Cake":
    st.title("🛒 Order Your Cake")
    cakes = get_cakes()

    if not cakes:
        st.error("No cakes are available.")
    else:
        options = {}
        for cake in cakes:
            cake_id, name, flavor, price, stock = cake
            options[f"{name} — ₹{price:,.0f} | Stock: {stock}"] = {
                "id": cake_id,
                "name": name,
                "price": float(price),
                "stock": int(stock),
            }

        selected_label = st.selectbox("Select Cake", list(options.keys()))
        selected = options[selected_label]

        c1, c2 = st.columns(2)
        with c1:
            customer_name = st.text_input("Customer Name")
        with c2:
            phone = st.text_input("Mobile Number")

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=max(1, selected["stock"]),
            value=1,
            step=1,
        )

        total = selected["price"] * quantity
        st.success(f"💰 Total Amount: ₹{total:,.0f}")

        if st.button("🛒 Place Order", width="stretch"):
            if not customer_name.strip() or not phone.strip():
                st.error("Please enter customer name and mobile number.")
            elif selected["stock"] < quantity:
                st.error("Not enough stock available.")
            else:
                customer_id = add_customer(customer_name.strip(), phone.strip())
                add_order(customer_id, selected["id"], quantity, total)
                st.success("✅ Order placed successfully!")
                st.balloons()


# =============================
# DASHBOARD
# =============================
elif page == "📊 Dashboard":
    st.markdown("""
    <div class="hero">
        <h1>📊 Sales Dashboard</h1>
        <p>Monitor revenue, orders, customers and cake performance.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

    total_cakes, total_orders, total_customers, total_sales = get_dashboard_data()
    orders_df = orders_dataframe()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🍰 Cake Types", total_cakes)
    c2.metric("🛒 Orders", total_orders)
    c3.metric("👥 Customers", total_customers)
    c4.metric("💰 Revenue", f"₹{total_sales:,.0f}")

    if orders_df.empty:
        st.info("📭 No orders yet. Place an order or generate practice orders from Admin.")
    else:
        min_date = orders_df["Order Date"].min().date()
        max_date = orders_df["Order Date"].max().date()

        st.markdown('<div class="section"><h3>📅 Sales Filter</h3></div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            start_date = st.date_input("Start Date", value=min_date)
        with d2:
            end_date = st.date_input("End Date", value=max_date)

        if start_date > end_date:
            st.error("Start Date cannot be greater than End Date.")
        else:
            filtered = orders_df[
                (orders_df["Order Date"].dt.date >= start_date)
                & (orders_df["Order Date"].dt.date <= end_date)
            ].copy()

            sales = float(filtered["Amount"].sum())
            count = len(filtered)
            quantity = int(filtered["Quantity"].sum())

            a, b, c = st.columns(3)
            a.metric("💰 Filtered Sales", f"₹{sales:,.0f}")
            b.metric("🛒 Filtered Orders", count)
            c.metric("🎂 Cakes Sold", quantity)

            if not filtered.empty:
                filtered["Month"] = filtered["Order Date"].dt.to_period("M").astype(str)
                monthly = filtered.groupby("Month", as_index=False)["Amount"].sum()

                st.subheader("📈 Revenue Trend")
                fig = px.line(monthly, x="Month", y="Amount", markers=True)
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, width="stretch")

                cake_sales = (
                    filtered.groupby("Cake", as_index=False)["Amount"]
                    .sum()
                    .sort_values("Amount", ascending=False)
                )
                cake_qty = (
                    filtered.groupby("Cake", as_index=False)["Quantity"]
                    .sum()
                    .sort_values("Quantity", ascending=False)
                )

                a, b = st.columns(2)
                with a:
                    st.subheader("💰 Sales by Cake")
                    fig1 = px.bar(cake_sales, x="Cake", y="Amount")
                    fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    st.plotly_chart(fig1, width="stretch")
                with b:
                    st.subheader("🍰 Order Distribution")
                    fig2 = px.pie(cake_qty, names="Cake", values="Quantity", hole=0.45)
                    st.plotly_chart(fig2, width="stretch")

                best = cake_qty.iloc[0]["Cake"]
                best_qty = int(cake_qty.iloc[0]["Quantity"])
                avg_order = sales / count if count else 0

                a, b = st.columns(2)
                a.success(f"🏆 Best Selling Cake: {best} ({best_qty} cakes)")
                b.info(f"💵 Average Order Value: ₹{avg_order:,.0f}")

                st.subheader("🛒 Recent Orders")
                recent = filtered.sort_values("Order Date", ascending=False).head(10).copy()
                recent["Order Date"] = recent["Order Date"].dt.strftime("%d-%m-%Y %H:%M")
                st.dataframe(recent, hide_index=True, width="stretch")

            st.markdown("---")
            st.subheader("📥 Download Sales Report")
            excel_file = create_excel_report(filtered)

            if excel_file is not None:
                st.download_button(
                    "📊 Download Excel Report",
                    data=excel_file,
                    file_name="cake_shop_sales_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch",
                )
            else:
                st.error("openpyxl is not installed in the active venv. Run: .\\venv\\Scripts\\python.exe -m pip install openpyxl")


# =============================
# ADMIN
# =============================
elif page == "🔐 Admin":
    st.title("🔐 Admin Panel")
    st.caption("Manage cake inventory and generate practice data.")

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("🔐 Login", width="stretch"):
            if username == "admin" and password == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password.")
    else:
        st.success("Welcome Admin! 👋")

        action = st.selectbox(
            "Admin Action",
            ["Add Cake", "Update Cake", "Delete Cake", "View Cakes", "Generate Practice Orders"],
        )

        if action == "Generate Practice Orders":
            st.subheader("📊 Generate Practice Orders")
            st.write("Creates demo orders for dashboard practice. Cake stock is not reduced.")
            number = st.number_input("Number of Orders", min_value=1, max_value=500, value=50, step=10)

            if st.button("🚀 Generate Practice Orders", width="stretch"):
                created = generate_practice_orders(int(number))
                st.success(f"✅ {created} practice orders created.")
                st.info("Go to Dashboard and press Refresh Dashboard.")

        elif action == "Add Cake":
            st.subheader("➕ Add Cake")
            name = st.text_input("Cake Name")
            flavor = st.text_input("Flavor")
            price = st.number_input("Price", min_value=0.0, step=50.0)
            stock = st.number_input("Stock", min_value=0, step=1)

            if st.button("➕ Add Cake", width="stretch"):
                if name.strip() and flavor.strip():
                    add_cake(name.strip(), flavor.strip(), price, stock)
                    st.success("Cake added successfully.")
                    st.rerun()
                else:
                    st.error("Enter cake name and flavor.")

        elif action == "Update Cake":
            cakes = get_cakes()
            if cakes:
                mapping = {f"{c[1]} — ID {c[0]}": c for c in cakes}
                selected = st.selectbox("Select Cake", list(mapping.keys()))
                cake = mapping[selected]

                name = st.text_input("Cake Name", value=cake[1])
                flavor = st.text_input("Flavor", value=cake[2])
                price = st.number_input("Price", min_value=0.0, value=float(cake[3]))
                stock = st.number_input("Stock", min_value=0, value=int(cake[4]))

                if st.button("💾 Update Cake", width="stretch"):
                    update_cake(cake[0], name, flavor, price, stock)
                    st.success("Cake updated successfully.")
                    st.rerun()

        elif action == "Delete Cake":
            cakes = get_cakes()
            if cakes:
                mapping = {f"{c[1]} — ID {c[0]}": c[0] for c in cakes}
                selected = st.selectbox("Select Cake", list(mapping.keys()))
                if st.button("🗑️ Delete Cake", width="stretch"):
                    delete_cake(mapping[selected])
                    st.success("Cake deleted successfully.")
                    st.rerun()

        elif action == "View Cakes":
            cakes = get_cakes()
            if cakes:
                df = pd.DataFrame(cakes, columns=["ID", "Cake Name", "Flavor", "Price", "Stock"])
                st.dataframe(df, hide_index=True, width="stretch")

        st.markdown("---")
        if st.button("🚪 Logout", width="stretch"):
            st.session_state.admin_logged_in = False
            st.rerun()