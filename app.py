import streamlit as st
import pandas as pd
import plotly.express as px

def show_eda():
    # ------------------ CUSTOM CSS ------------------
    st.markdown("""
        <style>
            .main {
                background-color: #0E1117;
            }
            .stMetric {
                background-color: #1c1f26;
                padding: 10px;
                border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # ------------------ TITLE ------------------
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        .stApp {
            font-family: 'Poppins', sans-serif;
        }

        h1 {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>🧑🏻Customer Sales Insights Engine 📊</h1>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

    # ------------------ LOAD DATA ------------------
    @st.cache_data
    def load_data():
        df = pd.read_csv("data/Custmer_sales.csv", encoding='ISO-8859-1')
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='mixed', errors='coerce')
        df.dropna(inplace=True)
        # Reduce memory usage
        df['Country'] = df['Country'].astype('category')
        df['Description'] = df['Description'].astype('category')
        
        return df

    df = load_data()
    # Safe sampling (prevents crash)
    if len(df) > 2000:
        df = df.sample(2000, random_state=42)


    # ------------------ SIDEBAR ------------------
    st.sidebar.header("🔍 Filters")

    country = st.sidebar.multiselect(
        "Select Country",
        options=df["Country"].unique().tolist(),
        default=df["Country"].unique().tolist()
    )

    date_range = st.sidebar.date_input(
        "Select Date Range",
        [df['InvoiceDate'].min(), df['InvoiceDate'].max()]
    )

    # Filter Data
    filtered_df = df[
        (df['Country'].isin(country)) &
        (df['InvoiceDate'].dt.date >= date_range[0]) &
        (df['InvoiceDate'].dt.date <= date_range[1])
    ]

    # ------------------ KPI METRICS ------------------
    total_sales = (filtered_df['Quantity'] * filtered_df['UnitPrice']).sum()
    total_orders = filtered_df['InvoiceNo'].nunique()
    total_customers = filtered_df['CustomerID'].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Total Sales", f"${total_sales:,.2f}", delta="+5%")
    col2.metric("🧾 Total Orders", total_orders, delta="-2%")
    col3.metric("👥 Customers", total_customers, delta="+3%")

    def center_title(fig):
        fig.update_layout(title_x=0.5)
        return fig

    # ------------------ CHARTS ------------------

    # 1. Sales by Country
    st.markdown("<h3 style='text-align: center;'>🌍 Sales by Country</h3>", unsafe_allow_html=True)
    country_sales = filtered_df.groupby('Country')['Quantity'].sum().nlargest(10).reset_index()

    fig1 = px.bar(
        country_sales,
        x='Country',
        y='Quantity',
        color='Quantity',
        template='plotly_dark'
    )

    fig1.update_traces(marker_line_width=1.5, marker_line_color='white', marker=dict(line=dict(color='white', width=1.5)))
    fig1.update_layout(
        title="Sales by Country",
        xaxis_title="Country",
        yaxis_title="Total Quantity Sold",
        coloraxis_showscale=False,
    )
    st.plotly_chart(center_title(fig1), use_container_width=True)
    st.markdown("<p style='text-align: center;'>This chart shows the Overall Sales completed in Every Country.</p>", unsafe_allow_html=True)

    # Total Products
    st.markdown("<h3 style='text-align: center;'>Top Products</h3>", unsafe_allow_html=True)
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    top_products = (
        df.groupby("Description")[["TotalPrice","Quantity","UnitPrice"]]
        .sum()
        .sort_values(ascending=False, by=['Quantity','UnitPrice'])
        .head(10)
        .reset_index()
    )

    st.dataframe(top_products, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This Table Shows the Top Products Sold with there appropriate quantity as well as unit price</p>", unsafe_allow_html=True)

    # Daily Sales 
    st.markdown("<h3 style='text-align: center;'>Daily Sales</h3>", unsafe_allow_html=True)
    daily_sales = (
        df.groupby(df["InvoiceDate"].dt.date)["TotalPrice"].sum()
    )

    st.dataframe(daily_sales, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This Table Shows the Daily Sales of everyday with the total price.</p>", unsafe_allow_html=True)


    # -------------------------------------------------------------------------------------------------------------
    # 2. Top Products
    st.markdown("<h3 style='text-align: center;'>Top 10 Products</h3>", unsafe_allow_html=True)
    top_products = filtered_df.groupby('Description')['Quantity'].sum().nlargest(10).reset_index()

    fig2 = px.bar(
        top_products,
        x='Quantity',
        y='Description',
        title="Top Products",
        orientation='h',
        color='Quantity',
        template='plotly_dark'
    )

    fig2.update_traces(marker_line_width=1.5, marker_line_color='white', opacity=0.8, marker=dict(line=dict(color='white', width=1.5)))
    fig2.update_layout(
        title="Top Products",
        xaxis_title="Total Quantity Sold",
        yaxis_title="Product Description",
        coloraxis_showscale=False
    )
    st.plotly_chart(center_title(fig2), use_container_width=True)
    st.markdown("<p style='text-align: center;'>This chart shows the top products that have generated more revenue for the business.</p>", unsafe_allow_html=True)

    # Top Expensive products
    st.markdown("<h3 style='text-align: center;'>Top Expensive Products</h3>", unsafe_allow_html=True)
    expensive_products = (
        df.groupby("Description")["UnitPrice"]
        .max()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    st.dataframe(expensive_products, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This Table Shows the Top Expensive Products in the Market with there Unit Price.</p>", unsafe_allow_html=True)

    # 3. Sales Over Time
    st.markdown("<h3 style='text-align: center;'>Sales Over Time </h3>", unsafe_allow_html=True)
    filtered_df['Date'] = filtered_df['InvoiceDate'].dt.date
    time_sales = filtered_df.groupby('Date')['Quantity'].sum().reset_index()

    fig3 = px.line(
        time_sales,
        x='Date',
        y='Quantity',
        title="Sales Over Time",
        markers=True,
        template='plotly_dark'
    )

    fig3.update_traces(marker=dict(color='#00FFFF', size=8))
    fig3.update_layout(
        title="Sales Over Time",
        xaxis_title="Date",
        yaxis_title="Total Quantity Sold"
    )
    st.plotly_chart(center_title(fig3), use_container_width=True)
    st.markdown("<p style='text-align: center;'>This chart shows total revenue contribution from each country, helping identify top-performing markets.</p>", unsafe_allow_html=True)

    # Monthly Sales 
    st.markdown("<h3 style='text-align: center;'>Monthly Sales</h3>", unsafe_allow_html=True)
    monthly_sales = (
        df.groupby(df["InvoiceDate"].dt.to_period("M"))["TotalPrice"]
        .sum()
    )
    
    st.dataframe(monthly_sales, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This Table Shows the Monthly Sales over a 30 day period of time.</p>", unsafe_allow_html=True)

    # Top Sales per Invoice
    st.markdown("<h3 style='text-align: center;'>Top Sales per Invoice</h3>", unsafe_allow_html=True)
    invoice_sales = (
        df.groupby("InvoiceNo")["TotalPrice"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    st.dataframe(invoice_sales, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This Table Shows the Top Sales as per the Invoice Number of the Customer.</p>", unsafe_allow_html=True)

    # 4. Price vs Quantity
    st.markdown("<h3 style='text-align: center;'>💰 Price vs Quantity</h3>", unsafe_allow_html=True)

    fig4 = px.scatter(
        filtered_df,
        x='UnitPrice',
        y='Quantity',
        title="Price vs Quantity",
        color='Country',
        template='plotly_dark'
    )

    fig4.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))
    fig4.update_layout(
        title="Price vs Quantity",
        xaxis_title="Unit Price",
        yaxis_title="Quantity"
    )
    st.plotly_chart(center_title(fig4), use_container_width=True)
    st.markdown("<p style='text-align: center;'>This chart shows total revenue contribution from each country, helping identify top-performing markets.</p>", unsafe_allow_html=True)

    # Average Order Value
    st.markdown("<h3 style='text-align: center;'>Average Order Value</h3>", unsafe_allow_html=True)
    avg_order_value = (
        df.groupby("CustomerID")["TotalPrice"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    st.dataframe(avg_order_value, use_container_width=True)

    # High Quantity Purchase 
    st.markdown("<h3 style='text-align: center;'>High Quantity Purchase</h3>", unsafe_allow_html=True)
    high_quantity_customers = (
        df.groupby("CustomerID")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.dataframe(high_quantity_customers, use_container_width=True)

    # 5. Quantity Distribution
    st.markdown("<h3 style='text-align: center;'>📦 Quantity Distribution</h3>", unsafe_allow_html=True)

    fig5 = px.histogram(
        filtered_df,
        x='Quantity',
        title="Quantity Distribution",
        nbins=50,
        template='plotly_dark'
    )

    fig5.update_traces(marker=dict(color='#FFA500', line=dict(color='white', width=1)))
    fig5.update_layout(
        title="Quantity Distribution",
        xaxis_title="Quantity",
        yaxis_title="Frequency"
    )
    st.plotly_chart(center_title(fig5), use_container_width=True)
    st.markdown("<p style='text-align: center;'>This chart shows total revenue contribution from each country, helping identify top-performing markets.</p>", unsafe_allow_html=True)

    # Top Quality Products
    st.markdown("<h3 style='text-align: center;'>Top Quality Products</h3>", unsafe_allow_html=True)
    top_quantity_products = (
        df.groupby("Description")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    st.dataframe(top_quantity_products, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This Table Shows the Top Quantity Products that has been purchased in high quantity</p>", unsafe_allow_html=True)


    # 6. Revenue by country
    st.markdown("<h3 style='text-align: center;'>Revenue by Country</h3>", unsafe_allow_html=True)
    filtered_df['Revenue'] = filtered_df['Quantity'] * filtered_df['UnitPrice']
    country_rev = filtered_df.groupby('Country')['Revenue'].sum().reset_index()

    fig6 = px.bar(
        country_rev,
        x='Country',
        y='Revenue',
        color='Revenue',
        title="Revenue by Country",
        color_continuous_scale='Blues',
        template='plotly_dark'
    )
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This chart shows total revenue contribution from each country, helping identify top-performing markets.</p>", unsafe_allow_html=True)

    # Country Sales
    st.markdown("<h3 style='text-align: center;'>Country Sales</h3>", unsafe_allow_html=True)
    country_sales = (
        df.groupby("Country")["TotalPrice"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.dataframe(country_sales, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This table shows the number of sales done by countries as per the total price.</p>", unsafe_allow_html=True)

    # Top Countries by Number of Orders
    st.markdown("<h3 style='text-align: center;'>Top Countries by Number of Orders</h3>", unsafe_allow_html=True)
    country_orders = (
        df.groupby("Country")["InvoiceNo"]
        .nunique()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(country_orders, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This table shows the Top countries with maximum number of Orders.</p>", unsafe_allow_html=True)

    # Revenue Contribution by top 5 country
    st.markdown("<h3 style='text-align: center;'>Revenue Generation of each country</h3>", unsafe_allow_html=True)
    top_countries = (
        df.groupby("Country")["TotalPrice"]
        .sum()
        .nlargest(5)
        .reset_index()
    )

    st.dataframe(top_countries, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This table shows the Revenue Generation of top 5 countries.</p>", unsafe_allow_html=True)

    # 7. Monthly Sales Trend
    st.markdown("<h3 style='text-align: center;'>Monthly Sales Trend</h3>", unsafe_allow_html=True)
    filtered_df['Month'] = filtered_df['InvoiceDate'].dt.to_period('M').astype(str)
    monthly_sales = filtered_df.groupby('Month')['Revenue'].sum().reset_index()

    fig7 = px.line(
        monthly_sales,
        x='Month',
        y='Revenue',
        markers=True,
        title="Monthly Revenue Trend",
        color_discrete_sequence=['#00FFFF'],
        template='plotly_dark'
    )

    fig7.update_traces(marker=dict(size=8, line=dict(width=1, color='white')))
    fig7.update_layout(
        title="Monthly Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Total Revenue"
    )
    st.plotly_chart(fig7, use_container_width=True)
    st.markdown("<p style='text-align: center;'>Displays how revenue changes over time on a monthly basis, useful for trend and seasonality analysis.</p>", unsafe_allow_html=True)

    # 8. Top Customers
    st.markdown("<h3 style='text-align: center;'>Top Customers</h3>", unsafe_allow_html=True)
    top_customers = filtered_df.groupby('CustomerID')['Revenue'].sum().nlargest(10).reset_index()

    fig8 = px.bar(
        top_customers,
        x='CustomerID',
        y='Revenue',
        color='Revenue',
        title="Top 10 Customers by Revenue",
        color_continuous_scale='Inferno',
        template='plotly_dark'
    )

    fig8.update_traces(marker=dict(line=dict(color='white', width=1)))
    fig8.update_layout(
        title="Top 10 Customers by Revenue",
        xaxis_title="Customer ID",
        yaxis_title="Total Revenue",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig8, use_container_width=True)
    st.markdown("<p style='text-align: center;'>Highlights the most valuable customers contributing the highest revenue.</p>", unsafe_allow_html=True)

    # Customer with Highest Purchase Frequency
    st.markdown("<h3 style='text-align: center;'>Customer with Highest Purchase Frequency</h3>", unsafe_allow_html=True)
    frequency = (
        df.groupby("CustomerID")["InvoiceNo"]
        .nunique()
        .sort_values(ascending=False)
    )

    st.dataframe(frequency, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This table shows the Customers with highest purchase frequency who purchased in high quantites.</p>", unsafe_allow_html=True)

    # Customers with Highest Monetary Value
    st.markdown("<h3 style='text-align: center;'>Customers with Highest Monetary Value</h3>", unsafe_allow_html=True)
    monetary = (
        df.groupby("CustomerID")["TotalPrice"]
        .sum()
        .sort_values(ascending=False)
    )

    st.dataframe(monetary, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This table shows the Customers with Highest Monetary Values.</p>", unsafe_allow_html=True)

    # Customers with highest average order value
    st.markdown("<h3 style='text-align: center;'>Customers with Highest Average order value</h3>", unsafe_allow_html=True)
    avg_order_value = (
        df.groupby("CustomerID")["TotalPrice"]
        .mean()
        .sort_values(ascending=False)
    )

    st.dataframe(avg_order_value, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This table shows the Customers with the highest average order values.</p>", unsafe_allow_html=True)

    # Customers Buying the Most products
    st.markdown("<h3 style='text-align: center;'>Customers purchased the most products</h3>", unsafe_allow_html=True)
    top_quantity_customers = (
        df.groupby("CustomerID")["Quantity"]
        .sum()
        .sort_values(ascending=False)
    )

    st.dataframe(top_quantity_customers, use_container_width=True)
    st.markdown("<p style='text-align: center;'>Highlights the most valuable customers contributing the highest revenue.</p>", unsafe_allow_html=True)

    # Customer with Longest Relationship
    st.markdown("<h3 style='text-align: center;'>Top Customers</h3>", unsafe_allow_html=True)
    customer_lifetime = (
        df.groupby("CustomerID")["InvoiceDate"]
        .agg(["min", "max"])
    )
    customer_lifetime["LifetimeDays"] = (
        customer_lifetime["max"] - customer_lifetime["min"]
    ).dt.days

    st.dataframe(customer_lifetime.sort_values("LifetimeDays", ascending=False).head(), use_container_width=True)

    monthly_frequency = (
        df.groupby(["CustomerID", df["InvoiceDate"].dt.to_period("M")])["InvoiceNo"]
        .nunique()
    )

    mf = monthly_frequency.sort_values(ascending=False).head()
    st.dataframe(mf, use_container_width=True)
    st.markdown("<p style='text-align: center;'>Highlights the most valuable customers contributing the highest revenue.</p>", unsafe_allow_html=True)

    # 9. Order Distribution by Country
    st.markdown("<h3 style='text-align: center;'>Order Distribution by Country</h3>", unsafe_allow_html=True)
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    country_sales = df.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False).head(5)

    fig9 = px.pie(
        values=country_sales.values,
        names=country_sales.index,
        title="Most Sales Distribution by Country",
        color_discrete_sequence=px.colors.sequential.Agsunset
    )

    fig9.update_traces(
        textinfo="percent+label",
        pull=[0.05]*len(country_sales),
        marker_line_width=1, marker_line_color='white'
    )

    fig9.update_layout(
        template="plotly_dark",
        height=550,
        width=1100
    )
    st.plotly_chart(fig9, use_container_width=True)
    st.markdown("<p style='text-align: center;'>Represents the proportion of total orders placed from each country.</p>", unsafe_allow_html=True)

    # Average Spending by country
    st.markdown("<h3 style='text-align: center;'>Average Spending by country</h3>", unsafe_allow_html=True)
    avg_country_spending = (
        df.groupby("Country")["TotalPrice"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(avg_country_spending, use_container_width=True)
    st.markdown("<p style='text-align: center;'>This table shows the average spending of countries on a particular product.</p>", unsafe_allow_html=True)

    # 10. Unit Price Distribution
    st.markdown("<h3 style='text-align: center;'>Unit Price Distribution</h3>", unsafe_allow_html=True)
    fig10 = px.box(
        filtered_df,
        y='UnitPrice',
        title="Unit Price Distribution",
        color_discrete_sequence=['#FFA500'],
        template='plotly_dark'
    )

    fig10.update_traces(marker=dict(line=dict(color='white', width=1)))
    fig10.update_layout(
        title="Unit Price Distribution",
        yaxis_title="Unit Price"
    )
    st.plotly_chart(fig10, use_container_width=True)
    st.markdown("<p style='text-align: center;'>Shows the spread and outliers in product pricing, helping detect anomalies or pricing strategy.</p>", unsafe_allow_html=True)

    # ------------------ DATA PREVIEW ------------------
    st.markdown("<h3 style='text-align: center;'>📄 Dataset Preview</h3>", unsafe_allow_html=True)
    st.dataframe(filtered_df.head(10), use_container_width=True)

    # ------------------ FOOTER ------------------
    st.markdown("""
                <div class="footer">
                Developed by 
                <span class="highlight">Vaibhav</span>
                • Powered by Streamlit
                </div>
            """, unsafe_allow_html=True)