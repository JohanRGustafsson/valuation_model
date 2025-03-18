import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

# Set page configuration
st.set_page_config(
    page_title="Pharma Asset Valuation Calculator",
    page_icon="💊",
    layout="wide",
)

# App title
st.title("Pharma Asset Valuation (NPV Calculations)")

# Initialize session state variables if they don't exist
if "show_assumptions" not in st.session_state:
    st.session_state.show_assumptions = False
if "show_formulas" not in st.session_state:
    st.session_state.show_formulas = False
if "inputs" not in st.session_state:
    st.session_state.inputs = {
        "launchValue": 1000,
        "orderOfEntry": 1,
        "includeRDCosts": True,
        "dealStage": "phase1",
        "dealValue": 200,
        "desiredShare": 50,  # Partner's desired percentage
        "discountRate": 12,  # Discount rate for NPV calculations
        # Custom timing assumptions (years to market)
        "timeToMarket": {
            "preclinical": 8,
            "phase1": 6,
            "phase2": 4,
            "phase3": 2,
            "registration": 0.5,
        },
        # Custom order of entry multipliers
        "orderMultipliers": {
            1: 1.0,  # 1st to market (100%)
            2: 0.67,  # 2nd to market (67%)
            3: 0.5,  # 3rd to market (50%)
            4: 0.3,  # 4th+ to market (30%)
        },
        "probabilities": {
            "preclinical": 40,
            "phase1": 60,
            "phase2": 80,
            "phase3": 90,
            "registration": 95,
        },
        "costs": {
            "preclinical": 10,
            "phase1": 50,
            "phase2": 100,
            "phase3": 200,
            "registration": 50,
        },
    }


# Function to get order multiplier
def get_order_multiplier(order):
    return st.session_state.inputs["orderMultipliers"].get(
        order, st.session_state.inputs["orderMultipliers"][4]
    )  # Default to 4th+ if invalid


# Function to calculate cumulative probability
def get_cumulative_probability(phase):
    probabilities = st.session_state.inputs["probabilities"]

    if phase == "preclinical":
        return (
            probabilities["preclinical"]
            * probabilities["phase1"]
            * probabilities["phase2"]
            * probabilities["phase3"]
            * probabilities["registration"]
        ) / math.pow(100, 5)
    elif phase == "phase1":
        return (
            probabilities["phase1"]
            * probabilities["phase2"]
            * probabilities["phase3"]
            * probabilities["registration"]
        ) / math.pow(100, 4)
    elif phase == "phase2":
        return (
            probabilities["phase2"]
            * probabilities["phase3"]
            * probabilities["registration"]
        ) / math.pow(100, 3)
    elif phase == "phase3":
        return (probabilities["phase3"] * probabilities["registration"]) / math.pow(
            100, 2
        )
    elif phase == "registration":
        return probabilities["registration"] / 100
    else:
        return 1


# Function to calculate phase value with NPV adjustments
def calculate_phase_value(phase):
    base_value = st.session_state.inputs["launchValue"] * get_order_multiplier(
        st.session_state.inputs["orderOfEntry"]
    )
    risk_adjusted = base_value * get_cumulative_probability(phase)

    # Apply time-based NPV adjustment using custom timing values
    time_to_market = st.session_state.inputs["timeToMarket"].get(phase, 0)

    # Calculate NPV with discount rate
    discount_factor = math.pow(
        1 + (st.session_state.inputs["discountRate"] / 100), time_to_market
    )
    npv_adjusted = risk_adjusted / discount_factor

    if not st.session_state.inputs["includeRDCosts"]:
        return npv_adjusted

    # Subtract cumulative costs up to this phase
    cumulative_costs = 0
    costs = st.session_state.inputs["costs"]

    # Calculate remaining costs based on current phase
    if phase == "preclinical":
        # No previous costs
        pass
    elif phase == "phase1":
        cumulative_costs += costs["preclinical"]
    elif phase == "phase2":
        cumulative_costs += costs["preclinical"] + costs["phase1"]
    elif phase == "phase3":
        cumulative_costs += costs["preclinical"] + costs["phase1"] + costs["phase2"]
    elif phase == "registration":
        cumulative_costs += (
            costs["preclinical"] + costs["phase1"] + costs["phase2"] + costs["phase3"]
        )

    return npv_adjusted - cumulative_costs


