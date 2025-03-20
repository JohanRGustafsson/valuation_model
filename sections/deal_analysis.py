import streamlit as st
import pandas as pd
from dataclasses import dataclass
from utils.calculations import (
    calculate_phase_value,
    calculate_deal_percentages,
    calculate_required_deal_value,
    PhaseValueResult,
    DealPercentagesResult,
)
from utils.state import get_stage_options
from components.ui_components import (
    create_pie_chart,
    create_metric,
    create_card,
    create_multi_metric_row,
    create_formula_expander,
    create_assumption_expander,
    create_formula_and_assumptions_expander,
)


@dataclass
class DealInputs:
    """Input parameters for deal analysis.

    Attributes:
        dealStage: Current development stage
        dealValue: Deal value in millions
        desiredShare: Desired partner's ownership percentage
    """

    dealStage: str
    dealValue: float
    desiredShare: float


def deal_analysis_page() -> None:
    """Display the deal analysis page for evaluating partnership terms.

    This function creates the complete deal analysis interface including:
    - Deal parameter inputs (stage, value, ownership split)
    - Deal value analysis with metrics and comparisons
    - Ownership structure visualization
    - Assessment of deal fairness

    The function handles real-time updates of calculations and visualizations
    as users modify deal parameters.
    """
    st.header("Deal Analysis")

    # Deal formula and assumptions at the top level for overall understanding (full width)
    create_formula_and_assumptions_expander(
        "Ownership and Value Relationship",
        """Ownership % = Deal Value ($M) ÷ Asset Value ($M)
Value per 1% = Asset Value ($M) ÷ 100
Required Deal Value = Asset Value ($M) × Desired Ownership %""",
        "The percentage of the asset that a partner receives is calculated by dividing the deal value by the total asset value at the current development stage. This fundamental relationship drives all deal parameters.",
        """
        - Both parties place the same valuation on the asset
        - Deal value is paid upfront with no milestone payments
        - No adjustment for payment terms or time value of money
        - Distribution of future profits is proportional to ownership
        - No premium for strategic value or synergies
        - No discount for development risk beyond NPV adjustment
        """,
        expanded=False,
    )

    # Deal Parameters
    st.subheader("Deal Parameters")
    deal_parameters = display_deal_parameters()

    # Deal Value Analysis
    st.subheader("Deal Value Analysis")
    display_deal_analysis(deal_parameters)


def display_deal_parameters() -> DealInputs:
    """Display and handle deal parameter inputs.

    Creates input controls for:
    - Deal stage selection
    - Deal value entry
    - Partner's share percentage

    Returns:
        DealInputs: Dictionary containing the current deal parameters:
            - dealStage: Selected development stage
            - dealValue: Deal value in millions
            - desiredShare: Partner's ownership percentage
    """
    # Deal parameters formula and assumptions
    create_formula_and_assumptions_expander(
        "Deal Parameters Calculation",
        """Required Deal Value = Asset Value × Desired Ownership %
Resulting Ownership % = Deal Value ÷ Asset Value""",
        "These formulas allow you to calculate either the required deal value for a desired ownership percentage or the resulting ownership percentage for a given deal value.",
        """
        - Changes to the deal stage will recalculate the underlying asset value
        - Changes to deal value will recalculate the resulting ownership percentage
        - Changes to ownership percentage will recalculate the required deal value
        - All calculations use the NPV at the selected development stage
        - The calculations assume a proportional relationship between value and ownership
        """,
        expanded=False,
    )

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
            st.session_state.inputs["desiredShare"] = round(percentages.partnerShare, 1)

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
            st.session_state.inputs["desiredShare"] = round(percentages.partnerShare, 1)

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

    return DealInputs(
        dealStage=selected_stage, dealValue=new_deal_value, desiredShare=new_share
    )


