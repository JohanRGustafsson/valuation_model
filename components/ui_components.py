import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.calculations import (
    calculate_phase_value,
    get_cumulative_probability,
    get_order_multiplier,
)
from utils.state import get_phase_display_name


def display_header():
    """Display the app header with toggles."""
    st.title("💊 Pharma Asset Valuation")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Net Present Value (NPV) Calculator")
    with col2:
        toggle_col1, toggle_col2 = st.columns(2)
        with toggle_col1:
            st.button(
                "📋 "
                + (
                    "Hide Assumptions"
                    if st.session_state.show_assumptions
                    else "Show Assumptions"
                ),
                on_click=lambda: toggle_state("show_assumptions"),
            )
        with toggle_col2:
            st.button(
                "📊 "
                + (
                    "Hide Formulas"
                    if st.session_state.show_formulas
                    else "Show Formulas"
                ),
                on_click=lambda: toggle_state("show_formulas"),
            )


def toggle_state(state_key):
    """Toggle a boolean state variable."""
    st.session_state[state_key] = not st.session_state[state_key]


def display_phase_card(phase, phase_value, time_to_market, discount_rate):
    """Display a phase card using native Streamlit components."""
    display_name = get_phase_display_name(phase)

    # Use a container with border styling
    with st.container():
        st.markdown(
            f"""
        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f8f9fa;">
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Use native Streamlit components within
        st.metric(
            label=display_name,
            value=f"${phase_value:.1f}M",
            help=f"Time to market: {time_to_market} years | NPV at {discount_rate}% discount rate",
        )


def display_npv_results(inputs):
    """Display NPV results for all phases using native Streamlit components."""
    st.subheader("The Final NPV by Development Stage")

    # Prepare data for all phases
    phases = ["preclinical", "phase1", "phase2", "phase3", "registration"]
    results_data = []

    for phase in phases:
        phase_value = calculate_phase_value(inputs, phase)
        time_to_market = inputs["timeToMarket"][phase]
        discount_rate = inputs["discountRate"]
        display_name = get_phase_display_name(phase)

        results_data.append(
            {
                "Phase": display_name,
                "NPV ($M)": phase_value,
                "Time to Market (years)": time_to_market,
            }
        )

    # Create a DataFrame
    results_df = pd.DataFrame(results_data)

    # Use columns to display each phase
    cols = st.columns(len(phases))
    for i, (col, data) in enumerate(zip(cols, results_data)):
        with col:
            st.metric(
                label=data["Phase"],
                value=f"${data['NPV ($M)']:.1f}M",
            )
            st.caption(f"Time to market: {data['Time to Market (years)']} years")

            if st.session_state.show_formulas:
                phase = phases[i]
                base_value = inputs["launchValue"] * get_order_multiplier(
                    inputs, inputs["orderOfEntry"]
                )
                probability = get_cumulative_probability(inputs, phase)
                discount_factor = (1 + (inputs["discountRate"] / 100)) ** inputs[
                    "timeToMarket"
                ][phase]

                st.write("---")
                st.write("**Details:**")
                st.write(f"Base: ${base_value:.1f}M")
                st.write(f"Prob: {(probability * 100):.1f}%")
                st.write(f"Time: {(1/discount_factor):.3f}")

                if inputs["includeRDCosts"]:
                    cumulative_costs = 0
                    for j in range(i + 1):
                        cumulative_costs += inputs["costs"][phases[j]]
                    st.write(f"Costs: ${cumulative_costs:.1f}M")


def create_pie_chart(data):
    """Create a pie chart for ownership structure."""
    fig = go.Figure(
        data=[
            go.Pie(
                labels=data["Entity"],
                values=data["Percentage"],
                hole=0.4,
                textinfo="label+percent",
                marker_colors=["#0088FE", "#00C49F"],
            )
        ]
    )

    fig.update_layout(
        height=400,
        margin=dict(t=0, b=0, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
    )

    return fig


def create_comparison_bar_chart(data):
    """Create a comparison bar chart for decision options."""
    fig = go.Figure(
        data=[
            go.Bar(
                x=data["Option"],
                y=data["Expected Value ($M)"],
                marker_color=["#17a2b8", "#28a745"],
                text=[f"${v:.1f}M" for v in data["Expected Value ($M)"]],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Expected Value Comparison",
        height=400,
        yaxis_title="Expected Value ($M)",
        xaxis_title=None,
    )

    return fig


def display_recommendation(recommendation, value_diff):
    """Display recommendation with native Streamlit components."""
    if recommendation == "Continue Development":
        st.success(
            f"**Recommendation: {recommendation}**\n\n{recommendation} is expected to generate **${value_diff:.1f}M more value**"
        )
    else:
        st.info(
            f"**Recommendation: {recommendation}**\n\n{recommendation} is expected to generate **${value_diff:.1f}M more value**"
        )


def display_formula_expander(title, formula, explanation):
    """Display a formula with explanation in an expander."""
    with st.expander(title, expanded=False):
        st.code(formula)
        st.write(explanation)
