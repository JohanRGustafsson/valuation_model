import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Any
from utils.calculations import (
    calculate_phase_value,
    PhaseInputs,
)
from utils.state import get_phase_display_name


def display_header():
    """Display the app header with toggles."""
    st.title("Pharma Asset Valuation 💊 ")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Net Present Value (NPV) Calculator")


def toggle_state(state_key):
    """Toggle a boolean state variable."""
    st.session_state[state_key] = not st.session_state[state_key]


def create_metric(label: str, value: Any, help_text: str = None, delta: Any = None):
    """Create a standardized metric display.

    Args:
        label: The metric label
        value: The metric value
        help_text: Optional help text
        delta: Optional delta value
    """
    return st.metric(
        label=label,
        value=value,
        help=help_text,
        delta=delta,
    )


def display_npv_results(inputs):
    """Display NPV results for all phases using native Streamlit components."""
    st.subheader("The Final NPV by Development Stage")

    # Convert dictionary to PhaseInputs dataclass
    phase_inputs = PhaseInputs(
        launchValue=inputs["launchValue"],
        orderOfEntry=inputs["orderOfEntry"],
        discountRate=inputs["discountRate"],
        timeToMarket=inputs["timeToMarket"],
        costs=inputs["costs"],
        probabilities=inputs["probabilities"],
        includeRDCosts=inputs["includeRDCosts"],
        dealStage=inputs["dealStage"],
        dealValue=inputs["dealValue"],
        desiredShare=inputs["desiredShare"],
    )

    # Prepare data for all phases
    phases = ["preclinical", "phase1", "phase2", "phase3", "registration"]
    results_data = []

    for phase in phases:
        phase_result = calculate_phase_value(phase_inputs, phase)
        time_to_market = inputs["timeToMarket"][phase]
        discount_rate = inputs["discountRate"]
        display_name = get_phase_display_name(phase)

        results_data.append(
            {
                "Phase": display_name,
                "NPV": phase_result.value,  # Get value from PhaseValueResult
                "Time": time_to_market,
                "Probability": phase_result.probability,
                "Costs": phase_result.costs,
            }
        )

    # Use columns to display each phase
    cols = st.columns(len(phases))
    for i, (col, data) in enumerate(zip(cols, results_data)):
        with col:
            create_metric(
                label=data["Phase"],
                value=f"${data['NPV']:.1f}M",
            )
            st.caption(f"Time to market: {data['Time']} years")

            # Always show an expander with details
            with st.expander("Details", expanded=False):
                st.markdown(f"**NPV:** ${data['NPV']:.1f}M")
                st.markdown(f"**Probability:** {data['Probability']:.1f}%")
                st.markdown(f"**Time:** {data['Time']:.1f} years")
                if inputs["includeRDCosts"]:
                    st.markdown(f"**Costs:** ${data['Costs']:.1f}M")


def create_card(title: str, content_function, *args, **kwargs):
    """Create a card-like container with consistent styling.

    Args:
        title: Card title
        content_function: Function to call to fill card content
        *args, **kwargs: Arguments to pass to content function
    """
    with st.container():
        st.markdown(f"#### {title}")
        with st.container():
            st.markdown(
                """
                <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; 
                     background-color: #f8f9fa;">
                </div>
                """,
                unsafe_allow_html=True,
            )
            content_function(*args, **kwargs)


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
            f"**Recommendation: {recommendation}**\n\n{recommendation} is expected to generate **${abs(value_diff):.1f}M more value**"
        )


def display_formula_expander(title, formula, explanation, use_container=False):
    """Display a formula with explanation in an expander or container.

    Args:
        title: Title of the formula section
        formula: The formula text to display
        explanation: Explanation text for the formula
        use_container: If True, uses a container instead of an expander (for nested contexts)
    """
    if use_container:
        with st.container():
            st.markdown(f"**{title}**")
            st.code(formula)
            st.write(explanation)
            st.markdown("---")
    else:
        with st.expander(title, expanded=False):
            st.code(formula)
            st.write(explanation)


def create_formula_expander(title, formula, explanation, expanded=False):
    """Create a consistently styled formula expander.

    Args:
        title: The formula section title
        formula: The formula text/code to display
        explanation: Text explanation of the formula
        expanded: Whether the expander should be expanded by default
    """
    with st.expander(f"📐 Formula: {title}", expanded=expanded):
        st.code(formula)
        st.markdown(explanation)


def create_assumption_expander(title, assumptions, expanded=False):
    """Create a consistently styled assumptions expander.

    Args:
        title: The assumptions section title
        assumptions: The assumptions text to display
        expanded: Whether the expander should be expanded by default
    """
    with st.expander(f"🎯 Assumptions: {title}", expanded=expanded):
        st.markdown(assumptions)


def create_formula_and_assumptions_expander(
    title, formula, formula_explanation, assumptions, expanded=False
):
    """Create an expander that displays both formulas and related assumptions.

    Args:
        title: The section title
        formula: The formula text/code to display
        formula_explanation: Text explanation of the formula
        assumptions: The assumptions text to display
        expanded: Whether the expander should be expanded by default
    """
    with st.expander(f"📐 {title}", expanded=expanded):
        st.subheader("Formula")
        st.code(body=formula, language=None)
        st.markdown(formula_explanation)

        st.markdown("---")

        st.subheader("Assumptions")
        st.markdown(assumptions)


def create_multi_metric_row(metrics: List[Tuple[str, Any, str, Any]]):
    """Create a row of metrics with consistent styling.

    Args:
        metrics: List of tuples containing (label, value, help_text, delta)
    """
    cols = st.columns(len(metrics))
    for i, (label, value, help_text, delta) in enumerate(metrics):
        with cols[i]:
            create_metric(label, value, help_text, delta)
