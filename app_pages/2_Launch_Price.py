import streamlit as st
import pandas as pd
import plotly.express as px
from typing import TypedDict
from dataclasses import dataclass
from utils.calculations import calculate_order_multiplier
from components.ui_components import (
    create_formula_expander,
    create_assumption_expander,
    create_formula_and_assumptions_expander,
)


@dataclass
class PriceInputs:
    """Input parameters for launch price calculations.

    Attributes:
        market_value: Total disease market value in millions
        order_of_entry: Market entry position ('first', 'second', 'third', 'later')
        estimated_patients: Total estimated patient population
        diagnosed_patients: Number of diagnosed patients
        treated_patients: Number of patients currently receiving treatment
        adoption_rate: Expected percentage of eligible patients who will adopt
    """

    market_value: float
    order_of_entry: str
    estimated_patients: int
    diagnosed_patients: int
    treated_patients: int
    adoption_rate: float


@dataclass
class MarketPenetrationResult:
    """Results of market penetration calculation.

    Attributes:
        penetration: Market penetration percentage (0-100)
        treatment_rate: Current treatment rate percentage (0-100)
        effective_patients: Number of patients at calculated penetration
    """

    penetration: float
    treatment_rate: float
    effective_patients: int


@dataclass
class LaunchPriceResult:
    """Results of launch price calculation.

    Attributes:
        launch_price: Recommended price per patient in dollars
        total_disease_market_value: Total market size in millions
        adjusted_market_value: Market value adjusted for entry order in millions
        effective_patients: Number of patients at calculated penetration
        general_price: Price if all patients used treatment in dollars
        foreseen_adoption_price: Price based on adoption rate in dollars
        foreseen_adoption_patients: Number of patients at adoption rate
        your_market_revenue: Expected revenue at penetration in millions
    """

    launch_price: float
    total_disease_market_value: float
    adjusted_market_value: float
    effective_patients: int
    general_price: float
    foreseen_adoption_price: float
    foreseen_adoption_patients: int
    your_market_revenue: float


def calculate_market_penetration(
    treated_patients: int, diagnosed_patients: int, adoption_rate: float
) -> MarketPenetrationResult:
    """Calculate the market penetration percentage based on patient numbers and adoption rate.

    Args:
        treated_patients (int): Number of patients currently receiving treatment
        diagnosed_patients (int): Total number of diagnosed patients
        adoption_rate (float): Expected percentage of eligible patients who will adopt (0-100)

    Returns:
        MarketPenetrationResult: Dictionary containing:
            - penetration: Market penetration percentage (0-100)
            - treatment_rate: Current treatment rate percentage (0-100)
            - effective_patients: Number of patients at calculated penetration

    Raises:
        ValueError: If adoption rate is outside valid range (0-100)
        ValueError: If patient numbers are negative
    """
    if not 0 <= adoption_rate <= 100:
        raise ValueError("Adoption rate must be between 0 and 100")
    if treated_patients < 0 or diagnosed_patients < 0:
        raise ValueError("Patient numbers cannot be negative")

    treatment_rate = (
        (treated_patients / diagnosed_patients * 100) if diagnosed_patients > 0 else 0
    )
    penetration = treatment_rate * (adoption_rate / 100)
    penetration = min(max(round(penetration, 1), 0), 100)
    effective_patients = int(diagnosed_patients * (penetration / 100))

    return MarketPenetrationResult(
        penetration=penetration,
        treatment_rate=treatment_rate,
        effective_patients=effective_patients,
    )


