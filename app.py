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
    generate_practice_orders
)


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Sweet Cake Shop",
    page_icon="🍰",
    layout="wide"
)


# =========================================================
# EXCEL REPORT
# =========================================================

def create_excel_report(orders_df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        orders_df.to_excel(
            writer,
            index=False,
            sheet_name="Sales Report"
        )

        summary = pd.DataFrame({

            "Metric": [
                "Total Orders",
                "Total Sales",
                "Total Cakes Sold"
            ],

            "Value": [
                len(orders_df),
                orders_df["Amount"].sum(),
                orders_df["Quantity"].sum()
            ]
        })

        summary.to_excel(
            writer,
            index=False,
            sheet_name="Summary"
        )

    output.seek(0)

    return output


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #fff8f5;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.dashboard-header {
    background: linear-gradient(
        135deg,
        #ff7eb3,
        #ff758c,
        #ff9a9e
    );

    padding: 35px;

    border-radius: 22px;

    margin-bottom: 25px;

    color: white;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.12);
}

.dashboard-header h1 {
    color: white;
    font-size: 38px;
    margin-bottom: 5px;
}

.dashboard-header p {
    color: white;
    font-size: 17px;
}

div[data-testid="stMetric"] {

    background: white;

    padding: 20px;

    border-radius: 18px;

    border: 1px solid #f2dfda;

    box-shadow:
        0 6px 20px rgba(0,0,0,0.07);
}

div[data-testid="stMetricLabel"] {
    font-weight: 700;
}

.section-box {

    background: white;

    padding: 20px;

    border-radius: 18px;

    margin-top: 15px;

    margin-bottom: 15px;

    box-shadow:
        0 5px 18px rgba(0,0,0,0.06);
}

