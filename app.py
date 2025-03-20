import streamlit as st
from typing import Callable, Optional

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


def with_error_handling(func: Callable) -> Callable:
    """Decorator to add error handling to page functions.

    Args:
        func: The page function to wrap with error handling

    Returns:
        Wrapped function with error handling
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please check your inputs and try again.")
            # Optional: add logging here

    return wrapper


def main_page() -> None:
    """Display the main application page with navigation tabs and content."""
    # Display header
    display_header()

    # Use tabs for main navigation
    tabs = st.tabs(["NPV Calculator 📊", "Deal Analysis 🤝", "Strategic Decision 🎯"])

    # Display appropriate page based on selected tab
    with tabs[0]:
        with_error_handling(npv_calculator_page)()

    with tabs[1]:
        with_error_handling(deal_analysis_page)()

    with tabs[2]:
        with_error_handling(strategic_decision_page)()

    # Footer
    display_footer()


def display_footer() -> None:
    """Display the application footer with credits and information."""
    st.markdown("---")
    st.markdown("**Pharma Business Valuation & Strategy Suite** - Built by Tuğçe")

    # Add version information
    st.sidebar.caption("Version 1.0")


def run_app():
    """Main entry point for the application."""
    try:
        # Initialize session state
        initialize_session_state()

        # Set up pages
        home_page = st.Page(main_page, title="Asset Valuation", icon="💊", default=True)
        launch_price_page = st.Page(
            "app_pages/2_Launch_Price.py", title="Launch Price", icon="💰"
        )
        about_page = st.Page("app_pages/1_About.py", title="About", icon="ℹ️")

        # Configure navigation
        pg = st.navigation(
            [home_page, launch_price_page, about_page], position="sidebar"
        )

        # Run the selected page
        pg.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please restart the application or contact support.")


# Run the application
run_app()
