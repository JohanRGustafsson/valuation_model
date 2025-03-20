import streamlit as st
from typing import NoReturn, Dict, List, TypedDict, cast
from dataclasses import dataclass, field


class PhaseDicts(TypedDict):
    """Type definitions for phase-related dictionaries"""

    timeToMarket: Dict[str, float]
    costs: Dict[str, float]
    probabilities: Dict[str, float]


class InputParameters:
    """Input parameters for asset valuation.

    Attributes:
        launchValue: Peak sales value at launch in millions
        orderOfEntry: Market entry position (first, second, third, later)
        discountRate: Annual discount rate as percentage
        dealStage: Current development stage
        dealValue: Proposed deal value in millions
        desiredShare: Desired ownership percentage
        includeRDCosts: Whether to include R&D costs in calculation
        timeToMarket: Dict mapping phases to time to market in years
        costs: Dict mapping phases to R&D costs in millions
        probabilities: Dict mapping phases to success probabilities
        orderMultipliers: Dict mapping order numbers to market value multipliers
    """

    def __init__(self):
        self.launchValue: float = 1000.0
        self.orderOfEntry: str = "first"
        self.discountRate: float = 10.0
        self.dealStage: str = "preclinical"
        self.dealValue: float = 100.0
        self.desiredShare: float = 50.0
        self.includeRDCosts: bool = True
        self.timeToMarket: Dict[str, float] = {
            "preclinical": 1.0,
            "phase1": 2.0,
            "phase2": 3.0,
            "phase3": 3.0,
            "registration": 1.0,
        }
        self.costs: Dict[str, float] = {
            "preclinical": 10.0,
            "phase1": 15.0,
            "phase2": 30.0,
            "phase3": 50.0,
            "registration": 5.0,
        }
        self.probabilities: Dict[str, float] = {
            "preclinical": 80.0,
            "phase1": 60.0,
            "phase2": 40.0,
            "phase3": 65.0,
            "registration": 90.0,
        }
        self.orderMultipliers: Dict[int, float] = {
            1: 1.0,  # first to market: 100%
            2: 0.67,  # second to market: 67%
            3: 0.5,  # third to market: 50%
            4: 0.3,  # later entrant: 30%
        }

    def to_dict(self) -> dict:
        """Convert class to dictionary for easier serialization"""
        return {k: v for k, v in self.__dict__.items()}


def initialize_session_state() -> NoReturn:
    """Initialize Streamlit session state variables if they don't exist.

    This function sets up the initial state for the application by initializing:
    - Input parameters for calculations

    The function uses NoReturn type hint since it modifies the session state
    directly and doesn't return any value.
    """
    if "initialized" not in st.session_state:
        st.session_state.initialized = True

        # Input parameters
        st.session_state.inputs = InputParameters().to_dict()


def get_phase_display_name(phase: str) -> str:
    """Convert internal phase name to display-friendly format.

    Args:
        phase (str): Internal phase name (e.g., 'phase1', 'preclinical')

    Returns:
        str: Display-friendly phase name (e.g., 'Phase 1', 'Preclinical')
    """
    display_names = {
        "preclinical": "Preclinical",
        "phase1": "Phase 1",
        "phase2": "Phase 2",
        "phase3": "Phase 3",
        "registration": "Registration",
    }
    return display_names.get(phase, phase)


def get_phases_list() -> List[str]:
    """Get ordered list of all development phases.

    Returns:
        List[str]: List of phase names in chronological order
    """
    return ["preclinical", "phase1", "phase2", "phase3", "registration"]


def get_stage_options() -> Dict[str, str]:
    """Get mapping of development stages to their display names.

    Returns:
        Dict[str, str]: Dictionary mapping internal stage names to display names
    """
    return {
        "preclinical": "Preclinical",
        "phase1": "Phase 1",
        "phase2": "Phase 2",
        "phase3": "Phase 3",
        "registration": "Registration",
    }


def get_order_options() -> Dict[int, str]:
    """Get mapping of market entry order numbers to display names.

    Returns:
        Dict[int, str]: Dictionary mapping order numbers to display names
            1: "First to Market"
            2: "Second to Market"
            3: "Third to Market"
            4: "Later Entrant"
    """
    return {
        1: "First to Market",
        2: "Second to Market",
        3: "Third to Market",
        4: "Later Entrant",
    }


def get_inputs() -> PhaseDicts:
    """Get typed dictionary of inputs from session state."""
    return cast(PhaseDicts, st.session_state.inputs)
