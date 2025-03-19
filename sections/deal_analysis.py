import streamlit as st
import pandas as pd
from utils.calculations import (
    calculate_phase_value,
    calculate_deal_percentages,
    calculate_required_deal_value,
)
from utils.state import get_stage_options
from components.ui_components import create_pie_chart


def deal_analysis_page():
    """Display the deal analysis page."""
    st.header("Deal Analysis")

    # Deal Parameters
    st.subheader("Deal Parameters")
    deal_col1, deal_col2, deal_col3 = st.columns(3)

    with deal_col1:
        stage_options = get_stage_options()
        selected_stage = st.selectbox(
            "Deal Stage",
            options=list(stage_options.keys()),
            format_func=lambda x: stage_options[x],
            index=list(stage_options.keys()).index(
                st.session_state.inputs["dealStage"]
            ),
        )
        # Update the deal stage and recalculate percentages if needed
        if selected_stage != st.session_state.inputs["dealStage"]:
            st.session_state.inputs["dealStage"] = selected_stage
            percentages = calculate_deal_percentages(st.session_state.inputs)
            st.session_state.inputs["desiredShare"] = round(
                percentages["partnerShare"], 1
            )

    with deal_col2:
        new_deal_value = st.number_input(
            "Deal Value ($M)",
            min_value=0.0,
            value=float(st.session_state.inputs["dealValue"]),
            step=0.1,
        )
        # Update deal value and recalculate percentages if needed
        if new_deal_value != st.session_state.inputs["dealValue"]:
            st.session_state.inputs["dealValue"] = new_deal_value
            percentages = calculate_deal_percentages(st.session_state.inputs)
            st.session_state.inputs["desiredShare"] = round(
                percentages["partnerShare"], 1
            )

    with deal_col3:
        new_share = st.number_input(
            "Partner's Share (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.inputs["desiredShare"]),
            step=1.0,
        )
        # Update share percentage and recalculate deal value if needed
        if new_share != st.session_state.inputs["desiredShare"]:
            st.session_state.inputs["desiredShare"] = new_share
            required_deal_value = calculate_required_deal_value(
                st.session_state.inputs, new_share
            )
            st.session_state.inputs["dealValue"] = round(required_deal_value, 1)

    # Deal Value Analysis
    st.subheader("Deal Value Analysis")

    percentages = calculate_deal_percentages(st.session_state.inputs)
    phase_value = calculate_phase_value(
        st.session_state.inputs, st.session_state.inputs["dealStage"]
    )

    # Display information in a structured way with cards
    col1, col2 = st.columns(2)

    with col1:
        # Use a container with styled elements
        with st.container():
            st.markdown("#### Asset and Deal Overview")
            metrics_col1, metrics_col2 = st.columns(2)

            with metrics_col1:
                st.metric(
                    label="Asset Value at Selected Stage", value=f"${phase_value:.1f}M"
                )
                st.metric(
                    label="Value per 1% Ownership",
                    value=f"${percentages['valuePerShare']:.2f}M",
                )

            with metrics_col2:
                st.metric(
                    label="Current Deal Value",
                    value=f"${st.session_state.inputs['dealValue']}M",
                )
                st.metric(
                    label="Resulting Ownership Percentage",
                    value=f"{percentages['partnerShare']:.1f}%",
                )

            if st.session_state.show_formulas:
                st.markdown("---")
                st.markdown("**Ownership Calculation:**")
                st.code(
                    f"Ownership % = Deal Value ÷ Asset Value = ${st.session_state.inputs['dealValue']}M ÷ ${phase_value:.1f}M = {percentages['partnerShare']:.1f}%"
                )

    with col2:
        # Use a container with styled elements for ownership details
        with st.container():
            st.markdown("#### Ownership Distribution")

            partner_value = phase_value * percentages["partnerShare"] / 100
            company_value = phase_value * percentages["companyShare"] / 100

            metrics_col1, metrics_col2 = st.columns(2)

            with metrics_col1:
                st.metric(
                    label="Partner Share",
                    value=f"{percentages['partnerShare']:.1f}%",
                    delta=f"${partner_value:.1f}M",
                )

            with metrics_col2:
                st.metric(
                    label="Company Share",
                    value=f"{percentages['companyShare']:.1f}%",
                    delta=f"${company_value:.1f}M",
                )

            # Deal assessment
            deal_assessment = (
                "⚠️ Undervalued"
                if st.session_state.inputs["dealValue"] < phase_value * 0.1
                else (
                    "⚠️ Overvalued"
                    if st.session_state.inputs["dealValue"] > phase_value * 0.9
                    else "✓ Fair value"
                )
            )

            # Use appropriate status function based on assessment
            if "Undervalued" in deal_assessment:
                st.warning(f"**Deal Assessment:** {deal_assessment}")
            elif "Overvalued" in deal_assessment:
                st.warning(f"**Deal Assessment:** {deal_assessment}")
            else:
                st.success(f"**Deal Assessment:** {deal_assessment}")

    # Pie Chart for Ownership Structure
    st.subheader("Ownership Structure")

    # Prepare data for pie chart
    pie_data = pd.DataFrame(
        {
            "Entity": ["Partner Share", "Company Share"],
            "Percentage": [percentages["partnerShare"], percentages["companyShare"]],
        }
    )

    # Create and display the pie chart
    fig = create_pie_chart(pie_data)
    st.plotly_chart(fig, use_container_width=True)
