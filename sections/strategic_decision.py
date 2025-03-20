import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Optional
from utils.calculations import (
    calculate_phase_value,
    calculate_strategic_decision,
    StrategicDecisionResult,
)
from utils.state import get_stage_options
from components.ui_components import (
    display_recommendation,
    create_comparison_bar_chart,
    create_metric,
    create_multi_metric_row,
    create_card,
    create_formula_expander,
    create_assumption_expander,
    create_formula_and_assumptions_expander,
)


@dataclass
class StrategicInputs:
    """Input parameters for strategic decision analysis.

    Attributes:
        dealStage: Current development stage
        timeToMarket: Dict mapping phases to time to market in years
        costs: Dict mapping phases to R&D costs in millions
        probabilities: Dict mapping phases to success probabilities
    """

    dealStage: str
    timeToMarket: Dict[str, float]
    costs: Dict[str, float]
    probabilities: Dict[str, float]


def strategic_decision_page() -> None:
    """Display the strategic decision making page for asset development strategy.

    This page helps users evaluate whether to continue development or out-license
    their asset at the current stage. It provides:
    - Input controls for current stage and licensing terms
    - Value analysis at current and next phases
    - Comparison of out-licensing vs continued development
    - Visual representation of options
    - Detailed calculations and recommendations

    The function directly modifies Streamlit's UI state and uses session state
    for maintaining input values across reruns.
    """
    st.header("Strategic Decision Making")
    st.markdown(
        "Should you continue development or out-license your asset at the current stage?"
    )

    # Main decision formula and assumptions (full width)
    create_formula_and_assumptions_expander(
        "Strategic Decision Framework",
        """Option 1: Out-License Now = Current Value × Out-License % + Current Value × (100% - Out-License %)
Option 2: Continue Development = Next Phase Value × Probability of Success""",
        "Choose the option with the higher expected value. Out-licensing provides immediate value but limits upside, while continued development offers higher potential returns but with added risk.",
        """
        - Both options are evaluated on expected value basis
        - No time adjustment between options (assumed to be contemporaneous decisions)
        - Out-licensing implies immediate upfront payment
        - Continued development assumes same discount rate as NPV calculation
        - Only one development phase ahead is considered in the analysis
        - No consideration of follow-on indications or expanded use
        - Risk is captured solely through probability of success
        """,
        expanded=False,
    )

    # Add selections for the strategic analysis
    strategic_col1, strategic_col2 = st.columns([1, 1])

    with strategic_col1:
        stage_options = get_stage_options()
        strategic_stage = st.selectbox(
            "Current Development Stage",
            options=list(stage_options.keys()),
            format_func=lambda x: stage_options[x],
            index=list(stage_options.keys()).index(
                st.session_state.inputs["dealStage"]
            ),
            key="strategic_stage",
        )

    with strategic_col2:
        out_license_percentage = st.slider(
            "Out-License Percentage (%)",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            key="strategic_license_percentage",
        )

    try:
        # Calculate the strategic decision
        decision_data = calculate_strategic_decision(
            st.session_state.inputs, strategic_stage, out_license_percentage
        )

        display_value_analysis(
            st.session_state.inputs, strategic_stage, decision_data, stage_options
        )
        display_strategic_options(decision_data, stage_options)
        display_additional_factors()
    except Exception as e:
        st.error(f"Error in strategic decision calculation: {str(e)}")


def display_value_analysis(
    inputs: StrategicInputs,
    strategic_stage: str,
    decision_data: StrategicDecisionResult,
    stage_options: Dict[str, str],
) -> None:
    """Display the asset value analysis section with current and next phase metrics.

    Args:
        inputs (StrategicInputs): Current valuation inputs from session state
        strategic_stage (str): Current development stage being analyzed
        decision_data (StrategicDecisionResult): Calculated decision metrics
        stage_options (Dict[str, str]): Mapping of stage codes to display names
    """
    st.subheader("Asset Value Analysis")

    # Value progression formula and assumptions (full width)
    if decision_data.next_phase:
        next_phase_value = calculate_phase_value(inputs, decision_data.next_phase).value
        current_phase_value = calculate_phase_value(inputs, strategic_stage).value
        value_change = next_phase_value - current_phase_value
        percent_change = (
            (value_change / current_phase_value * 100) if current_phase_value > 0 else 0
        )

        create_formula_and_assumptions_expander(
            "Value Progression Analysis",
            f"""Value at {stage_options[strategic_stage]}: ${current_phase_value:.1f}M
Value at {stage_options[decision_data.next_phase]}: ${next_phase_value:.1f}M
Value Change: ${value_change:.1f}M ({percent_change:.1f}%)
Success Probability: {decision_data.probability_next_phase:.1f}%
Risk-Adjusted Value Increase: ${value_change:.1f}M × {decision_data.probability_next_phase:.1f}% = ${(value_change * decision_data.probability_next_phase / 100):.1f}M""",
            "This analysis shows how asset value is expected to increase as the product progresses through development phases, along with the associated success probability.",
            """
            - Values shown are risk-adjusted NPVs at each development stage
            - Success probability represents likelihood of advancing to the next phase
            - Cost to complete the current phase is already factored into the NPV
            - Time to market difference is already accounted for in the NPV calculation
            - All probabilities based on historical industry benchmarks
            """,
            expanded=False,
        )

    def value_analysis_content():
        # Show current phase value
        current_phase_result = calculate_phase_value(inputs, strategic_stage)

        metrics = []
        metrics.append(
            (
                f"Asset Value at {stage_options[strategic_stage]}",
                f"${current_phase_result.value:.1f}M",
                None,
                None,
            )
        )

        if decision_data.next_phase:
            next_phase_result = calculate_phase_value(inputs, decision_data.next_phase)
            metrics.append(
                (
                    f"Asset Value at {stage_options[decision_data.next_phase]}",
                    f"${next_phase_result.value:.1f}M",
                    None,
                    f"{(next_phase_result.value - current_phase_result.value):.1f}M",
                )
            )

            metrics.append(
                (
                    f"Probability of Advancing",
                    f"{decision_data.probability_next_phase:.1f}%",
                    None,
                    None,
                )
            )

            cost = inputs["costs"][strategic_stage]
            metrics.append(("Cost to Complete Phase", f"${cost:.1f}M", None, None))
        else:
            metrics.append(("Next Phase", "N/A (Registration)", None, None))

        create_multi_metric_row(metrics[:3])  # Show first 3 metrics in one row
        if len(metrics) > 3:
            create_multi_metric_row(metrics[3:])  # Show remaining metrics

    create_card("Current and Next Phase Value", value_analysis_content)


