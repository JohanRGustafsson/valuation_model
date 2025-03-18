import streamlit as st


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "show_assumptions" not in st.session_state:
        st.session_state.show_assumptions = False
    if "show_formulas" not in st.session_state:
        st.session_state.show_formulas = False
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "NPV Calculator"
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


def get_phase_display_name(phase):
    """Convert phase key to display name."""
    return phase.capitalize() if phase != "preclinical" else "Preclinical"


def get_stage_options():
    """Return dictionary of stage options."""
    return {
        "preclinical": "Preclinical",
        "phase1": "Phase 1",
        "phase2": "Phase 2",
        "phase3": "Phase 3",
        "registration": "Registration",
    }


def get_order_options():
    """Return dictionary of order entry options."""
    return {
        1: "1st (100%)",
        2: "2nd (67%)",
        3: "3rd (50%)",
        4: "4th+ (30%)",
    }


def get_phases_list():
    """Return list of phases in order."""
    return ["preclinical", "phase1", "phase2", "phase3", "registration"]


def toggle_assumptions():
    """Toggle the assumptions visibility."""
    st.session_state.show_assumptions = not st.session_state.show_assumptions


def toggle_formulas():
    """Toggle the formulas visibility."""
    st.session_state.show_formulas = not st.session_state.show_formulas
