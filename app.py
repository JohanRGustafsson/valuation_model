import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import io


# Cache the Excel file creation to prevent unnecessary recomputation
@st.cache_data
def create_excel_file(
    clinical_probability,
    time_to_market,
    peak_annual_sales,
    discount_rate,
    npv,
    irr,
    payback_period,
    years,
    revenue,
    r_and_d_costs,
    marketing_costs,
    cash_flows,
):
    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()

    # Create a Pandas Excel writer using the XlsxWriter engine
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # 1. Dashboard: Key metrics summary
        dashboard_data = {
            "Metric": ["NPV", "IRR", "Payback Period"],
            "Value": [npv, irr, payback_period],
        }
        dashboard_df = pd.DataFrame(dashboard_data)
        dashboard_df.to_excel(writer, sheet_name="Dashboard", index=False)

        # 2. Assumptions: Input values for the model
        assumptions_data = {
            "Assumption": [
                "Clinical Probability",
                "Time to Market (years)",
                "Peak Annual Sales ($M)",
                "Discount Rate (%)",
            ],
            "Value": [
                clinical_probability * 100,
                time_to_market,
                peak_annual_sales,
                discount_rate * 100,
            ],
        }
        assumptions_df = pd.DataFrame(assumptions_data)
        assumptions_df.to_excel(writer, sheet_name="Assumptions", index=False)

        # 3. Revenue Forecast
        revenue_data = {"Year": years, "Projected Revenue ($M)": revenue}
        revenue_df = pd.DataFrame(revenue_data)
        revenue_df.to_excel(writer, sheet_name="Revenue", index=False)

        # 4. Cost Structure
        costs_data = {
            "Year": years,
            "R&D Costs ($M)": r_and_d_costs,
            "Marketing Costs ($M)": marketing_costs,
        }
        costs_df = pd.DataFrame(costs_data)
        costs_df.to_excel(writer, sheet_name="Costs", index=False)

        # 5. DCF Calculation
        dcf_data = {
            "Year": years,
            "Cash Flow ($M)": cash_flows,
            "Discount Factor": [
                1 / (1 + discount_rate) ** i for i in range(len(years))
            ],
            "Discounted Cash Flow": [
                cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows)
            ],
        }
        dcf_df = pd.DataFrame(dcf_data)
        dcf_df.to_excel(writer, sheet_name="DCF", index=False)

        # 6. Sensitivity Analysis
        sensitivity_data = {
            "Parameter": ["Discount Rate", "Clinical Probability", "Peak Sales"],
            "Base Value": [
                discount_rate * 100,
                clinical_probability * 100,
                peak_annual_sales,
            ],
            "Low": [
                discount_rate * 0.8 * 100,
                clinical_probability * 0.8 * 100,
                peak_annual_sales * 0.8,
            ],
            "High": [
                discount_rate * 1.2 * 100,
                clinical_probability * 1.2 * 100,
                peak_annual_sales * 1.2,
            ],
        }
        sensitivity_df = pd.DataFrame(sensitivity_data)
        sensitivity_df.to_excel(writer, sheet_name="Sensitivity Analysis", index=False)

        # 7. Notes & Documentation
        notes_data = {
            "Section": ["Assumptions", "Revenue", "Costs", "DCF", "Sensitivity"],
            "Instructions": [
                "Enter key input assumptions. Use a consistent color for inputs (e.g., light blue).",
                "Link revenue forecast to assumptions. Update formulas as necessary.",
                "Detail fixed and variable costs; include R&D and marketing costs separately.",
                "Apply discount factors to cash flows to calculate DCF. Adjust formulas if needed.",
                "Test sensitivity of key metrics (NPV, IRR) by varying assumptions.",
            ],
        }
        notes_df = pd.DataFrame(notes_data)
        notes_df.to_excel(writer, sheet_name="Notes", index=False)

    output.seek(0)
    return output


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

# Calculate basic metrics (simplified for demonstration)
years = list(range(2025, 2030))
revenue = [
    peak_annual_sales * (1 + 0.2) ** (year - (2025 + time_to_market)) for year in years
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

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(
    ["Dashboard", "Revenue Forecast", "Cost Structure", "Sensitivity Analysis"]
)

# Dashboard Tab
with tab1:
    st.header("Key Metrics")

    # Add download button at the top of the dashboard with improved features
    excel_file = create_excel_file(
        clinical_probability,
        time_to_market,
        peak_annual_sales,
        discount_rate,
        npv,
        irr,
        payback_period,
        years,
        revenue,
        r_and_d_costs,
        marketing_costs,
        cash_flows,
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        st.download_button(
            label="📥 Download Excel Model",
            data=excel_file,
            file_name="Pharma_Valuation_Model.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the current model state as an Excel file",
            type="primary",
            use_container_width=True,
        )
    with col2:
        st.markdown(
            """
        <div style='text-align: center; padding-top: 10px;'>
            <small>Last updated: {}</small>
        </div>
        """.format(
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ),
            unsafe_allow_html=True,
        )

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