def display_strategic_options(
    decision_data: StrategicDecisionResult, stage_options: Dict[str, str]
) -> None:
    """Display the strategic options comparison with licensing vs development analysis.

    Args:
        decision_data (StrategicDecisionResult): Calculated decision metrics
        stage_options (Dict[str, str]): Mapping of stage codes to display names
    """
    st.subheader("Strategic Options Comparison")

    # Strategic options formula and assumptions
    create_formula_and_assumptions_expander(
        "Strategic Options Calculation",
        (
            f"""Option 1 (Out-License Now): 
Value = Current Value × Out-License % + Current Value × (100% - Out-License %)
     = ${decision_data.current_phase_value:.1f}M × {decision_data.out_license_percentage}% + ${decision_data.current_phase_value:.1f}M × {100-decision_data.out_license_percentage}%
     = ${decision_data.deal_now_value:.1f}M

Option 2 (Continue Development): 
Value = Next Phase Value × Success Probability
     = ${calculate_phase_value(st.session_state.inputs, decision_data.next_phase).value:.1f}M × {decision_data.probability_next_phase:.1f}%
     = ${decision_data.continue_develop_value:.1f}M"""
            if decision_data.next_phase
            else f"""Option 1 (Out-License Now): 
Value = Current Value × Out-License % + Current Value × (100% - Out-License %)
     = ${decision_data.current_phase_value:.1f}M × {decision_data.out_license_percentage}% + ${decision_data.current_phase_value:.1f}M × {100-decision_data.out_license_percentage}%
     = ${decision_data.deal_now_value:.1f}M

Option 2 (Continue Development): 
Not applicable at registration stage"""
        ),
        f"Based on this analysis, the recommended strategy is to {decision_data.recommendation.lower()} because it generates ${abs(decision_data.value_difference):.1f}M more value.",
        """
        - Out-licensing splits ownership while preserving some long-term value
        - Continued development preserves 100% ownership but carries success risk
        - Both options are valued on expected value (EV) basis
        - The recommended option is the one with higher expected value
        - Option values already account for R&D costs, time value, and risk
        - Calculation is strictly financial and doesn't account for strategic considerations
        - See additional factors section for non-financial considerations
        """,
        expanded=False,
    )

    # Use tabs for displaying the two options
    option_tabs = st.tabs(
        ["Option 1: Out-License Now", "Option 2: Continue Development"]
    )

    with option_tabs[0]:
        display_license_option(decision_data)

    with option_tabs[1]:
        display_development_option(decision_data)

    # Display the recommendation
    st.subheader("Decision Recommendation")
    display_recommendation(decision_data.recommendation, decision_data.value_difference)

    # Create comparison bar chart if there's a next phase
    if decision_data.next_phase:
        display_comparison_chart(decision_data)


def display_license_option(decision_data: StrategicDecisionResult) -> None:
    """Display the out-licensing option analysis.

    Args:
        decision_data (StrategicDecisionResult): Calculated decision metrics
    """
    st.markdown(f"**Current Asset Value:** ${decision_data.current_phase_value:.1f}M")

    # Calculate values based on license percentage
    license_value = (
        decision_data.current_phase_value * decision_data.out_license_percentage
    ) / 100
    retained_value = decision_data.current_phase_value - license_value

    metrics = [
        (
            f"Out-License {decision_data.out_license_percentage}%",
            f"${license_value:.1f}M",
            None,
            None,
        ),
        (
            f"Retain {100-decision_data.out_license_percentage}%",
            f"${retained_value:.1f}M",
            None,
            None,
        ),
    ]

    create_multi_metric_row(metrics)
    create_metric(label="Total Value", value=f"${decision_data.deal_now_value:.1f}M")


