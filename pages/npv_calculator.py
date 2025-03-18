import streamlit as st
import pandas as pd
from utils.calculations import calculate_phase_value
from utils.state import get_phase_display_name, get_order_options, get_phases_list
from components.ui_components import display_npv_results


def display_assumptions():
    """Display model assumptions section."""
    if st.session_state.show_assumptions:
        with st.expander("Model Assumptions", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Timing Assumptions (Years to Market)")
                timing_cols = st.columns(5)
                phases = get_phases_list()

                for i, phase in enumerate(phases):
                    with timing_cols[i]:
                        display_name = get_phase_display_name(phase)
                        st.session_state.inputs["timeToMarket"][phase] = (
                            st.number_input(
                                f"{display_name}",
                                min_value=0.0,
                                max_value=20.0,
                                value=float(
                                    st.session_state.inputs["timeToMarket"][phase]
                                ),
                                step=0.5,
                                key=f"time_{phase}",
                            )
                        )

                st.markdown("### Market Entry Multipliers")
                entry_cols = st.columns(4)

                labels = {
                    1: "1st to market",
                    2: "2nd to market",
                    3: "3rd to market",
                    4: "4th+ to market",
                }

                for i, (order, value) in enumerate(
                    st.session_state.inputs["orderMultipliers"].items()
                ):
                    with entry_cols[i]:
                        st.session_state.inputs["orderMultipliers"][order] = (
                            st.number_input(
                                f"{labels[order]}",
                                min_value=0.0,
                                max_value=1.0,
                                value=float(value),
                                step=0.01,
                                key=f"multiplier_{order}",
                            )
                        )

            with col2:
                st.markdown("### Financial Assumptions")
                st.markdown(
                    """
                - R&D costs subtracted from NPV when enabled
                - Only costs incurred up to current phase are subtracted
                - Deal value determines ownership percentage
                - No revenue milestone payments modeled
                """
                )

                st.markdown("### Valuation Assumptions")
                st.markdown(
                    """
                - Risk-adjusted using cumulative probability
                - Time value adjustment using discount rate
                - Time Factor = 1 / (1 + Discount Rate)^Years to Market
                - Final NPV includes both risk adjustment and time value
                - Costs to date are subtracted from risk-adjusted, time-adjusted value
                - No terminal value included
                - No tax implications modeled
                """
                )


def display_formulas():
    """Display NPV calculation formulas."""
    if st.session_state.show_formulas:
        with st.expander("NPV Calculation Formulas", expanded=True):
            st.markdown("### Base Value:")
            st.code("Base Value = Launch Value × Order Entry Multiplier")
            st.markdown("Applies market position discount to the potential peak value")

            st.markdown("### Cumulative Probability Calculation:")
            st.code(
                "For Phase 1: Cumulative Probability = P(Phase1) × P(Phase2) × P(Phase3) × P(Registration)"
            )
            st.markdown(
                "Represents the overall probability of reaching market from current stage"
            )

            st.markdown("### Time Factor Calculation:")
            st.code("Time Factor = 1 / (1 + Discount Rate)^Years to Market")
            st.markdown(
                "Converts future value to present value (e.g., Time Factor of 0.5 means $1 in future = $0.50 today)"
            )

            st.markdown("### Risk-Adjusted Value:")
            st.code("Risk-Adjusted Value = Base Value × Cumulative Success Probability")
            st.markdown(
                "Adjusts value based on probability of successfully reaching market"
            )

            st.markdown("### Final NPV Calculation:")
            st.code(
                """Final NPV = (Base Value × Cumulative Probability) × Time Factor - Cumulative R&D Costs
= (Base Value × Cumulative Probability) ÷ (1 + Discount Rate)^Years to Market - Costs"""
            )
            st.markdown(
                "Complete calculation incorporating risk, time value of money, and development costs"
            )


def display_basic_inputs():
    """Display basic inputs section."""
    st.subheader("Basic Inputs")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.session_state.inputs["launchValue"] = st.number_input(
            "Launch Value ($M)",
            min_value=0,
            value=st.session_state.inputs["launchValue"],
            step=50,
        )

    with col2:
        order_options = get_order_options()
        st.session_state.inputs["orderOfEntry"] = st.selectbox(
            "Order of Entry",
            options=list(order_options.keys()),
            format_func=lambda x: order_options[x],
            index=st.session_state.inputs["orderOfEntry"] - 1,
        )

    with col3:
        st.session_state.inputs["discountRate"] = st.number_input(
            "Discount Rate (%)",
            min_value=0.0,
            max_value=30.0,
            value=float(st.session_state.inputs["discountRate"]),
            step=0.5,
        )

    # R&D Costs Toggle
    st.session_state.inputs["includeRDCosts"] = st.checkbox(
        "Include R&D and Clinical Costs in NPV Calculation",
        value=st.session_state.inputs["includeRDCosts"],
    )


def display_probabilities():
    """Display success probabilities section."""
    st.subheader("Success Probabilities (%)")
    phases = get_phases_list()

    # Use columns for layout
    prob_cols = st.columns(len(phases))

    for i, phase in enumerate(phases):
        with prob_cols[i]:
            display_name = get_phase_display_name(phase)
            st.session_state.inputs["probabilities"][phase] = st.number_input(
                f"{display_name}",
                min_value=0,
                max_value=100,
                value=int(st.session_state.inputs["probabilities"][phase]),
                key=f"prob_{phase}",
            )


def display_costs():
    """Display R&D and clinical costs section."""
    st.subheader("R&D and Clinical Costs ($M)")
    phases = get_phases_list()

    # Use columns for layout
    cost_cols = st.columns(len(phases))

    for i, phase in enumerate(phases):
        with cost_cols[i]:
            display_name = get_phase_display_name(phase)
            st.session_state.inputs["costs"][phase] = st.number_input(
                f"{display_name}",
                min_value=0.0,
                value=float(st.session_state.inputs["costs"][phase]),
                step=0.1,
                key=f"cost_{phase}",
            )


def npv_calculator_page():
    """Display the NPV calculator page."""
    # Display assumptions and formulas
    display_assumptions()
    display_formulas()

    # Display inputs
    display_basic_inputs()
    display_probabilities()
    display_costs()

    # Display results
    display_npv_results(st.session_state.inputs)