def display_deal_analysis(deal_params: DealInputs) -> None:
    """Display the deal value analysis section with metrics and visualizations.

    Args:
        deal_params (DealInputs): Current deal parameters including stage,
            value, and ownership split

    This function:
    1. Calculates and displays key deal metrics
    2. Shows ownership distribution
    3. Provides deal assessment
    4. Creates ownership structure visualization
    """
    percentages = calculate_deal_percentages(st.session_state.inputs)
    phase_result = calculate_phase_value(
        st.session_state.inputs, st.session_state.inputs["dealStage"]
    )

    # Deal assessment criteria (full width)
    create_formula_and_assumptions_expander(
        "Deal Fairness Assessment",
        """Undervalued: Deal Value < 10% of Asset Value
Fair Value: 10% ≤ Deal Value ≤ 90% of Asset Value
Overvalued: Deal Value > 90% of Asset Value""",
        "The fairness assessment compares the deal value to the asset value to determine if the deal represents fair value for both parties.",
        """
        - A deal is considered 'undervalued' if it values the asset at less than 10% of its calculated NPV
        - A deal is 'overvalued' if it values the asset at more than 90% of its calculated NPV 
        - These thresholds are industry benchmarks but may vary by:
          - Therapeutic area and indication
          - Company strategic priorities
          - Market conditions and competition
          - Asset uniqueness and differentiation
        - Fairness assessment does not account for non-financial strategic factors
        """,
        expanded=False,
    )

    # Display information in a structured way with cards
    col1, col2 = st.columns(2)

    with col1:
        display_asset_overview(phase_result, percentages)

    with col2:
        display_ownership_details(phase_result, percentages)

    # Pie Chart for Ownership Structure
    st.subheader("Ownership Structure")

    # Ownership structure explanation (full width)
    create_formula_and_assumptions_expander(
        "Ownership Structure Details",
        f"""Partner Share: {percentages.partnerShare:.1f}% for ${st.session_state.inputs['dealValue']}M
Company Share: {percentages.companyShare:.1f}% retained
Value per 1%: ${percentages.valuePerShare:.2f}M""",
        "The ownership structure determines how future profits would be distributed between the partner and the company.",
        f"""
        - The pie chart visually represents the ownership split based on current deal parameters
        - Partner receives {percentages.partnerShare:.1f}% ownership for ${st.session_state.inputs['dealValue']}M investment
        - Company retains {percentages.companyShare:.1f}% ownership
        - Each 1% of ownership is valued at ${percentages.valuePerShare:.2f}M based on the calculated asset value
        - Ownership percentages translate directly to profit sharing in the same proportion
        """,
        expanded=False,
    )

    # Create and display the pie chart
    display_ownership_chart(percentages)


def display_asset_overview(
    phase_value: PhaseValueResult, percentages: DealPercentagesResult
) -> None:
    """Display asset and deal overview metrics."""

    def asset_overview_content():
        metrics = [
            ("Asset Value at Selected Stage", f"${phase_value.value:.1f}M", None, None),
            (
                "Value per 1% Ownership",
                f"${percentages.valuePerShare:.2f}M",
                None,
                None,
            ),
            (
                "Current Deal Value",
                f"${st.session_state.inputs['dealValue']}M",
                None,
                None,
            ),
            (
                "Resulting Ownership Percentage",
                f"{percentages.partnerShare:.1f}%",
                None,
                None,
            ),
        ]

        # Display as 2x2 grid
        row1 = metrics[:2]
        row2 = metrics[2:]

        create_multi_metric_row(row1)
        create_multi_metric_row(row2)

        # Ownership calculation details
        with st.expander("Ownership Calculation Details", expanded=False):
            st.markdown("#### Ownership Calculation:")
            st.code(
                f"Ownership % = Deal Value ÷ Asset Value = ${st.session_state.inputs['dealValue']}M ÷ ${phase_value.value:.1f}M = {percentages.partnerShare:.1f}%"
            )
            st.markdown("#### Value per 1% Calculation:")
            st.code(
                f"Value per 1% = Asset Value ÷ 100 = ${phase_value.value:.1f}M ÷ 100 = ${percentages.valuePerShare:.2f}M"
            )

    create_card("Asset and Deal Overview", asset_overview_content)


def display_ownership_details(
    phase_value: PhaseValueResult, percentages: DealPercentagesResult
) -> None:
    """Display detailed ownership distribution and deal assessment."""

    def ownership_content():
        partner_value = phase_value.value * percentages.partnerShare / 100
        company_value = phase_value.value * percentages.companyShare / 100

        metrics = [
            (
                "Partner Share",
                f"{percentages.partnerShare:.1f}%",
                None,
                f"${partner_value:.1f}M",
            ),
            (
                "Company Share",
                f"{percentages.companyShare:.1f}%",
                None,
                f"${company_value:.1f}M",
            ),
        ]

        create_multi_metric_row(metrics)

        # Deal assessment
        deal_assessment = (
            "⚠️ Undervalued"
            if st.session_state.inputs["dealValue"] < phase_value.value * 0.1
            else (
                "⚠️ Overvalued"
                if st.session_state.inputs["dealValue"] > phase_value.value * 0.9
                else "✓ Fair value"
            )
        )

        # Display the assessment with appropriate styling
        st.markdown("#### Deal Assessment")
        if "Undervalued" in deal_assessment:
            st.warning(f"{deal_assessment}")
        elif "Overvalued" in deal_assessment:
            st.warning(f"{deal_assessment}")
        else:
            st.success(f"{deal_assessment}")

    create_card("Ownership Distribution", ownership_content)


def display_ownership_chart(percentages: DealPercentagesResult) -> None:
    """Create and display pie chart showing ownership structure.

    Args:
        percentages (DealPercentagesResult): Dictionary containing ownership percentages
            and related calculations
    """
    # Prepare data for pie chart
    pie_data = pd.DataFrame(
        {
            "Entity": ["Partner Share", "Company Share"],
            "Percentage": [percentages.partnerShare, percentages.companyShare],
        }
    )

    # Create and display the pie chart
    fig = create_pie_chart(pie_data)
    st.plotly_chart(fig, use_container_width=True)
