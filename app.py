import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from database import (
    add_customer,
    add_order,
    add_cake,
    update_cake,
    delete_cake,
    get_cakes,
    get_dashboard_data,
    get_orders,
    get_recent_orders,
    get_sales_by_cake,
    get_sales_by_day,
    generate_practice_orders,
)

st.set_page_config(
    page_title="Sweet Cake Shop",
    page_icon="🎂",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: #fffaf8;
    }

    [data-testid="stSidebar"] {
        background: #f3f5f9;
    }

    .brand {
        font-size: 30px;
        font-weight: 800;
        color: #203a5f;
        margin-bottom: 2px;
    }

    .subtitle {
        color: #7a8491;
        font-size: 14px;
        margin-bottom: 22px;
    }

    .hero {
        padding: 34px;
        border-radius: 0 0 28px 28px;
        background: linear-gradient(135deg, #ff6f91, #ff9eb3);
        box-shadow: 0 14px 30px rgba(205, 95, 125, .18);
        margin-bottom: 24px;
    }

    .hero h1 {
        color: #203a5f;
        font-size: 34px;
        margin: 0 0 8px 0;
    }

    .hero p {
        color: #34495e;
        font-size: 17px;
        margin: 0;
    }

    .section-title {
        font-size: 27px;
        font-weight: 800;
        color: #203a5f;
        margin: 20px 0 14px 0;
    }

    .cake-card {
        background: white;
        border: 1px solid #f0d9d4;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 7px 20px rgba(50, 50, 50, .06);
    }

    .cake-name {
        font-size: 20px;
        font-weight: 700;
        color: #203a5f;
    }

    .price {
        font-size: 18px;
        font-weight: 700;
        color: #d24b73;
    }

    .metric-note {
        color: #7a8491;
        font-size: 13px;
        margin-top: -10px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #f0d9d4;
        padding: 16px;
        border-radius: 16px;
        box-shadow: 0 7px 20px rgba(50, 50, 50, .05);
    }

    .footer {
        text-align: center;
        color: #8993a0;
        padding: 30px 0 10px 0;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand">🍰 Sweet Cake Shop</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Cake Shop Management System</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "🍰 Cake Menu",
            "🛒 Order Cake",
            "📊 Dashboard",
            "🔐 Admin",
        ],
        label_visibility="visible",
    )

    st.divider()
    st.info("Fresh Cakes • Happy Customers 💗")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def money(value):
    return f"₹{float(value):,.0f}"