.menu-card {

    background: white;

    padding: 18px;

    border-radius: 16px;

    border: 1px solid #f1e4df;

    margin-bottom: 15px;

    box-shadow:
        0 4px 15px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🍰 Sweet Cake Shop")

st.sidebar.caption(
    "Cake Shop Management System"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "🍰 Cake Menu",
        "🛒 Order Cake",
        "📊 Dashboard",
        "🔐 Admin"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Fresh Cakes • Happy Customers ❤️"
)


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.markdown("""
    <div class="dashboard-header">

        <h1>🍰 Welcome to Sweet Cake Shop</h1>

        <p>
        Freshly baked cakes for every special moment.
        </p>

    </div>
    """, unsafe_allow_html=True)

    total_cakes, total_orders, total_customers, total_sales = (
        get_dashboard_data()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🍰 Available Cakes",
            total_cakes
        )

    with col2:

        st.metric(
            "🛒 Total Orders",
            total_orders
        )

    with col3:

        st.metric(
            "👥 Customers",
            total_customers
        )

    with col4:

        st.metric(
            "💰 Total Sales",
            f"₹{total_sales:,.0f}"
        )

    st.markdown("---")

    st.subheader(
        "🎉 Celebrate Every Moment"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "🎂 Birthday Cakes"
        )

    with col2:

        st.success(
            "💍 Anniversary Cakes"
        )

    with col3:

        st.warning(
            "🎉 Celebration Cakes"
        )


# =========================================================
# CAKE MENU
# =========================================================

elif page == "🍰 Cake Menu":

    st.title("🍰 Cake Menu")

    st.write(
        "Explore our delicious cakes."
    )

    cakes = get_cakes()

    if cakes:

        df = pd.DataFrame(
            cakes,
            columns=[
                "ID",
                "Cake Name",
                "Flavor",
                "Price (₹)",
                "Available Stock"
            ]
        )

        search = st.text_input(
            "🔍 Search Cake",
            placeholder="Search chocolate, vanilla..."
        )

        if search:

            df = df[
                df["Cake Name"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                df["Flavor"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True
        )

    else:

        st.warning(
            "No cakes found."
        )


# =========================================================
# ORDER CAKE
# =========================================================

elif page == "🛒 Order Cake":

    st.title("🛒 Order Your Cake")

    cakes = get_cakes()

    if cakes:

        cake_options = {}

        for cake in cakes:

            cake_id = cake[0]

            cake_name = cake[1]

            price = cake[3]

            stock = cake[4]

            cake_options[
                f"{cake_name} - ₹{price:,.0f} "
                f"(Stock: {stock})"
            ] = {

                "id": cake_id,

                "name": cake_name,

                "price": price,

                "stock": stock
            }

        selected_cake = st.selectbox(
            "🎂 Select Cake",
            list(cake_options.keys())
        )

        selected = cake_options[
            selected_cake
        ]

        st.info(
            f"Selected Cake: {selected['name']} | "
            f"Price: ₹{selected['price']:,.0f} | "
            f"Stock: {selected['stock']}"
        )

        col1, col2 = st.columns(2)

        with col1:

            customer_name = st.text_input(
                "👤 Customer Name"
            )

        with col2:

            phone = st.text_input(
                "📱 Mobile Number"
            )

        max_quantity = max(
            1,
            int(selected["stock"])
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=max_quantity,
            value=1,
            step=1
        )

        total_price = (
            selected["price"]
            * quantity
        )

        st.markdown(
            f"### 💰 Total Amount: ₹{total_price:,.0f}"
        )

        if st.button(
            "🛒 Place Order",
            use_container_width=True,
            type="primary"
        ):

            if not customer_name.strip():

                st.error(
                    "Please enter customer name."
                )

            elif not phone.strip():

                st.error(
                    "Please enter mobile number."
                )

            elif selected["stock"] < quantity:

                st.error(
                    "Not enough stock available."
                )

            else:

                customer_id = add_customer(
                    customer_name,
                    phone
                )

                success = add_order(
                    customer_id,
                    selected["id"],
                    quantity,
                    total_price
                )

                if success:

                    st.success(
                        "✅ Order placed successfully!"
                    )

                    st.balloons()

                    st.write(
                        f"**Customer:** {customer_name}"
                    )

                    st.write(
                        f"**Cake:** {selected['name']}"
                    )

                    st.write(
                        f"**Quantity:** {quantity}"
                    )

                    st.write(
                        f"**Total:** ₹{total_price:,.0f}"
                    )

                else:

                    st.error(
                        "Unable to place order."
                    )

    else:

        st.error(
            "No cakes available."
        )


# =========================================================
# PROFESSIONAL DASHBOARD
# =========================================================

elif page == "📊 Dashboard":

    st.markdown("""
    <div class="dashboard-header">

        <h1>📊 Sweet Cake Shop Dashboard</h1>

        <p>
        Monitor sales, orders, customers and inventory
        from one place.
        </p>

    </div>
    """, unsafe_allow_html=True)

    col_refresh, col_space = st.columns(
        [1, 5]
    )

    with col_refresh:

        if st.button(
            "🔄 Refresh"
        ):

            st.rerun()

    st.markdown("---")

    # -----------------------------------------------------
    # MAIN KPI
    # -----------------------------------------------------

    (
        total_cakes,
        total_orders,
        total_customers,
        total_sales
    ) = get_dashboard_data()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🍰 Total Cakes",
            total_cakes
        )

    with col2:

        st.metric(
            "🛒 Total Orders",
            total_orders
        )

    with col3:

        st.metric(
            "👥 Customers",
            total_customers
        )

    with col4:

        st.metric(
            "💰 Total Sales",
            f"₹{total_sales:,.0f}"
        )

    st.markdown("---")

    # -----------------------------------------------------
    # ORDERS
    # -----------------------------------------------------

    orders = get_orders()

    if orders:

        orders_df = pd.DataFrame(
            orders,
            columns=[
                "Order ID",
                "Customer",
                "Cake",
                "Quantity",
                "Amount",
                "Order Date"
            ]
        )

        orders_df["Order Date"] = pd.to_datetime(
            orders_df["Order Date"],
            errors="coerce"
        )

        # -------------------------------------------------
        # DATE FILTER
        # -------------------------------------------------

        st.subheader(
            "📅 Sales Date Filter"
        )

        min_date = (
            orders_df["Order Date"]
            .min()
            .date()
        )

        max_date = (
            orders_df["Order Date"]
            .max()
            .date()
        )

        col1, col2 = st.columns(2)

        with col1:

            start_date = st.date_input(
                "Start Date",
                value=min_date
            )

        with col2:

            end_date = st.date_input(
                "End Date",
                value=max_date
            )

        if start_date > end_date:

            st.error(
                "Start Date cannot be greater than End Date."
            )

        else:

            filtered_orders = orders_df[
                (
                    orders_df["Order Date"].dt.date
                    >= start_date
                )
                &
                (
                    orders_df["Order Date"].dt.date
                    <= end_date
                )
            ]

            st.info(
                f"Showing {len(filtered_orders)} orders "
                f"from {start_date} to {end_date}"
            )

            # -------------------------------------------------
            # FILTERED KPI
            # -------------------------------------------------

            filtered_sales = (
                filtered_orders["Amount"].sum()
            )

            filtered_order_count = (
                len(filtered_orders)
            )

            filtered_quantity = (
                filtered_orders["Quantity"].sum()
            )

            average_order = (
                filtered_sales
                / filtered_order_count
                if filtered_order_count > 0
                else 0
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💰 Filtered Sales",
                    f"₹{filtered_sales:,.0f}"
                )

            with col2:

                st.metric(
                    "🛒 Filtered Orders",
                    filtered_order_count
                )

            with col3:

                st.metric(
                    "🎂 Cakes Sold",
                    filtered_quantity
                )

            with col4:

                st.metric(
                    "💵 Avg Order",
                    f"₹{average_order:,.0f}"
                )

            st.markdown("---")

            if not filtered_orders.empty:

                # =========================================
                # MONTHLY SALES
                # =========================================

                st.subheader(
                    "📈 Monthly Sales Analysis"
                )

                monthly_sales = (
                    filtered_orders
                    .set_index("Order Date")
                    .resample("ME")["Amount"]
                    .sum()
                    .reset_index()
                )

                monthly_sales["Month"] = (
                    monthly_sales["Order Date"]
                    .dt.strftime("%b %Y")
                )

                fig_monthly = px.line(
                    monthly_sales,
                    x="Month",
                    y="Amount",
                    markers=True,
                    text="Amount",
                    title="Monthly Revenue Trend"
                )

                fig_monthly.update_traces(
                    texttemplate="₹%{text:,.0f}",
                    textposition="top center"
                )

                fig_monthly.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Revenue (₹)",
                    plot_bgcolor="white",
                    paper_bgcolor="white"
                )

                st.plotly_chart(
                    fig_monthly,
                    use_container_width=True
                )

                st.markdown("---")

                # =========================================
                # CAKE ANALYSIS
                # =========================================

                orders_by_cake = (
                    filtered_orders
                    .groupby("Cake")["Quantity"]
                    .sum()
                    .reset_index()
                    .sort_values(
                        "Quantity",
                        ascending=False
                    )
                )

                sales_by_cake = (
                    filtered_orders
                    .groupby("Cake")["Amount"]
                    .sum()
                    .reset_index()
                    .sort_values(
                        "Amount",
                        ascending=False
                    )
                )

                best_cake = (
                    orders_by_cake.iloc[0]["Cake"]
                )

                best_cake_quantity = int(
                    orders_by_cake.iloc[0]["Quantity"]
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.subheader(
                        "🏆 Best Selling Cake"
                    )

                    st.success(
                        f"🎂 {best_cake}\n\n"
                        f"{best_cake_quantity} cakes sold"
                    )

                with col2:

                    st.subheader(
                        "💵 Average Order Value"
                    )

                    st.info(
                        f"₹{average_order:,.0f}"
                    )

                st.markdown("---")

                # =========================================
                # CHARTS
                # =========================================

                col1, col2 = st.columns(2)

                with col1:

                    st.subheader(
                        "💰 Sales by Cake"
                    )

                    fig1 = px.bar(
                        sales_by_cake,
                        x="Cake",
                        y="Amount",
                        text="Amount",
                        title="Cake-wise Sales"
                    )

                    fig1.update_traces(
                        texttemplate="₹%{text:,.0f}",
                        textposition="outside"
                    )

                    fig1.update_layout(
                        xaxis_title="Cake",
                        yaxis_title="Sales (₹)",
                        plot_bgcolor="white",
                        paper_bgcolor="white"
                    )

                    st.plotly_chart(
                        fig1,
                        use_container_width=True
                    )

                with col2:

                    st.subheader(
                        "🍰 Order Distribution"
                    )

                    fig2 = px.pie(
                        orders_by_cake,
                        names="Cake",
                        values="Quantity",
                        hole=0.45,
                        title="Orders by Cake"
                    )

                    st.plotly_chart(
                        fig2,
                        use_container_width=True
                    )

                st.markdown("---")

                # =========================================
                # TOP CUSTOMERS
                # =========================================

                st.subheader(
                    "👥 Top Customers"
                )

                top_customers = (
                    filtered_orders
                    .groupby("Customer")
                    .agg(
                        Orders=("Order ID", "count"),
                        Sales=("Amount", "sum")
                    )
                    .reset_index()
                    .sort_values(
                        "Sales",
                        ascending=False
                    )
                    .head(10)
                )

                top_customers["Sales"] = (
                    top_customers["Sales"]
                    .round(0)
                )

                st.dataframe(
                    top_customers,
                    hide_index=True,
                    use_container_width=True
                )

                st.markdown("---")

                # =========================================
                # RECENT ORDERS
                # =========================================

                st.subheader(
                    "🛒 Recent Orders"
                )

                recent_orders = (
                    filtered_orders
                    .sort_values(
                        "Order Date",
                        ascending=False
                    )
                    .head(10)
                    .copy()
                )

                recent_orders["Order Date"] = (
                    recent_orders["Order Date"]
                    .dt.strftime(
                        "%d-%m-%Y %H:%M"
                    )
                )

                st.dataframe(
                    recent_orders,
                    hide_index=True,
                    use_container_width=True
                )

                st.markdown("---")

                # =========================================
                # EXCEL DOWNLOAD
                # =========================================

                st.subheader(
                    "📥 Download Sales Report"
                )

                excel_file = create_excel_report(
                    filtered_orders
                )

                st.download_button(
                    label="📊 Download Excel Report",
                    data=excel_file,
                    file_name="cake_shop_sales_report.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True
                )

            else:

                st.warning(
                    "No orders found for the selected dates."
                )

    else:

        st.info(
            "📭 No orders available yet. "
            "Place an order from Order Cake."
        )

    # -----------------------------------------------------
    # STOCK MANAGEMENT
    # -----------------------------------------------------

    st.markdown("---")

    st.subheader(
        "⚠️ Stock Management"
    )

    cakes = get_cakes()

    if cakes:

        cakes_df = pd.DataFrame(
            cakes,
            columns=[
                "ID",
                "Cake Name",
                "Flavor",
                "Price",
                "Stock"
            ]
        )

        low_stock = cakes_df[
            cakes_df["Stock"] <= 5
        ]

        if not low_stock.empty:

            st.warning(
                "⚠️ Some cakes have low stock!"
            )

            st.dataframe(
                low_stock,
                hide_index=True,
                use_container_width=True
            )

        else:

            st.success(
                "✅ All cakes have sufficient stock."
            )


# =========================================================
# ADMIN PANEL
# =========================================================

elif page == "🔐 Admin":

    st.title(
        "🔐 Admin Panel"
    )

    st.write(
        "Manage cakes, inventory and practice data."
    )

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    if "admin_logged_in" not in st.session_state:

        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:

        st.subheader(
            "Admin Login"
        )

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True,
            type="primary"
        ):

            if (
                username == "admin"
                and password == "admin123"
            ):

                st.session_state.admin_logged_in = True

                st.success(
                    "Login successful!"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    # -----------------------------------------------------
    # ADMIN AREA
    # -----------------------------------------------------

    else:

        st.success(
            "Welcome Admin! 👋"
        )

        admin_option = st.selectbox(
            "Select Admin Action",
            [
                "Add Cake",
                "Update Cake",
                "Delete Cake",
                "View Cakes",
                "Generate Practice Orders"
            ]
        )

        # ================================================
        # ADD CAKE
        # ================================================

        if admin_option == "Add Cake":

            st.subheader(
                "➕ Add New Cake"
            )

            cake_name = st.text_input(
                "Cake Name"
            )

            flavor = st.text_input(
                "Flavor"
            )

            price = st.number_input(
                "Price",
                min_value=0.0,
                step=50.0
            )

            quantity = st.number_input(
                "Stock Quantity",
                min_value=0,
                step=1
            )

            if st.button(
                "➕ Add Cake",
                use_container_width=True
            ):

                if cake_name and flavor:

                    add_cake(
                        cake_name,
                        flavor,
                        price,
                        quantity
                    )

                    st.success(
                        "Cake added successfully! 🎂"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Please enter cake name and flavor."
                    )

        # ================================================
        # UPDATE CAKE
        # ================================================

        elif admin_option == "Update Cake":

            st.subheader(
                "✏️ Update Cake"
            )

            cakes = get_cakes()

            if cakes:

                cake_dict = {}

                for cake in cakes:

                    cake_dict[
                        f"{cake[1]} - ID {cake[0]}"
                    ] = cake

                selected = st.selectbox(
                    "Select Cake",
                    list(cake_dict.keys())
                )

                cake = cake_dict[selected]

                cake_id = cake[0]

                cake_name = st.text_input(
                    "Cake Name",
                    value=cake[1]
                )

                flavor = st.text_input(
                    "Flavor",
                    value=cake[2]
                )

                price = st.number_input(
                    "Price",
                    min_value=0.0,
                    value=float(cake[3])
                )

                quantity = st.number_input(
                    "Stock",
                    min_value=0,
                    value=int(cake[4])
                )

                if st.button(
                    "💾 Update Cake",
                    use_container_width=True
                ):

                    update_cake(
                        cake_id,
                        cake_name,
                        flavor,
                        price,
                        quantity
                    )

                    st.success(
                        "Cake updated successfully! ✅"
                    )

                    st.rerun()

            else:

                st.info(
                    "No cakes available."
                )

        # ================================================
        # DELETE CAKE
        # ================================================

        elif admin_option == "Delete Cake":

            st.subheader(
                "🗑️ Delete Cake"
            )

            cakes = get_cakes()

            if cakes:

                cake_dict = {}

                for cake in cakes:

                    cake_dict[
                        f"{cake[1]} - ID {cake[0]}"
                    ] = cake[0]

                selected = st.selectbox(
                    "Select Cake",
                    list(cake_dict.keys())
                )

                cake_id = cake_dict[selected]

                if st.button(
                    "🗑️ Delete Cake",
                    use_container_width=True
                ):

                    delete_cake(
                        cake_id
                    )

                    st.success(
                        "Cake deleted successfully."
                    )

                    st.rerun()

            else:

                st.info(
                    "No cakes available."
                )

        # ================================================
        # VIEW CAKES
        # ================================================

        elif admin_option == "View Cakes":

            st.subheader(
                "🍰 Cake Inventory"
            )

            cakes = get_cakes()

            if cakes:

                df = pd.DataFrame(
                    cakes,
                    columns=[
                        "ID",
                        "Cake Name",
                        "Flavor",
                        "Price",
                        "Stock"
                    ]
                )

                st.dataframe(
                    df,
                    hide_index=True,
                    use_container_width=True
                )

            else:

                st.info(
                    "No cakes available."
                )

        # ================================================
        # PRACTICE ORDERS
        # ================================================

        elif admin_option == "Generate Practice Orders":

            st.subheader(
                "📊 Generate Practice Orders"
            )

            st.info(
                "Use this option to create sample "
                "orders for testing the Dashboard."
            )

            number_of_orders = st.number_input(
                "Number of Orders",
                min_value=1,
                max_value=500,
                value=50,
                step=10
            )

            if st.button(
                "🚀 Generate Orders",
                use_container_width=True,
                type="primary"
            ):

                created = generate_practice_orders(
                    number_of_orders
                )

                st.success(
                    f"✅ {created} practice orders created!"
                )

                st.rerun()

        # ================================================
        # LOGOUT
        # ================================================

        st.markdown("---")

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.admin_logged_in = False

            st.rerun()