def calculate_launch_price(
    inputs: PriceInputs, penetration: float
) -> LaunchPriceResult:
    """Calculate launch price and related market metrics based on inputs and penetration.

    Args:
        inputs (PriceInputs): Dictionary containing:
            - market_value: Total disease market value (in millions)
            - order_of_entry: Market entry position (first, second, third, later)
            - estimated_patients: Total estimated patient population
            - adoption_rate: Expected adoption rate percentage (0-100)
        penetration (float): Calculated market penetration percentage (0-100)

    Returns:
        LaunchPriceResult: Dictionary containing:
            - launch_price: Recommended price per patient (in dollars)
            - total_disease_market_value: Total market size (in millions)
            - adjusted_market_value: Market value adjusted for entry order (in millions)
            - effective_patients: Number of patients at calculated penetration
            - general_price: Price if all patients used treatment (in dollars)
            - foreseen_adoption_price: Price based on adoption rate (in dollars)
            - foreseen_adoption_patients: Patients at adoption rate
            - your_market_revenue: Expected revenue at penetration (in millions)

    Raises:
        ValueError: If penetration is outside valid range (0-100)
        ValueError: If market value is negative
        ValueError: If patient numbers are negative
    """
    if not 0 <= penetration <= 100:
        raise ValueError("Penetration must be between 0 and 100")
    if inputs.market_value < 0:
        raise ValueError("Market value cannot be negative")
    if inputs.estimated_patients < 0:
        raise ValueError("Patient numbers cannot be negative")

    # Get order multiplier from utils
    order_result = calculate_order_multiplier(inputs.order_of_entry)

    # Calculate values
    total_disease_market_value = inputs.market_value
    adjusted_market_value = total_disease_market_value * order_result.multiplier
    effective_patients = int(inputs.estimated_patients * (penetration / 100))
    foreseen_adoption_patients = int(
        inputs.estimated_patients * (inputs.adoption_rate / 100)
    )

    # Calculate prices
    general_price = (
        (adjusted_market_value * 1_000_000) / inputs.estimated_patients
        if inputs.estimated_patients > 0
        else 0
    )
    foreseen_adoption_price = (
        (adjusted_market_value * 1_000_000) / foreseen_adoption_patients
        if foreseen_adoption_patients > 0
        else 0
    )
    launch_price = (
        (adjusted_market_value * 1_000_000) / effective_patients
        if effective_patients > 0
        else 0
    )
    your_market_revenue = (penetration / 100) * adjusted_market_value

    return LaunchPriceResult(
        launch_price=launch_price,
        total_disease_market_value=total_disease_market_value,
        adjusted_market_value=adjusted_market_value,
        effective_patients=effective_patients,
        general_price=general_price,
        foreseen_adoption_price=foreseen_adoption_price,
        foreseen_adoption_patients=foreseen_adoption_patients,
        your_market_revenue=your_market_revenue,
    )


def display_price_terminology() -> None:
    """Display an expandable section explaining price terminology used in the calculator.

    Creates a Streamlit expander with markdown content explaining various pricing terms
    and metrics used throughout the calculator interface.
    """
    with st.expander("💡 Price Terminology Guide", expanded=False):
        st.markdown(
            """
        - **Total Disease Market Value**: The entire market size for this disease (in $M)
        - **Your Market Revenue**: What you'll earn with your market penetration percentage
        - **Adjusted Market Value**: The disease market value adjusted for your order of entry
        - **Recommended Launch Price**: The price per patient you should charge
        - **General Price**: The price per patient if all potential patients used your treatment
        - **Adoption-Based Price**: The price per patient based solely on your adoption rate
        """
        )


def display_adoption_rate_help() -> None:
    """Display an expandable section with guidance on determining adoption rates.

    Creates a Streamlit expander with markdown content explaining how to estimate
    adoption rates and typical values for different types of products.
    """
    with st.expander("📊 How to determine Adoption Rate?", expanded=False):
        st.markdown(
            """
        Adoption rate can be estimated through:
        - Market research studies with physicians
        - Analysis of similar products' uptake rates
        - Competitive advantage assessment
        - Patient preference surveys
        - Clinical differentiation from existing treatments
        
        **Typical values:**
        - 10-20% for me-too products
        - 30-50% for differentiated products
        - 60-80% for highly innovative treatments
        """
        )


