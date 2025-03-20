import streamlit as st
from utils.state import get_phase_display_name, get_order_options, get_phases_list
from components.ui_components import (
    display_npv_results,
    create_metric,
    display_formula_expander,
    create_multi_metric_row,
    create_formula_expander,
    create_assumption_expander,
    create_formula_and_assumptions_expander,
)


def _display_assumption_explanations() -> None:
    """Display explanations for assumptions in the model."""
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


def display_basic_inputs() -> None:
    """Display and handle basic input parameters for NPV calculation.

    Shows input controls for:
    - Launch value
    - Order of entry
    - Discount rate
    - R&D costs toggle

    Updates session state with user input values.
    """
    st.subheader("Basic Inputs")

    # Combined formulas and assumptions expander for Basic Inputs
    create_formula_and_assumptions_expander(
        "Basic Input Calculations & Assumptions",
        """Base Value = Launch Value × Order Entry Multiplier
Time Factor = 1 / (1 + Discount Rate)^Years to Market
Final NPV = (Base Value × Cumulative Probability) × Time Factor - Cumulative R&D Costs""",
        """
        The complete NPV calculation incorporates:
        - Base value calculation using launch value and market entry position
        - Time value adjustment using the discount rate
        - Risk adjustment using cumulative probability
        - R&D cost subtraction (when enabled)
        """,
        """
        - **Base Value** assumes peak sales potential at launch
        - **Launch Value** represents undiscounted peak sales in millions
        - **Order Entry** impacts market share based on competitive position:
          - First to Market (100%): Maximum market share potential as the pioneering product
          - Second to Market (67%): Reduced market potential due to established competition
          - Third to Market (50%): Significant market share limitations as a later entrant
          - Later Entrant (30%): Heavily reduced market potential in a crowded market
        - The model assumes constant discount rate throughout all phases
        - No competitive entry is modeled after initial market positioning
        """,
        expanded=False,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.session_state.inputs["launchValue"] = st.number_input(
            "Launch Value ($M)",
            min_value=0.0,
            value=float(st.session_state.inputs["launchValue"]),
            step=50.0,
        )

    with col2:
        order_options = get_order_options()
        # Convert string order to numeric index
        order_mapping = {"first": 1, "second": 2, "third": 3, "later": 4}
        current_order = order_mapping.get(st.session_state.inputs["orderOfEntry"], 1)

        selected_order = st.selectbox(
            "Order of Entry",
            options=list(order_options.keys()),
            format_func=lambda x: order_options[x],
            index=current_order - 1,
        )
        # Convert numeric order back to string format
        reverse_mapping = {1: "first", 2: "second", 3: "third", 4: "later"}
        st.session_state.inputs["orderOfEntry"] = reverse_mapping[selected_order]

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


def display_probabilities() -> None:
    """Display and handle success probability inputs for each phase.

    Shows a row of number input controls for setting success probabilities
    for each development phase. Updates session state with user inputs.
    """
    st.subheader("Success Probabilities (%)")

    # Probability formula and assumptions (full width)
    create_formula_and_assumptions_expander(
        "Success Probability Calculation & Assumptions",
        "Cumulative Probability = P(Phase1) × P(Phase2) × P(Phase3) × P(Registration)",
        "The overall probability of reaching market from the current stage is calculated by multiplying all individual phase probabilities that remain to be completed.",
        """
        - Probabilities represent the chance of advancing from one phase to the next
        - Industry benchmarks for typical success rates:
          - Preclinical to Phase 1: 70-80%
          - Phase 1 to Phase 2: 50-70%
          - Phase 2 to Phase 3: 30-50%
          - Phase 3 to Registration: 60-70%
          - Registration to Approval: 80-95%
        - These probabilities vary by therapeutic area and indication
        - The model uses simple multiplication of probabilities (assumes independence)
        """,
        expanded=False,
    )

    _display_phase_inputs("probabilities", 0.0, 100.0, 1.0, "prob_")


def display_costs() -> None:
    """Display and handle R&D and clinical cost inputs for each phase.

    Shows a row of number input controls for setting development costs
    for each phase. Updates session state with user inputs.
    """
    st.subheader("R&D and Clinical Costs ($M)")

    # Cost calculation formula and assumptions (full width)
    create_formula_and_assumptions_expander(
        "R&D Cost Calculation & Assumptions",
        "Cumulative Costs = Sum of all costs up to and including current phase",
        "When the R&D costs toggle is enabled, the calculator subtracts all R&D costs incurred up to and including the current phase from the risk-adjusted NPV.",
        """
        - Costs are treated as incurred at the start of each phase
        - Only costs up to the selected phase are included in the calculation
        - No inflation adjustment is applied to costs
        - The model doesn't account for time distribution of costs within phases
        - Typical cost ranges vary significantly by therapeutic area:
          - Preclinical: $5-15M
          - Phase 1: $10-30M
          - Phase 2: $20-60M
          - Phase 3: $30-100M+
          - Registration: $5-10M
        """,
        expanded=False,
    )

    _display_phase_inputs("costs", 0.0, None, 0.1, "cost_")


def _display_phase_inputs(
    input_type: str,
    min_value: float,
    max_value: float = None,
    step: float = 1.0,
    key_prefix: str = "",
) -> None:
    """Generic function to display inputs for each phase.

    Args:
        input_type: The type of input (costs, probabilities, etc.)
        min_value: Minimum allowed value
        max_value: Maximum allowed value (or None for no max)
        step: Step size for increment/decrement
        key_prefix: Prefix for Streamlit widget keys
    """
    # Timing Assumptions
    if input_type == "probabilities" or input_type == "costs":
        show_timing = input_type == "probabilities"
        if show_timing:
            st.markdown("#### Time to Market (Years)")
            timing_cols = st.columns(5)
            phases = get_phases_list()
            for i, phase in enumerate(phases):
                with timing_cols[i]:
                    display_name = get_phase_display_name(phase)
                    st.caption(
                        f"{display_name}: {st.session_state.inputs['timeToMarket'][phase]:.1f} years"
                    )

    phases = get_phases_list()
    cols = st.columns(len(phases))

    for i, phase in enumerate(phases):
        with cols[i]:
            display_name = get_phase_display_name(phase)
            st.session_state.inputs[input_type][phase] = st.number_input(
                f"{display_name}",
                min_value=min_value,
                max_value=max_value,
                value=float(st.session_state.inputs[input_type][phase]),
                step=step,
                key=f"{key_prefix}{phase}",
            )


def display_timing_inputs() -> None:
    """Display and handle time to market inputs for each phase.

    Shows a row of number input controls for setting time to market
    for each phase. Updates session state with user inputs.
    """
    st.subheader("Time to Market (Years)")

    create_formula_and_assumptions_expander(
        "Time Value Calculation & Assumptions",
        "Time Factor = 1 / (1 + Discount Rate)^Years to Market",
        "Time to market affects the present value of future cash flows. The longer it takes to reach market, the lower the present value due to discounting.",
        """
        - Times represent years from current phase to market launch
        - Typical development timelines:
          - Preclinical to market: 8-10 years
          - Phase 1 to market: 6-8 years
          - Phase 2 to market: 4-6 years
          - Phase 3 to market: 2-3 years
          - Registration to market: 1 year
        - No acceleration of timelines is modeled
        - Time to market affects discount factor but not probability
        """,
        expanded=False,
    )

    phases = get_phases_list()
    cols = st.columns(len(phases))

    for i, phase in enumerate(phases):
        with cols[i]:
            display_name = get_phase_display_name(phase)
            st.session_state.inputs["timeToMarket"][phase] = st.number_input(
                f"{display_name}",
                min_value=0.0,
                max_value=20.0,
                value=float(st.session_state.inputs["timeToMarket"][phase]),
                step=0.5,
                key=f"time_{phase}",
            )


def npv_calculator_page() -> None:
    """Display the main NPV calculator page with all components.

    This function creates the complete NPV calculator interface including:
    - Model assumptions and formulas
    - Basic inputs (launch value, order of entry, etc.)
    - Success probabilities for each phase
    - R&D and clinical costs for each phase
    - NPV results display

    The function handles all user interactions and updates calculations
    in real-time as users modify inputs.
    """
    # Display inputs in the order that makes most sense
    display_timing_inputs()
    display_basic_inputs()
    display_probabilities()
    display_costs()

    # Display results
    display_npv_results(st.session_state.inputs)
