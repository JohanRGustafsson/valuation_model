import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Pharmaceutical Valuation Model", page_icon="💊", layout="wide"
)

# Title and description
st.title("💊 Pharmaceutical Valuation Model")
st.markdown(
    """
This application helps evaluate the financial viability of pharmaceutical projects using key metrics like NPV, IRR, and Payback Period.
"""
)

# Sidebar for assumptions
st.sidebar.header("Model Assumptions")

# Input parameters
clinical_probability = st.sidebar.slider("Clinical Probability (%)", 0, 100, 70) / 100
time_to_market = st.sidebar.number_input("Time to Market (years)", 1, 10, 3)
peak_annual_sales = st.sidebar.number_input("Peak Annual Sales ($M)", 100, 1000, 500)
discount_rate = st.sidebar.slider("Discount Rate (%)", 0, 20, 10) / 100

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(
    ["Dashboard", "Revenue Forecast", "Cost Structure", "Sensitivity Analysis"]
)

# Dashboard Tab
with tab1:
    st.header("Key Metrics")

    # Calculate basic metrics (simplified for demonstration)
    years = list(range(2025, 2030))
    revenue = [
        peak_annual_sales * (1 + 0.2) ** (year - (2025 + time_to_market))
        for year in years
    ]
    r_and_d_costs = [100, 50, 30, 20, 10]
    marketing_costs = [20, 30, 40, 50, 60]

    # Calculate cash flows
    cash_flows = [
        rev - rd - mk for rev, rd, mk in zip(revenue, r_and_d_costs, marketing_costs)
    ]

    # Calculate NPV
    npv = sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows))

    # Calculate IRR (simplified)
    irr = (npv / sum(cash_flows)) * 100

    # Calculate Payback Period (simplified)
    cumulative_cf = np.cumsum(cash_flows)
    payback_period = np.where(cumulative_cf >= 0)[0][0] + 1

    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("NPV ($M)", f"{npv:.2f}")
    with col2:
        st.metric("IRR (%)", f"{irr:.2f}")
    with col3:
        st.metric("Payback Period (years)", f"{payback_period}")

# Revenue Forecast Tab
with tab2:
    st.header("Revenue Forecast")

    # Create revenue forecast chart
    fig_revenue = go.Figure()
    fig_revenue.add_trace(
        go.Scatter(x=years, y=revenue, mode="lines+markers", name="Projected Revenue")
    )
    fig_revenue.update_layout(
        title="Revenue Forecast Over Time",
        xaxis_title="Year",
        yaxis_title="Revenue ($M)",
        showlegend=True,
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# Cost Structure Tab
with tab3:
    st.header("Cost Structure")

    # Create cost breakdown chart
    fig_costs = go.Figure()
    fig_costs.add_trace(go.Bar(x=years, y=r_and_d_costs, name="R&D Costs"))
    fig_costs.add_trace(go.Bar(x=years, y=marketing_costs, name="Marketing Costs"))
    fig_costs.update_layout(
        title="Cost Breakdown Over Time",
        xaxis_title="Year",
        yaxis_title="Costs ($M)",
        barmode="stack",
    )
    st.plotly_chart(fig_costs, use_container_width=True)

# Sensitivity Analysis Tab
with tab4:
    st.header("Sensitivity Analysis")

    # Create sensitivity analysis parameters
    sensitivity_params = {
        "Discount Rate": [discount_rate * 0.8, discount_rate, discount_rate * 1.2],
        "Clinical Probability": [
            clinical_probability * 0.8,
            clinical_probability,
            clinical_probability * 1.2,
        ],
        "Peak Sales": [
            peak_annual_sales * 0.8,
            peak_annual_sales,
            peak_annual_sales * 1.2,
        ],
    }

    # Create sensitivity analysis chart
    fig_sensitivity = go.Figure()
    for param, values in sensitivity_params.items():
        fig_sensitivity.add_trace(
            go.Scatter(
                x=["Low", "Base", "High"], y=values, mode="lines+markers", name=param
            )
        )
    fig_sensitivity.update_layout(
        title="Sensitivity Analysis of Key Parameters",
        xaxis_title="Scenario",
        yaxis_title="Value",
        showlegend=True,
    )
    st.plotly_chart(fig_sensitivity, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center'>
    <p>Built with Streamlit | Pharmaceutical Valuation Model</p>
</div>
""",
    unsafe_allow_html=True,
)
