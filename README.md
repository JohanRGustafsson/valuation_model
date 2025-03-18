# Pharma Asset Valuation Calculator

A Streamlit application for pharmaceutical asset valuation and deal analysis. This application helps calculate the Net Present Value (NPV) of pharmaceutical assets at different clinical development stages and analyze potential deal structures.

## Features

- NPV calculation for pharmaceutical assets
- Risk adjustment based on clinical stage probabilities
- Time value adjustment using discount rates
- Order of entry market position adjustments
- R&D cost considerations
- Deal value and ownership analysis
- Visualization of ownership structure

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Enter the launch value, order of entry, and discount rate
2. Toggle whether to include R&D costs in the NPV calculation
3. Adjust success probabilities for each clinical phase
4. Set R&D and clinical costs for each phase
5. Select the deal stage and parameters
6. View the calculated NPV values and deal analysis

The application provides toggleable views for model assumptions and calculation formulas to understand the valuation methodology. 