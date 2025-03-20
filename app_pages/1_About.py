import streamlit as st
from typing import NoReturn


def display_about_page() -> NoReturn:
    """Display the About page for the Pharma Business Valuation & Strategy Suite.

    This function creates a static page that provides an overview of the application's
    features and functionality. It includes sections on:
    - Main capabilities and use cases
    - Instructions for using different modules
    - Detailed feature descriptions
    - Key terminology and definitions
    - Version information

    The function uses Streamlit's markdown and layout components to create
    a well-structured, informative page.

    Returns:
        NoReturn: Function modifies Streamlit's UI state directly
    """
    st.title("About the Pharma Business Valuation & Strategy Suite")

    st.markdown(
        """
        This comprehensive suite helps pharmaceutical companies and investors with:
        
        - Net Present Value (NPV) calculations across development stages 📊
        - Reasonable deal terms for licensing/partnerships 🤝
        - Strategic decisions between development vs. out-licensing 🎯
        - Launch price optimization and market penetration analysis 💰
        
        ## How to Use
        
        1. Start with NPV Calculator to assess basic asset value
        2. Use Deal Analysis to evaluate potential partnerships
        3. Explore Strategic Decision to compare options
        4. Optimize Launch Price based on market dynamics
        
        ## Key Features
        
        ### NPV & Deal Analysis
        - Risk-adjusted NPV calculations
        - Clinical phase success probabilities
        - Deal structure evaluation
        - Partnership terms analysis
        
        ### Strategic Decision Making
        - Development vs. licensing comparison
        - Risk-return trade-off analysis
        - Resource allocation guidance
        
        ### Launch Price Optimization
        - Market size and penetration analysis
        - Order-of-entry impact assessment
        - Patient population segmentation
        - Adoption rate considerations
        
        ## Legend
        
        - **NPV:** Net Present Value
        - **Phase 1-3:** Clinical trial phases
        - **Registration:** Regulatory approval phase
        - **Market Penetration:** Expected market share
        - **Adoption Rate:** Expected usage by target population
        
        ## Version Information
        
        Current Version: 1.0.0
        """
    )


# Run the page
display_about_page()