def launch_price_calculator_page() -> None:
    """Display the main launch price calculator page with all its components.

    This function creates the complete user interface for the launch price calculator,
    including:
    - Title and description
    - Input parameters for market and patient data
    - Price terminology guide
    - Adoption rate help
    - Formula explanations
    - Key assumptions
    - Results display with metrics and visualizations

    The function handles all user interactions and updates the display in real-time
    as users modify input parameters.
    """
    st.title("Launch Price Calculator 💰")
    st.markdown("Calculate optimal pricing based on market size and penetration")

    # Display price terminology guide
    display_price_terminology()

    # Overview section with terminology
    st.header("Overview")

    # Master formula for launch price (full width)
    create_formula_and_assumptions_expander(
        "Launch Price Calculation Process",
        """Launch Price = (Market Value × Order Entry Multiplier × 1,000,000) / (Estimated Patients × Market Penetration %)
Market Penetration = (Treated Patients / Diagnosed Patients) × Adoption Rate""",
        "The price per patient is determined by dividing the adjusted market value (converted to dollars) by the number of patients expected to use your treatment based on market penetration.",
        """
        - The calculator assumes a single price point across all patient segments
        - No price differentiation by geography, indication, or patient subgroups
        - Future price increases/decreases are not modeled
        - Competition is accounted for only through the order of entry adjustment
        - Patient numbers refer to annual patient populations, not cumulative
        - Price is calculated as annual treatment cost per patient
        - Order of entry impacts market value: 1st (100%), 2nd (67%), 3rd (50%), Later (30%)
        - Diagnosed patients represent the total diagnosed population with the condition
        - Treated patients represent those currently receiving any treatment for the condition
        - Adoption rate represents the percentage of eligible patients expected to adopt your specific treatment
        - Market penetration calculation assumes similar treatment patterns to current standards
        """,
        expanded=False,
    )

    # Input Parameters
    st.header("Input Parameters")

    # Display adoption rate help within input section
    display_adoption_rate_help()

    col1, col2 = st.columns(2)

    with col1:
        market_value = st.number_input(
            "Market Value ($M)", min_value=0.0, value=1000.0, step=50.0
        )

        order_of_entry = st.selectbox(
            "Order of Entry",
            options=["first", "second", "third", "later"],
            format_func=lambda x: {
                "first": "1st (100%)",
                "second": "2nd (67%)",
                "third": "3rd (50%)",
                "later": "Later (30%)",
            }[x],
        )

        estimated_patients = st.number_input(
            "Estimated Patients", min_value=0, value=100000, step=1000
        )

    with col2:
        diagnosed_patients = st.number_input(
            "Diagnosed Patients", min_value=0, value=500000, step=1000
        )
        treated_patients = st.number_input(
            "Treated Patients", min_value=0, value=300000, step=1000
        )

        adoption_rate = st.slider(
            "Adoption Rate (%)", min_value=0, max_value=100, value=50
        )

    # Calculate results
    inputs = PriceInputs(
        market_value=market_value,
        order_of_entry=order_of_entry,
        estimated_patients=estimated_patients,
        diagnosed_patients=diagnosed_patients,
        treated_patients=treated_patients,
        adoption_rate=adoption_rate,
    )

    penetration = calculate_market_penetration(
        treated_patients, diagnosed_patients, adoption_rate
    )
    results = calculate_launch_price(inputs, penetration.penetration)

    # Results Section
    st.header("Results")

    # Market penetration and calculation details
    create_formula_and_assumptions_expander(
        "Market Penetration Details",
        f"Market Penetration = (Treated Patients / Diagnosed Patients) × Adoption Rate\n= ({treated_patients:,} / {diagnosed_patients:,}) × {adoption_rate}% = {penetration.penetration}%",
        f"This formula estimates what percentage of the eligible patient population will use your drug. Your calculated penetration is {penetration.penetration}% based on a treatment rate of {(penetration.treatment_rate if diagnosed_patients > 0 else 0):.1f}% and adoption rate of {adoption_rate}%.",
        f"""
        - Treatment Rate: {(penetration.treatment_rate if diagnosed_patients > 0 else 0):.1f}% of diagnosed patients currently receive treatment
        - Adoption Rate: {adoption_rate}% of patients receiving treatment are expected to use your product
        - Effective Patient Population: {penetration.effective_patients:,} patients
        - Market penetration assumes your product follows existing treatment patterns
        """,
        expanded=False,
    )

    # Display Market Penetration
    st.metric(
        "Market Penetration",
        f"{penetration.penetration}%",
        help="Calculated based on treatment patterns and adoption rate",
    )

    # Launch Price Results
    st.subheader("Launch Price Results")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Recommended Launch Price Per Patient",
            f"${int(results.launch_price):,}",
            help="Price per patient based on expected market penetration",
        )

        st.metric(
            "Total Disease Market Value",
            f"${results.total_disease_market_value}M",
            help="Total market for this disease (all patients)",
        )

        st.metric(
            "Your Market Revenue",
            f"${results.your_market_revenue:.1f}M",
            help=f"Your revenue based on your market penetration ({penetration.penetration}%)",
        )

    with col2:
        st.metric(
            "Adjusted Market Value",
            f"${results.adjusted_market_value:.1f}M",
            help="Disease market adjusted for order of entry",
        )

        st.metric(
            "Effective Patients",
            f"{int(results.effective_patients):,}",
            help="Based on market penetration",
        )

        st.metric(
            "General Price Per Patient",
            f"${int(results.general_price):,}",
            help="Price per patient if all estimated patients used the treatment",
        )

    # Price calculation details (full width)
    create_formula_and_assumptions_expander(
        "Price Calculation Details",
        f"""Launch Price = (Adjusted Market Value × 1,000,000) ÷ Effective Patients 
        = (${results.adjusted_market_value:.1f}M × 1,000,000) ÷ {int(results.effective_patients):,} 
        = ${int(results.launch_price):,}""",
        "The launch price is calculated by converting the adjusted market value to dollars and dividing by the effective patient population based on market penetration.",
        f"""
        - Market Value: ${results.total_disease_market_value}M
        - Order Entry Multiplier: {calculate_order_multiplier(order_of_entry).multiplier} ({order_of_entry} to market)
        - Adjusted Market Value: ${results.adjusted_market_value:.1f}M
        - Effective Patients: {int(results.effective_patients):,}
        - The adjustment for order of entry accounts for reduced market opportunity for later entrants
        - Price is expressed as cost per patient per year
        """,
        expanded=False,
    )

    # Create visualization
    if results.effective_patients > 0:
        st.subheader("Price Comparison")
        data = pd.DataFrame(
            {
                "Price Type": ["Launch Price", "General Price", "Adoption-Based Price"],
                "Price ($)": [
                    results.launch_price,
                    results.general_price,
                    results.foreseen_adoption_price,
                ],
            }
        )

        fig = px.bar(
            data,
            x="Price Type",
            y="Price ($)",
            title="Price Comparison",
            color="Price Type",
            color_discrete_sequence=["#4C51BF", "#48BB78", "#ED8936"],
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Price comparison explanation
        create_formula_and_assumptions_expander(
            "Price Comparison Explanation",
            f"""Launch Price: ${int(results.launch_price):,}
General Price: ${int(results.general_price):,}
Adoption-Based Price: ${int(results.foreseen_adoption_price):,}""",
            "The difference between these prices reflects how market penetration and adoption assumptions affect pricing strategy.",
            f"""
            - **Launch Price**: Price based on your market penetration of {penetration.penetration}%
            - **General Price**: Price if all estimated patients ({inputs.estimated_patients:,}) used your treatment
            - **Adoption-Based Price**: Price based solely on your adoption rate ({inputs.adoption_rate}%) without considering current treatment patterns
            
            Higher market penetration results in a lower price point but potentially higher total revenue.
            """,
            expanded=False,
        )


# Run the page
launch_price_calculator_page()