def display_development_option(
    decision_data: StrategicDecisionResult,
) -> None:
    """Display the continued development option analysis.

    Args:
        decision_data (StrategicDecisionResult): Calculated decision metrics
    """
    if decision_data.next_phase:
        # Organized using metrics for clarity
        metrics = [
            (
                "Value if Successful",
                f"${calculate_phase_value(st.session_state.inputs, decision_data.next_phase).value:.1f}M",
                None,
                None,
            ),
            (
                "Probability of Success",
                f"{decision_data.probability_next_phase:.1f}%",
                None,
                None,
            ),
            (
                "Risk-Adjusted Expected Value",
                f"${decision_data.continue_develop_value:.1f}M",
                None,
                None,
            ),
        ]

        create_multi_metric_row(metrics)
        st.info("**Note:** Values already include all R&D costs through each phase")
    else:
        st.warning(
            "**No further development possible**\n\nAsset is at registration stage"
        )


def display_comparison_chart(decision_data: StrategicDecisionResult) -> None:
    """Display a bar chart comparing out-licensing vs development options.

    Args:
        decision_data (StrategicDecisionResult): Calculated decision metrics
    """
    comparison_data = pd.DataFrame(
        {
            "Option": ["Out-License Now", "Continue Development"],
            "Expected Value ($M)": [
                decision_data.deal_now_value,
                decision_data.continue_develop_value,
            ],
        }
    )

    fig = create_comparison_bar_chart(comparison_data)
    st.plotly_chart(fig, use_container_width=True)

    # Calculation details in expander
    with st.expander("Calculation Details", expanded=False):
        st.markdown("#### Out-License Calculation")
        st.code(
            f"""
Current Asset Value at {decision_data.current_phase_value:.1f}M
Out-License {decision_data.out_license_percentage}% = ${(decision_data.current_phase_value * decision_data.out_license_percentage / 100):.1f}M
Retained Value ({100-decision_data.out_license_percentage}%) = ${(decision_data.current_phase_value * (100-decision_data.out_license_percentage) / 100):.1f}M
Total Value = ${decision_data.deal_now_value:.1f}M
        """
        )

        if decision_data.next_phase:
            st.markdown("#### Continue Development Calculation")
            st.code(
                f"""
Next Phase Value if Successful = ${calculate_phase_value(st.session_state.inputs, decision_data.next_phase).value:.1f}M
Success Probability = {decision_data.probability_next_phase:.1f}%

Expected Value = Success Probability × Next Phase Value
Expected Value = {decision_data.probability_next_phase:.1f}% × ${calculate_phase_value(st.session_state.inputs, decision_data.next_phase).value:.1f}M = ${decision_data.continue_develop_value:.1f}M

Note: Both current and next phase values already include all R&D costs through each respective phase.
            """
            )


def display_additional_factors() -> None:
    """Display additional strategic factors to consider beyond financial calculations."""
    st.subheader("Additional Factors to Consider")

    # Additional factors expander (full width)
    create_assumption_expander(
        "Non-Financial Strategic Considerations",
        """
        Beyond the quantitative analysis, consider these factors when making your decision:
        
        **Continue Development Advantages:**
        - **Strategic Control**: Maintaining full control of asset development path and decisions
        - **Higher Upside**: Potential for significantly higher returns if successful
        - **Pipeline Value**: Building internal capabilities and expertise
        - **Future Partnering**: Possibility of better deal terms at a later stage with de-risked asset
        
        **Out-License Advantages:**
        - **Risk Mitigation**: Transfer development risk to partner
        - **Immediate Returns**: Secure upfront payment and near-term cashflow
        - **Resource Allocation**: Free up resources for other projects
        - **Partner Expertise**: Leverage partner's development and commercial capabilities
        
        **Company-Specific Considerations:**
        - Current cash position and funding needs
        - Internal development capabilities and experience
        - Portfolio diversification strategy
        - Competitive landscape dynamics
        - Patent life remaining
        - Long-term therapeutic area strategy
        """,
        expanded=False,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Continue Development Factors")
        st.markdown(
            """
        - **Strategic Control**: Maintaining full control of asset development
        - **Higher Upside**: Potential for significantly higher returns if successful
        - **Pipeline Value**: Building internal capabilities and expertise
        - **Future Partnering**: Possibility of better deal terms at a later stage
        """
        )

    with col2:
        st.markdown("### Out-License Factors")
        st.markdown(
            """
        - **Risk Mitigation**: Transfer development risk to partner
        - **Immediate Returns**: Secure upfront payment and near-term cashflow
        - **Resource Allocation**: Free up resources for other projects
        - **Partner Expertise**: Leverage partner's development and commercial capabilities
        """
        )

    st.markdown("### Other Considerations")
    st.markdown(
        """
    - Company cash position and funding needs
    - Internal development capabilities
    - Portfolio diversification strategy
    - Market competitive landscape changes
    - Patent life remaining
    """
    )
