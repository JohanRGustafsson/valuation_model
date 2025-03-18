import streamlit as st
import pandas as pd
from utils.calculations import calculate_phase_value, calculate_strategic_decision
from utils.state import get_stage_options
from components.ui_components import display_recommendation, create_comparison_bar_chart


def strategic_decision_page():
    """Display strategic decision making page."""
    st.header("Strategic Decision Making")
    st.markdown(
        "Should you continue development or out-license your asset at the current stage?"
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

    # Calculate the strategic decision
    decision_data = calculate_strategic_decision(
        st.session_state.inputs, strategic_stage, out_license_percentage
    )

    # Display the phase values and strategic analysis
    st.subheader("Asset Value Analysis")

    # Show current phase value
    current_phase_value = calculate_phase_value(
        st.session_state.inputs, strategic_stage
    )
    value_at_next_phase = (
        calculate_phase_value(st.session_state.inputs, decision_data["next_phase"])
        if decision_data["next_phase"]
        else 0
    )

    # Use metrics to display values with deltas
    value_cols = st.columns(3)
    with value_cols[0]:
        st.metric(
            label=f"Asset Value at {stage_options[strategic_stage]}",
            value=f"${current_phase_value:.1f}M",
        )

    with value_cols[1]:
        if decision_data["next_phase"]:
            st.metric(
                label=f"Asset Value at {stage_options[decision_data['next_phase']]}",
                value=f"${value_at_next_phase:.1f}M",
                delta=f"{(value_at_next_phase - current_phase_value):.1f}M",
            )
        else:
            st.metric(
                label="Next Phase",
                value="N/A (Registration)",
            )

    with value_cols[2]:
        if decision_data["next_phase"]:
            prob = decision_data["probability_next_phase"]
            st.metric(
                label=f"Probability of Advancing",
                value=f"{prob:.1f}%",
            )

            cost = st.session_state.inputs["costs"][strategic_stage]
            st.metric(
                label="Cost to Complete Phase",
                value=f"${cost:.1f}M",
            )

    # Use tabs for displaying the two options
    option_tabs = st.tabs(
        ["Option 1: Out-License Now", "Option 2: Continue Development"]
    )

    with option_tabs[0]:
        st.markdown(
            f"**Current Asset Value:** ${decision_data['current_phase_value']:.1f}M"
        )

        # Calculate values based on license percentage
        license_value = (
            decision_data["current_phase_value"]
            * decision_data["out_license_percentage"]
        ) / 100
        retained_value = decision_data["current_phase_value"] - license_value

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label=f"Out-License {decision_data['out_license_percentage']}%",
                value=f"${license_value:.1f}M",
            )
        with col2:
            st.metric(
                label=f"Retain {100-decision_data['out_license_percentage']}%",
                value=f"${retained_value:.1f}M",
            )

        st.metric(label="Total Value", value=f"${decision_data['deal_now_value']:.1f}M")

    with option_tabs[1]:
        if decision_data["next_phase"]:
            # Organized using metrics for clarity
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Value if Successful",
                    value=f"${calculate_phase_value(st.session_state.inputs, decision_data['next_phase']):.1f}M",
                )
                st.metric(
                    label="Risk-Adjusted Expected Value",
                    value=f"${decision_data['continue_develop_value']:.1f}M",
                )
            with col2:
                st.metric(
                    label="Probability of Success",
                    value=f"{decision_data['probability_next_phase']:.1f}%",
                )

            st.info("**Note:** Values already include all R&D costs through each phase")
        else:
            st.warning(
                "**No further development possible**\n\nAsset is at registration stage"
            )

    # Display the recommendation with native components
    st.subheader("Decision Recommendation")
    display_recommendation(
        decision_data["recommendation"], decision_data["value_difference"]
    )

    # Create comparison bar chart if there's a next phase
    if decision_data["next_phase"]:
        comparison_data = pd.DataFrame(
            {
                "Option": ["Out-License Now", "Continue Development"],
                "Expected Value ($M)": [
                    decision_data["deal_now_value"],
                    decision_data["continue_develop_value"],
                ],
            }
        )

        fig = create_comparison_bar_chart(comparison_data)
        st.plotly_chart(fig)

        # Display calculations if formulas are shown
        if st.session_state.show_formulas:
            with st.expander("How these calculations work", expanded=True):
                st.markdown("### Out-License Calculation")
                st.code(
                    f"""
    Current Asset Value at {stage_options[strategic_stage]} = ${decision_data['current_phase_value']:.1f}M
    Out-License {decision_data['out_license_percentage']}% = ${(decision_data['current_phase_value'] * decision_data['out_license_percentage'] / 100):.1f}M
    Retained Value ({100-decision_data['out_license_percentage']}%) = ${(decision_data['current_phase_value'] * (100-decision_data['out_license_percentage']) / 100):.1f}M
    Total Value = ${decision_data['deal_now_value']:.1f}M
                """
                )

                st.markdown("### Continue Development Calculation")
                st.code(
                    f"""
    Next Phase Value if Successful = ${calculate_phase_value(st.session_state.inputs, decision_data['next_phase']):.1f}M
    Success Probability = {decision_data['probability_next_phase']:.1f}%

    Expected Value = Success Probability × Next Phase Value
    Expected Value = {decision_data['probability_next_phase']:.1f}% × ${calculate_phase_value(st.session_state.inputs, decision_data['next_phase']):.1f}M = ${decision_data['continue_develop_value']:.1f}M

    Note: Both current and next phase values already include all R&D costs through each respective phase.
                """
                )

    # Additional factors to consider
    with st.expander("Additional Factors to Consider", expanded=True):
        st.markdown(
            """
        ### Beyond the Numbers

        While the financial calculation provides a recommendation, consider these additional factors:
        
        #### Continue Development Factors:
        - **Strategic Control**: Maintaining full control of asset development
        - **Higher Upside**: Potential for significantly higher returns if successful
        - **Pipeline Value**: Building internal capabilities and expertise
        - **Future Partnering**: Possibility of better deal terms at a later stage
        
        #### Out-License Factors:
        - **Risk Mitigation**: Transfer development risk to partner
        - **Immediate Returns**: Secure upfront payment and near-term cashflow
        - **Resource Allocation**: Free up resources for other projects
        - **Partner Expertise**: Leverage partner's development and commercial capabilities
        
        #### Other Considerations:
        - Company cash position and funding needs
        - Internal development capabilities
        - Portfolio diversification strategy
        - Market competitive landscape changes
        - Patent life remaining
        """
        )
