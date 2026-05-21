import streamlit as st
import numpy as np
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

def show_model():
    # ----------------------------
    # Load Model & Scaler
    # ----------------------------
    model = joblib.load("models/customer_segmentation_model.pkl")
    scaler = joblib.load("models/scaler.pkl")

    st.markdown("""
        <style>
            .main {
                background-color: #0E1117;
            }
            .stMetric {
                background-color: #1c1f26;
                padding: 5px;
                border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>🧑🏻Customer Sales Prediction📈</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Enter customer details to predict segment</h3>", unsafe_allow_html=True)

    # ----------------------------
    # Input Fields
    # ----------------------------
    recency = st.number_input("Recency (days since last purchase)", min_value=0)
    frequency = st.number_input("Frequency (number of transactions)", min_value=0)
    monetary = st.number_input("Monetary (total spending)", min_value=0.0)

    avg_order_value = st.number_input("Average Order Value", min_value=0.0)
    purchase_frequency = st.number_input("Purchase Frequency", min_value=0.0)
    total_quantity = st.number_input("Total Quantity Purchased", min_value=0)
    customer_lifetime = st.number_input("Customer Lifetime (days)", min_value=0)

    # ----------------------------
    # Prediction Button
    # ----------------------------
    if st.button("Predict Segment"):

        # Create feature array
        features = np.array([[
            recency,
            frequency,
            monetary,
            avg_order_value,
            purchase_frequency,
            total_quantity,
            customer_lifetime
        ]])

        # Scale features
        features_scaled = scaler.transform(features)

        # Predict cluster
        cluster = model.predict(features_scaled)[0]

        # ----------------------------
        # Map Cluster to Segment
        # (based on your earlier analysis)
        # ----------------------------
        cluster_labels = {
            0: "🛒 Regular Customer",
            1: "⭐ VIP Customer",
            2: "⚠️ At-Risk Customer",
            3: "💰 Low-Value Customer"
        }

        segment = cluster_labels.get(cluster, "Unknown")

        # ----------------------------
        # Output
        # ----------------------------
        st.success(f"Predicted Cluster: {cluster}")
        st.success(f"Customer Segment: {segment}")

        # ----------------------------
        # Visualization Section
        # ----------------------------
        st.markdown(
        "<h2 style='text-align: center;'>📊 Cluster Visualization (PCA)</h2>",
        unsafe_allow_html=True
        )

        # Load dataset (same used during training)
        df = pd.read_csv("data/Customers.csv")

        # Feature engineering (same as training)
        df['LastPurchase'] = pd.to_datetime(df['LastPurchase'])
        snapshot_date = df['LastPurchase'].max() + pd.Timedelta(days=1)
        df['Recency'] = (snapshot_date - df['LastPurchase']).dt.days
        df['Frequency'] = df['TotalTransactions']
        df['Monetary'] = df['TotalSpending']

        features = [
            'Recency','Frequency','Monetary',
            'AvgOrderValue','PurchaseFrequency',
            'TotalQuantity','CustomerLifetime'
        ]

        X = df[features]
        X_scaled = scaler.transform(X)

        # Predict clusters for visualization
        df['Cluster'] = model.predict(X_scaled)

        # PCA for 2D visualization
        pca = PCA(n_components=4)
        X_pca = pca.fit_transform(X_scaled)

        df['PCA1'] = X_pca[:, 0]
        df['PCA2'] = X_pca[:, 1]

        # Plot
        fig, ax = plt.subplots(figsize=(12, 4), dpi=180)

        scatter = ax.scatter(
            df['PCA1'],
            df['PCA2'],
            c=df['Cluster'],
            edgecolors='k',
            s=50
        )

        ax.set_title("Customer Segments (PCA View)")
        ax.set_xlabel("PCA 1")
        ax.set_ylabel("PCA 2")

        st.pyplot(fig)

        # ----------------------------
        # Business Insight
        # ----------------------------
        if cluster == 1:
            st.info("💎 High-value customer → Offer loyalty rewards & premium services.")
        elif cluster == 2:
            st.warning("⚠️ Customer is at risk → Provide discounts or re-engagement offers.")
        elif cluster == 0:
            st.info("🛍️ Regular customer → Encourage more purchases with offers.")
        else:
            st.info("💰 Low-value customer → Focus on awareness & engagement strategies.")

         # ------------------ FOOTER ------------------
        st.markdown("""
                <div class="footer">
                Developed by 
                <span class="highlight">Vaibhav</span>
                • Powered by Streamlit
                </div>
            """, unsafe_allow_html=True)