# Function to calculate deal percentages
def calculate_deal_percentages():
    phase_value = calculate_phase_value(st.session_state.inputs["dealStage"])
    deal_value = st.session_state.inputs["dealValue"]

    # Calculate ownership percentage based on deal value relative to asset value
    ownership_percent = (
        min((deal_value / phase_value) * 100, 100) if phase_value > 0 else 0
    )

    return {
        "partnerShare": ownership_percent,
        "companyShare": 100 - ownership_percent,
        "totalValue": phase_value,
        "valuePerShare": phase_value / 100,  # Value per 1% ownership
    }


# Function to calculate required deal value for desired percentage
def calculate_required_deal_value(percentage):
    phase_value = calculate_phase_value(st.session_state.inputs["dealStage"])
    return (phase_value * percentage) / 100


# Function to calculate strategic decision between continuing development vs out-licensing
def calculate_strategic_decision(current_phase):
    # Get all phases and find the next phase
    phases = ["preclinical", "phase1", "phase2", "phase3", "registration"]
    if current_phase == "registration":
        next_phase = None  # No next phase after registration
    else:
        next_phase_index = phases.index(current_phase) + 1
        next_phase = phases[next_phase_index]

    # Calculate current deal option
    phase_value = calculate_phase_value(current_phase)
    deal_value = calculate_required_deal_value(st.session_state.inputs["desiredShare"])
    company_share_percentage = 100 - st.session_state.inputs["desiredShare"]
    retained_value = (phase_value * company_share_percentage) / 100

    total_deal_value = deal_value + retained_value

    # If there's no next phase, only the current deal is possible
    if next_phase is None:
        return {
            "current_phase": current_phase,
            "next_phase": None,
            "deal_now_value": total_deal_value,
            "continue_develop_value": 0,
            "recommendation": "Deal Now",
            "value_difference": total_deal_value,
            "probability_next_phase": 0,
        }

    # Calculate value of continuing development
    next_phase_value = calculate_phase_value(next_phase)

    # Calculate the costs to get to the next phase
    next_phase_cost = st.session_state.inputs["costs"][current_phase]

    # Calculate the probability of successfully progressing to the next phase
    probability_next_phase = (
        st.session_state.inputs["probabilities"][current_phase] / 100
    )

    # Expected value = (Success probability × Next phase value) - Cost to next phase
    expected_continue_value = (
        probability_next_phase * next_phase_value
    ) - next_phase_cost

    # Determine recommendation
    value_difference = expected_continue_value - total_deal_value
    if value_difference > 0:
        recommendation = "Continue Development"
    else:
        recommendation = "Deal Now"

    return {
        "current_phase": current_phase,
        "next_phase": next_phase,
        "deal_now_value": total_deal_value,
        "continue_develop_value": expected_continue_value,
        "recommendation": recommendation,
        "value_difference": abs(value_difference),
        "probability_next_phase": probability_next_phase * 100,
    }


