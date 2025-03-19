import streamlit as st
import pandas as pd
import plotly.express as px


def get_order_multiplier(order_of_entry):
    """Calculate the order of entry multiplier."""
    multipliers = {
        "first": 1.0,  # 100% for first-in-class
        "second": 0.67,  # 67% for second-in-class
        "third": 0.5,  # 50% for third-in-class
        "later": 0.3,  # 30% for later entrants
    }
    return multipliers.get(order_of_entry, 1.0)


def calculate_market_penetration(treated_patients, diagnosed_patients, adoption_rate):
    """Calculate market penetration based on inputs."""
    if diagnosed_patients == 0:
        return 0
    treatment_rate = treated_patients / diagnosed_patients
    penetration = treatment_rate * (adoption_rate / 100)
    return min(max(round(penetration * 100), 0), 100)


def calculate_launch_price(inputs, penetration):
    """Calculate launch price and related metrics."""
    order_multiplier = get_order_multiplier(inputs["order_of_entry"])

    # Total disease market value
    total_disease_market_value = inputs["market_value"]

    # Adjusted market value based on order of entry
    adjusted_market_value = total_disease_market_value * order_multiplier

    # Calculate effective patients
    effective_patients = inputs["estimated_patients"] * (penetration / 100)

    # Calculate foreseen adoption patients
    foreseen_adoption_patients = inputs["estimated_patients"] * (
        inputs["adoption_rate"] / 100
    )

    # Calculate general price (if all patients used the treatment)
    general_price = (
        (adjusted_market_value * 1_000_000) / inputs["estimated_patients"]
        if inputs["estimated_patients"] > 0
        else 0
    )

    # Calculate price for foreseen adopted patients
    foreseen_adoption_price = (
        (adjusted_market_value * 1_000_000) / foreseen_adoption_patients
        if foreseen_adoption_patients > 0
        else 0
    )

    # Calculate launch price
    launch_price = (
        (adjusted_market_value * 1_000_000) / effective_patients
        if effective_patients > 0
        else 0
    )

    # Calculate your market revenue
    your_market_revenue = (penetration / 100) * adjusted_market_value

    return {
        "launch_price": launch_price,
        "total_disease_market_value": total_disease_market_value,
        "adjusted_market_value": adjusted_market_value,
        "effective_patients": effective_patients,
        "general_price": general_price,
        "foreseen_adoption_price": foreseen_adoption_price,
        "foreseen_adoption_patients": foreseen_adoption_patients,
        "your_market_revenue": your_market_revenue,
    }


def display_price_terminology():
    """Display the price terminology guide."""
    with st.expander("💡 Price Terminology Guide", expanded=True):
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


def display_adoption_rate_help():
    """Display adoption rate help information."""
    with st.expander("📊 How to determine Adoption Rate?"):
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


def display_formulas():
    """Display the formulas used in calculations."""
    with st.expander("📐 Formulas Used"):
        st.markdown(
            """
        ### Market Penetration
        ```
        Market Penetration = (Treated Patients / Diagnosed Patients) × Adoption Rate
        ```
        This formula estimates what percentage of the eligible patient population will use your drug based on current treatment patterns and your product's adoption rate.
        
        ### Launch Price
        ```
        Launch Price = (Market Value × Order Entry Multiplier × 1,000,000) / (Estimated Patients × Market Penetration %)
        ```
        The 1,000,000 multiplier converts the market value from millions of dollars to dollars, giving you the price per patient.
        
        ### Market Value vs Your Revenue
        - **Total Disease Market Value** represents the entire market for this disease (all patients)
        - **Your Market Revenue** is what you'll capture based on your market penetration
        """
        )


def display_assumptions():
    """Display key assumptions."""
    with st.expander("🎯 Key Assumptions"):
        st.markdown(
            """
        - The overall market value represents the total addressable market in millions of dollars
        - Order of entry impacts market value: 1st (100%), 2nd (67%), 3rd (50%), Later (30%)
        - Diagnosed patients represent the total diagnosed population with the condition
        - Treated patients represent those currently receiving any treatment for the condition
        - Adoption rate represents the percentage of eligible patients expected to adopt your specific treatment
        - Market penetration calculation assumes similar treatment patterns to current standards
        - The price calculation assumes a single price point across all patient segments
        """
        )


def launch_price_calculator_page():
    st.title("💰 Launch Price Calculator")
    st.markdown("Calculate optimal pricing based on market size and penetration")

    # Display price terminology guide
    display_price_terminology()

    # Input Parameters
    st.header("Input Parameters")

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

    # Display adoption rate help
    display_adoption_rate_help()

    # Toggle switches for formulas and assumptions
    col1, col2 = st.columns(2)
    with col1:
        show_formulas = st.toggle("Show Formulas", value=False)
    with col2:
        show_assumptions = st.toggle("Show Assumptions", value=False)

    if show_formulas:
        display_formulas()

    if show_assumptions:
        display_assumptions()

    # Calculate results
    inputs = {
        "market_value": market_value,
        "order_of_entry": order_of_entry,
        "estimated_patients": estimated_patients,
        "diagnosed_patients": diagnosed_patients,
        "treated_patients": treated_patients,
        "adoption_rate": adoption_rate,
    }

    penetration = calculate_market_penetration(
        treated_patients, diagnosed_patients, adoption_rate
    )
    results = calculate_launch_price(inputs, penetration)

    # Display Market Penetration
    st.metric(
        "Market Penetration",
        f"{penetration}%",
        help="Calculated based on treatment patterns and adoption rate",
    )

    if show_formulas:
        st.code(
            f"""
        Calculation: ({treated_patients:,} / {diagnosed_patients:,}) × {adoption_rate}% = {penetration}%
        Treatment Rate: {(treated_patients / diagnosed_patients * 100 if diagnosed_patients > 0 else 0):.1f}%
        """
        )

    # Results Section
    st.header("Launch Price Results")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Recommended Launch Price Per Patient",
            f"${int(results['launch_price']):,}",
            help="Price per patient based on expected market penetration",
        )

        st.metric(
            "Total Disease Market Value",
            f"${results['total_disease_market_value']}M",
            help="Total market for this disease (all patients)",
        )

        st.metric(
            "Your Market Revenue",
            f"${results['your_market_revenue']:.1f}M",
            help=f"Your revenue based on your market penetration ({penetration}%)",
        )

    with col2:
        st.metric(
            "Adjusted Market Value",
            f"${results['adjusted_market_value']:.1f}M",
            help="Disease market adjusted for order of entry",
        )

        st.metric(
            "Effective Patients",
            f"{int(results['effective_patients']):,}",
            help="Based on market penetration",
        )

        st.metric(
            "General Price Per Patient",
            f"${int(results['general_price']):,}",
            help="Price per patient if all estimated patients used the treatment",
        )

    # Create visualization
    if results["effective_patients"] > 0:
        data = pd.DataFrame(
            {
                "Price Type": ["Launch Price", "General Price", "Adoption-Based Price"],
                "Price ($)": [
                    results["launch_price"],
                    results["general_price"],
                    results["foreseen_adoption_price"],
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


# Run the page
launch_price_calculator_page()