def create_excel_report():
    orders = get_orders()

    if not orders:
        return None

    df = pd.DataFrame(
        orders,
        columns=[
            "Order ID", "Customer", "Phone", "Cake",
            "Flavor", "Quantity", "Amount", "Order Date"
        ],
    )

    summary = pd.DataFrame({
        "Metric": [
            "Total Orders",
            "Total Sales",
            "Total Cakes Sold",
            "Total Customers",
        ],
        "Value": [
            len(df),
            df["Amount"].sum(),
            df["Quantity"].sum(),
            df["Customer"].nunique(),
        ],
    })

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sales Report")
        summary.to_excel(writer, index=False, sheet_name="Summary")

    output.seek(0)
    return output


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------
if page == "🏠 Home":
    total_cakes, total_orders, total_customers, total_sales, sold, low_stock = get_dashboard_data()

    st.markdown("""
    <div class="hero">
        <h1>🎂 Welcome to Sweet Cake Shop</h1>
        <p>Freshly baked cakes for birthdays, anniversaries and every special moment.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🍰 Available Cakes", total_cakes)
    c2.metric("🛒 Total Orders", total_orders)
    c3.metric("👥 Customers", total_customers)
    c4.metric("💰 Total Sales", money(total_sales))

    st.markdown('<div class="section-title">🎉 Celebrate Every Moment</div>', unsafe_allow_html=True)

    a, b, c = st.columns(3)
    with a:
        st.info("🎂 Birthday Cakes\n\nPerfect cakes for birthday celebrations.")
    with b:
        st.success("💍 Anniversary Cakes\n\nMake your special day sweeter.")
    with c:
        st.warning("🎊 Celebration Cakes\n\nBeautiful cakes for every occasion.")

    st.markdown('<div class="section-title">📦 Recent Orders</div>', unsafe_allow_html=True)

    recent = get_recent_orders(8)
    if recent:
        df = pd.DataFrame(
            recent,
            columns=["Order ID", "Customer", "Cake", "Quantity", "Amount", "Order Date"]
        )
        df["Amount"] = df["Amount"].apply(money)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No orders yet. Go to Order Cake and place your first order.")

# ---------------------------------------------------------
# CAKE MENU
# ---------------------------------------------------------
elif page == "🍰 Cake Menu":
    st.markdown('<div class="section-title">🍰 Our Cake Menu</div>', unsafe_allow_html=True)
    st.caption("Choose from our freshly baked cake collection.")

    cakes = get_cakes()

    if not cakes:
        st.warning("No cakes available.")
    else:
        cols = st.columns(3)

        for i, cake in enumerate(cakes):
            cake_id, name, flavor, price, quantity = cake

            with cols[i % 3]:
                st.markdown(f"""
                <div class="cake-card">
                    <div style="font-size:42px;">🎂</div>
                    <div class="cake-name">{name}</div>
                    <div style="color:#7a8491;">Flavor: {flavor}</div>
                    <br>
                    <div class="price">{money(price)}</div>
                    <div>Stock: <b>{quantity}</b></div>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# ORDER CAKE
# ---------------------------------------------------------
elif page == "🛒 Order Cake":
    st.markdown('<div class="section-title">🛒 Place a New Order</div>', unsafe_allow_html=True)

    cakes = get_cakes()
    available_cakes = [c for c in cakes if c[4] > 0]

    if not available_cakes:
        st.error("No cakes are currently in stock. Please update stock from Admin.")
    else:
        cake_options = {
            f"{c[1]} — {money(c[3])} — Stock: {c[4]}": c
            for c in available_cakes
        }

        selected_label = st.selectbox("Select Cake", list(cake_options.keys()))
        selected = cake_options[selected_label]

        cake_id, cake_name, flavor, price, stock = selected

        st.write(f"**Flavor:** {flavor}  |  **Price:** {money(price)}  |  **Stock:** {stock}")

        with st.form("order_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                customer_name = st.text_input("Customer Name")
                phone = st.text_input("Phone Number")

            with col2:
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=int(stock),
                    value=1,
                    step=1,
                )
                total = float(price) * int(quantity)
                st.metric("Order Total", money(total))

            submitted = st.form_submit_button("🎂 Place Order", use_container_width=True)

            if submitted:
                if not customer_name.strip():
                    st.error("Please enter customer name.")
                elif not phone.strip():
                    st.error("Please enter phone number.")
                elif len(phone.strip()) < 10:
                    st.error("Please enter a valid phone number.")
                else:
                    try:
                        customer_id = add_customer(customer_name, phone)
                        add_order(customer_id, cake_id, quantity, total)
                        st.success("🎉 Order placed successfully!")
                        st.balloons()
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Unable to place order: {e}")

# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
elif page == "📊 Dashboard":
    st.markdown('<div class="section-title">📊 Sales Dashboard</div>', unsafe_allow_html=True)

    total_cakes, total_orders, total_customers, total_sales, sold, low_stock = get_dashboard_data()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🍰 Cake Types", total_cakes)
    c2.metric("🛒 Total Orders", total_orders)
    c3.metric("👥 Customers", total_customers)
    c4.metric("💰 Total Sales", money(total_sales))

    st.caption(f"Total cakes sold: {sold}  •  Low-stock items: {low_stock}")

    st.divider()

    sales_by_cake = get_sales_by_cake()
    daily_sales = get_sales_by_day()

    left, right = st.columns(2)

    with left:
        st.subheader("🏆 Best-Selling Cakes")
        if sales_by_cake:
            df = pd.DataFrame(
                sales_by_cake,
                columns=["Cake", "Units Sold", "Sales"]
            )
            chart = px.bar(
                df.head(8),
                x="Cake",
                y="Sales",
                title="Sales by Cake"
            )
            chart.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No sales data available.")

    with right:
        st.subheader("📈 Sales Trend")
        if daily_sales:
            df = pd.DataFrame(
                daily_sales,
                columns=["Date", "Sales"]
            )
            chart = px.line(
                df,
                x="Date",
                y="Sales",
                markers=True,
                title="Daily Sales"
            )
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No sales data available.")

    st.divider()

    st.subheader("🧾 Recent Orders")
    orders = get_orders()

    if orders:
        df = pd.DataFrame(
            orders,
            columns=[
                "Order ID", "Customer", "Phone", "Cake",
                "Flavor", "Quantity", "Amount", "Order Date"
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        report = create_excel_report()
        if report:
            st.download_button(
                "📥 Download Sales Report (Excel)",
                data=report,
                file_name="sweet_cake_sales_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    else:
        st.info("No orders yet. Place orders from the Order Cake page.")

# ---------------------------------------------------------
# ADMIN
# ---------------------------------------------------------
elif page == "🔐 Admin":
    st.markdown('<div class="section-title">🔐 Admin Panel</div>', unsafe_allow_html=True)

    password = st.text_input(
        "Admin Password",
        type="password",
        placeholder="Enter admin password"
    )

    if password == "admin123":
        st.success("Admin access granted.")

        tab1, tab2, tab3, tab4 = st.tabs([
            "➕ Add Cake",
            "✏️ Update Cake",
            "🗑️ Delete Cake",
            "🧪 Practice Orders",
        ])

        with tab1:
            st.subheader("Add New Cake")
            with st.form("add_cake_form", clear_on_submit=True):
                name = st.text_input("Cake Name")
                flavor = st.text_input("Flavor")
                price = st.number_input("Price", min_value=0.0, value=500.0, step=50.0)
                quantity = st.number_input("Stock Quantity", min_value=0, value=10, step=1)

                if st.form_submit_button("➕ Add Cake", use_container_width=True):
                    if not name.strip():
                        st.error("Cake name is required.")
                    else:
                        add_cake(name, flavor, price, quantity)
                        st.success("Cake added successfully.")
                        st.rerun()

        with tab2:
            cakes = get_cakes()

            if cakes:
                options = {f"{c[1]} (ID {c[0]})": c for c in cakes}
                selected_label = st.selectbox("Select Cake to Update", list(options.keys()))
                cake = options[selected_label]

                with st.form("update_cake_form"):
                    new_name = st.text_input("Cake Name", value=cake[1])
                    new_flavor = st.text_input("Flavor", value=cake[2] or "")
                    new_price = st.number_input("Price", min_value=0.0, value=float(cake[3]), step=50.0)
                    new_qty = st.number_input("Stock", min_value=0, value=int(cake[4]), step=1)

                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        update_cake(cake[0], new_name, new_flavor, new_price, new_qty)
                        st.success("Cake updated successfully.")
                        st.rerun()

        with tab3:
            cakes = get_cakes()

            if cakes:
                options = {f"{c[1]} (ID {c[0]})": c[0] for c in cakes}
                selected_label = st.selectbox("Select Cake to Delete", list(options.keys()))

                if st.button("🗑️ Delete Selected Cake", use_container_width=True):
                    ok = delete_cake(options[selected_label])

                    if ok:
                        st.success("Cake deleted successfully.")
                        st.rerun()
                    else:
                        st.error("This cake already has orders, so it cannot be deleted. Update its stock instead.")

        with tab4:
            st.subheader("Generate Practice Orders")
            st.caption("Use this only for demo/portfolio data. It creates sample customers and orders.")

            count = st.number_input(
                "Number of Practice Orders",
                min_value=1,
                max_value=500,
                value=50,
                step=10,
            )

            if st.button("🧪 Generate Practice Orders", use_container_width=True):
                created = generate_practice_orders(int(count))
                st.success(f"{created} practice orders created successfully.")
                st.rerun()

        st.divider()
        st.subheader("📦 Current Stock")

        cakes = get_cakes()
        if cakes:
            stock_df = pd.DataFrame(
                cakes,
                columns=["ID", "Cake", "Flavor", "Price", "Stock"]
            )
            st.dataframe(stock_df, use_container_width=True, hide_index=True)

    elif password:
        st.error("Incorrect password.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    '<div class="footer">🎂 Sweet Cake Shop • Cake Shop Management System • Built with Python, Streamlit & SQLite</div>',
    unsafe_allow_html=True
)