# Main container
with st.container():
    # Toggle buttons for assumptions and formulas
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Net Present Value (NPV) Calculator")
    with col2:
        toggle_col1, toggle_col2 = st.columns(2)
        with toggle_col1:
            if st.button(
                "📋 "
                + (
                    "Hide Assumptions"
                    if st.session_state.show_assumptions
                    else "Show Assumptions"
                )
            ):
                st.session_state.show_assumptions = (
                    not st.session_state.show_assumptions
                )
        with toggle_col2:
            if st.button(
                "📊 "
                + (
                    "Hide Formulas"
                    if st.session_state.show_formulas
                    else "Show Formulas"
                )
            ):
                st.session_state.show_formulas = not st.session_state.show_formulas

    # Model Assumptions - Toggleable
    if st.session_state.show_assumptions:
        with st.expander("Model Assumptions", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Timing Assumptions (Years to Market)")
                timing_cols = st.columns(5)
                phases = list(st.session_state.inputs["timeToMarket"].keys())

                for i, phase in enumerate(phases):
                    with timing_cols[i]:
                        display_name = (
                            phase.capitalize()
                            if phase != "preclinical"
                            else "Preclinical"
                        )
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

    # Formula Explanation - Toggleable
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

    # NPV Basic Inputs
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
        order_options = {
            1: "1st (100%)",
            2: "2nd (67%)",
            3: "3rd (50%)",
            4: "4th+ (30%)",
        }
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

    # Success Probabilities
    st.subheader("Success Probabilities (%)")
    prob_cols = st.columns(5)
    phases = list(st.session_state.inputs["probabilities"].keys())

    for i, phase in enumerate(phases):
        with prob_cols[i]:
            display_name = (
                phase.capitalize() if phase != "preclinical" else "Preclinical"
            )
            st.session_state.inputs["probabilities"][phase] = st.number_input(
                f"{display_name}",
                min_value=0,
                max_value=100,
                value=int(st.session_state.inputs["probabilities"][phase]),
                key=f"prob_{phase}",
            )

    # R&D and Clinical Costs
    st.subheader("R&D and Clinical Costs ($M)")
    cost_cols = st.columns(5)

    for i, phase in enumerate(phases):
        with cost_cols[i]:
            display_name = (
                phase.capitalize() if phase != "preclinical" else "Preclinical"
            )
            st.session_state.inputs["costs"][phase] = st.number_input(
                f"{display_name}",
                min_value=0.0,
                value=float(st.session_state.inputs["costs"][phase]),
                step=0.1,
                key=f"cost_{phase}",
            )

    # NPV Results
    st.subheader("The Final NPV by Development Stage")
    result_cols = st.columns(5)

    # Prepare data for all phases
    phases = ["preclinical", "phase1", "phase2", "phase3", "registration"]
    phase_values = {}

    for i, phase in enumerate(phases):
        phase_value = calculate_phase_value(phase)
        phase_values[phase] = phase_value

        base_value = st.session_state.inputs["launchValue"] * get_order_multiplier(
            st.session_state.inputs["orderOfEntry"]
        )
        probability = get_cumulative_probability(phase)

        time_to_market = st.session_state.inputs["timeToMarket"][phase]
        discount_factor = math.pow(
            1 + (st.session_state.inputs["discountRate"] / 100), time_to_market
        )

        # Calculate costs for this phase
        cumulative_costs = 0
        if st.session_state.inputs["includeRDCosts"]:
            if phase == "phase1":
                cumulative_costs = st.session_state.inputs["costs"]["preclinical"]
            elif phase == "phase2":
                cumulative_costs = (
                    st.session_state.inputs["costs"]["preclinical"]
                    + st.session_state.inputs["costs"]["phase1"]
                )
            elif phase == "phase3":
                cumulative_costs = (
                    st.session_state.inputs["costs"]["preclinical"]
                    + st.session_state.inputs["costs"]["phase1"]
                    + st.session_state.inputs["costs"]["phase2"]
                )
            elif phase == "registration":
                cumulative_costs = (
                    st.session_state.inputs["costs"]["preclinical"]
                    + st.session_state.inputs["costs"]["phase1"]
                    + st.session_state.inputs["costs"]["phase2"]
                    + st.session_state.inputs["costs"]["phase3"]
                )

        with result_cols[i]:
            display_name = (
                phase.capitalize() if phase != "preclinical" else "Preclinical"
            )

            # Create a card-like display for each phase
            st.markdown(
                f"""
            <div style="padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f8f9fa;">
                <div style="font-weight: 600; font-size: 0.9rem;">{display_name}</div>
                <div style="font-size: 1.5rem; font-weight: 700; margin: 5px 0;">${phase_value:.1f}M</div>
                <div style="font-size: 0.8rem; margin-top: 8px;">
                    Time to market: {time_to_market} years
                </div>
                <div style="font-size: 0.8rem; color: gray; margin-top: 5px;">
                    NPV at {st.session_state.inputs['discountRate']}% discount rate
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Show detailed calculations if formulas are toggled on
            if st.session_state.show_formulas:
                st.markdown(
                    "<hr style='margin: 10px 0; border-color: #eee;'>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                <div style="font-size: 0.8rem;">
                    <div><strong>Base Value:</strong> ${base_value:.1f}M</div>
                    <div><strong>Probability:</strong> {(probability * 100):.2f}%</div>
                    <div><strong>Time Factor:</strong> {(1/discount_factor):.3f}</div>
                    {f"<div><strong>Costs to date:</strong> ${cumulative_costs}M</div>" if st.session_state.inputs['includeRDCosts'] else ""}
                    <div style="background-color: #fff; padding: 5px; border-radius: 4px; margin-top: 5px;">
                        ${base_value:.1f}M × {(probability * 100):.1f}% ÷ {discount_factor:.2f} 
                        {f" - ${cumulative_costs}M" if st.session_state.inputs['includeRDCosts'] else ""} = 
                        <strong> ${phase_value:.1f}M</strong>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # Deal Analysis Section
    st.markdown("---")
    st.header("Deal Analysis")

    # Deal Parameters
    st.subheader("Deal Parameters")
    deal_col1, deal_col2, deal_col3 = st.columns(3)

    with deal_col1:
        stage_options = {
            "preclinical": "Preclinical",
            "phase1": "Phase 1",
            "phase2": "Phase 2",
            "phase3": "Phase 3",
            "registration": "Registration",
        }
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
            percentages = calculate_deal_percentages()
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
            percentages = calculate_deal_percentages()
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
            required_deal_value = calculate_required_deal_value(new_share)
            st.session_state.inputs["dealValue"] = round(required_deal_value, 1)

    # Deal Value Analysis
    st.subheader("Deal Value Analysis")

    percentages = calculate_deal_percentages()
    phase_value = calculate_phase_value(st.session_state.inputs["dealStage"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Asset Value at Selected Stage:** ${phase_value:.1f}M")
        st.markdown(f"**Current Deal Value:** ${st.session_state.inputs['dealValue']}M")
        st.markdown(
            f"**Resulting Ownership Percentage:** {percentages['partnerShare']:.1f}%"
        )
        st.markdown(f"**Value per 1% Ownership:** ${percentages['valuePerShare']:.1f}M")

        if st.session_state.show_formulas:
            st.markdown("---")
            st.markdown("**Ownership Calculation:**")
            st.code(
                f"Ownership % = Deal Value ÷ Asset Value = ${st.session_state.inputs['dealValue']}M ÷ ${phase_value:.1f}M = {percentages['partnerShare']:.1f}%"
            )

    with col2:
        st.markdown(f"**Partner Gets:** {percentages['partnerShare']:.1f}% Ownership")
        st.markdown(
            f"**Partner Value:** ${(phase_value * percentages['partnerShare'] / 100):.1f}M"
        )
        st.markdown(
            f"**Company Retains:** {percentages['companyShare']:.1f}% Ownership"
        )
        st.markdown(
            f"**Company Value:** ${(phase_value * percentages['companyShare'] / 100):.1f}M"
        )

        deal_assessment = (
            "⚠️ Undervalued"
            if st.session_state.inputs["dealValue"] < phase_value * 0.1
            else (
                "⚠️ Overvalued"
                if st.session_state.inputs["dealValue"] > phase_value * 0.9
                else "✓ Fair value"
            )
        )
        st.markdown(f"**Deal Assessment:** {deal_assessment}")

    # Pie Chart for Ownership Structure
    st.subheader("Ownership Structure")

    # Prepare data for pie chart
    pie_data = pd.DataFrame(
        {
            "Entity": ["Partner Share", "Company Share"],
            "Percentage": [percentages["partnerShare"], percentages["companyShare"]],
        }
    )

    # Create a pie chart using Plotly
    fig = go.Figure(
        data=[
            go.Pie(
                labels=pie_data["Entity"],
                values=pie_data["Percentage"],
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

    st.plotly_chart(fig, use_container_width=True)

# Strategic Decision Making Section
st.markdown("---")
st.header("Strategic Decision Making")
st.markdown(
    "Should you continue development or out-license your asset at the current stage?"
)

# Add a selection for the current phase for the strategic analysis
strategic_col1, strategic_col2 = st.columns([1, 3])

with strategic_col1:
    stage_options = {
        "preclinical": "Preclinical",
        "phase1": "Phase 1",
        "phase2": "Phase 2",
        "phase3": "Phase 3",
        "registration": "Registration",
    }

    strategic_stage = st.selectbox(
        "Current Development Stage",
        options=list(stage_options.keys()),
        format_func=lambda x: stage_options[x],
        index=list(stage_options.keys()).index(st.session_state.inputs["dealStage"]),
        key="strategic_stage",
    )

# Calculate the strategic decision
decision_data = calculate_strategic_decision(strategic_stage)

# Display the strategic analysis
with strategic_col2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Option 1: Out-License Now")
        st.markdown(
            f"**Deal Value:** ${calculate_required_deal_value(st.session_state.inputs['desiredShare']):.1f}M"
        )
        st.markdown(
            f"**Retained Value (at {100-st.session_state.inputs['desiredShare']:.1f}% ownership):** ${(calculate_phase_value(strategic_stage) * (100-st.session_state.inputs['desiredShare']) / 100):.1f}M"
        )
        st.markdown(
            f"**Total Expected Value:** ${decision_data['deal_now_value']:.1f}M"
        )

    with col2:
        if decision_data["next_phase"]:
            st.subheader(
                f"Option 2: Continue to {stage_options[decision_data['next_phase']]}"
            )
            st.markdown(
                f"**Value if Successful:** ${calculate_phase_value(decision_data['next_phase']):.1f}M"
            )
            st.markdown(
                f"**Cost to Complete Current Phase:** ${st.session_state.inputs['costs'][strategic_stage]:.1f}M"
            )
            st.markdown(
                f"**Probability of Success:** {decision_data['probability_next_phase']:.1f}%"
            )
            st.markdown(
                f"**Risk-Adjusted Expected Value:** ${decision_data['continue_develop_value']:.1f}M"
            )
        else:
            st.subheader("Option 2: Continue Development")
            st.markdown("**No further development possible**")
            st.markdown("**Asset is at registration stage**")

# Display the recommendation with visualization
st.subheader("Decision Recommendation")

# Create recommendation card
recommendation_color = (
    "#28a745"
    if decision_data["recommendation"] == "Continue Development"
    else "#17a2b8"
)
value_diff = decision_data["value_difference"]

recommendation_html = f"""
<div style="padding: 20px; border-radius: 5px; background-color: {recommendation_color}; color: white; margin-bottom: 20px;">
    <h3 style="margin: 0;">Recommendation: {decision_data['recommendation']}</h3>
    <p style="margin: 10px 0 0 0; font-size: 1.1rem;">
        {decision_data['recommendation']} is expected to generate <strong>${value_diff:.1f}M more value</strong>
    </p>
</div>
"""
st.markdown(recommendation_html, unsafe_allow_html=True)

# Create comparison bar chart
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

    fig = go.Figure(
        data=[
            go.Bar(
                x=comparison_data["Option"],
                y=comparison_data["Expected Value ($M)"],
                marker_color=["#17a2b8", "#28a745"],
                text=[f"${v:.1f}M" for v in comparison_data["Expected Value ($M)"]],
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

    st.plotly_chart(fig)

    # Display calculations if formulas are shown
    if st.session_state.show_formulas:
        with st.expander("How these calculations work", expanded=True):
            st.markdown("### Out-License Calculation")
            st.code(
                f"""
Deal Value = ${calculate_required_deal_value(st.session_state.inputs['desiredShare']):.1f}M
Retained Value = ${(calculate_phase_value(strategic_stage) * (100-st.session_state.inputs['desiredShare']) / 100):.1f}M (retained {100-st.session_state.inputs['desiredShare']}% ownership)
Total Deal Value = ${decision_data['deal_now_value']:.1f}M
            """
            )

            st.markdown("### Continue Development Calculation")
            st.code(
                f"""
Next Phase Value if Successful = ${calculate_phase_value(decision_data['next_phase']):.1f}M
Cost to Complete {stage_options[strategic_stage]} = ${st.session_state.inputs['costs'][strategic_stage]:.1f}M
Success Probability = {decision_data['probability_next_phase']:.1f}%
            
Expected Value = (Success Probability × Next Phase Value) - Development Cost
Expected Value = ({decision_data['probability_next_phase']:.1f}% × ${calculate_phase_value(decision_data['next_phase']):.1f}M) - ${st.session_state.inputs['costs'][strategic_stage]:.1f}M = ${decision_data['continue_develop_value']:.1f}M
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

# Footer
st.markdown("---")
st.markdown("**Pharma Asset Valuation Calculator** - Built with Streamlit")
