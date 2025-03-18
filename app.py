import streamlit as st
from utils.state import initialize_session_state
from components.ui_components import display_header
from pages.npv_calculator import npv_calculator_page
from pages.deal_analysis import deal_analysis_page
from pages.strategic_decision import strategic_decision_page

# Set page configuration
st.set_page_config(
    page_title="Pharma Asset Valuation Calculator",
    page_icon="💊",
    layout="wide",
)

# Initialize session state
initialize_session_state()

# Display header
display_header()

# Use tabs for main navigation
tabs = st.tabs(["NPV Calculator", "Deal Analysis", "Strategic Decision"])

# Display appropriate page based on selected tab
with tabs[0]:
    npv_calculator_page()

with tabs[1]:
    deal_analysis_page()

with tabs[2]:
    strategic_decision_page()

# Footer
st.markdown("---")
st.markdown("**Pharma Asset Valuation Calculator** - Built with Streamlit")

# Add app info in sidebar
with st.sidebar:
    st.title("About")
    st.markdown(
        """
    ## Pharma Asset Valuation Tool
    
    This application helps pharmaceutical companies and investors evaluate:
    
    - Net Present Value (NPV) across development stages
    - Reasonable deal terms for licensing/partnerships
    - Strategic decisions between development vs. out-licensing
    
    ### How to Use
    
    1. Start with NPV Calculator to assess basic asset value
    2. Use Deal Analysis to evaluate potential partnerships
    3. Explore Strategic Decision to compare options
    
    ### Legend
    
    - **NPV:** Net Present Value
    - **Phase 1-3:** Clinical trial phases
    - **Registration:** Regulatory approval phase
    """
    )

    st.markdown("---")

    # Add app settings
    st.subheader("Settings")

    # Theme toggle (just for demonstration as Streamlit doesn't support runtime theme changes)
    st.selectbox(
        "Color Theme",
        ["Light", "Dark"],
        index=0,
        disabled=True,
        help="Theme changes require app restart",
    )

    # Version info
    st.caption("Version 1.0.0")
