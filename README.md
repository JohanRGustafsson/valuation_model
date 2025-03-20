# Pharma Business Valuation & Strategy Suite

A Streamlit application for pharmaceutical asset valuation and deal analysis. This application helps calculate the Net Present Value (NPV) of pharmaceutical assets at different clinical development stages and analyze potential deal structures.

## Features

- NPV calculation for pharmaceutical assets
- Risk adjustment based on clinical stage probabilities
- Time value adjustment using discount rates
- Order of entry market position adjustments
- R&D cost considerations
- Deal value and ownership analysis
- Visualization of ownership structure
- Launch price calculator
- Strategic decision analysis

## Project Structure

```
├── app.py                 # Main application entry point
├── requirements.txt       # Project dependencies
├── app_pages/             # Additional pages
│   ├── 1_About.py
│   └── 2_Launch_Price.py
├── components/            # Reusable UI components
│   └── ui_components.py
├── sections/              # Main application sections
│   ├── deal_analysis.py
│   ├── npv_calculator.py
│   └── strategic_decision.py
└── utils/                 # Utility modules
    ├── calculations.py    # Business logic and calculations
    └── state.py           # State management
```

## Core Design Principles

- **Separation of Concerns**: UI components are separated from business logic
- **Consistent UI Patterns**: Reusable components for consistent look and feel
- **Error Handling**: Robust error handling throughout the application
- **Type Safety**: Type annotations and validation of inputs
- **Code Reusability**: Shared components and utility functions

## Local Development with Conda

For local development, you can use Conda to create an isolated environment:

1. Create a new conda environment:
   ```
   conda create -n valuation-model python=3.9 -c conda-forge streamlit pandas plotly
   ```

2. Activate the environment:
   ```
   conda activate valuation-model
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   streamlit run app.py
   ```

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

The application consists of several sections:

1. **NPV Calculator**: Calculate the Net Present Value of a pharmaceutical asset
   - Enter launch value, order of entry, and discount rate
   - Set success probabilities for each clinical phase
   - Adjust R&D and clinical costs
   - View calculated NPV values for each phase

2. **Deal Analysis**: Analyze partnership deals and ownership structure
   - Select deal stage and parameters
   - Visualize ownership distribution
   - Evaluate deal fairness

3. **Strategic Decision**: Compare continued development vs. out-licensing
   - Evaluate financial impact of different strategic options
   - Receive data-driven recommendations

4. **Launch Price Calculator**: Determine optimal pricing strategy
   - Calculate prices based on market size and penetration
   - Visualize price comparisons

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 