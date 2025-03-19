import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Pharma Business Valuation & Strategy Suite",
    page_icon="💊",
    layout="wide",
)

from utils.state import initialize_session_state
from components.ui_components import display_header
from sections.npv_calculator import npv_calculator_page
from sections.deal_analysis import deal_analysis_page
from sections.strategic_decision import strategic_decision_page


def main_page():
    # Display header
    display_header()

    # Use tabs for main navigation
    tabs = st.tabs(["NPV Calculator 📊", "Deal Analysis 🤝", "Strategic Decision 🎯"])

    # Display appropriate page based on selected tab
    with tabs[0]:
        npv_calculator_page()

    with tabs[1]:
        deal_analysis_page()

    with tabs[2]:
        strategic_decision_page()

    # Footer
    st.markdown("---")
    st.markdown("**Pharma Business Valuation & Strategy Suite** - Built by Tuğçe")


# Initialize session state
initialize_session_state()

# Set up pages
home_page = st.Page(main_page, title="Asset Valuation", icon="💊", default=True)
launch_price_page = st.Page("pages/2_Launch_Price.py", title="Launch Price", icon="💰")
about_page = st.Page("pages/1_About.py", title="About", icon="ℹ️")

# Configure navigation
pg = st.navigation([home_page, launch_price_page, about_page], position="sidebar")

# Run the selected page
pg.run()
