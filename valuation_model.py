import pandas as pd

# Create a Pandas Excel writer using the XlsxWriter engine.
with pd.ExcelWriter("Pharma_Valuation_Model.xlsx", engine="xlsxwriter") as writer:
    
    # 1. Dashboard: Key metrics summary
    dashboard_data = {
        "Metric": ["NPV", "IRR", "Payback Period"],
        "Value": ["=IFERROR(DCF!D7, 0)", "=IFERROR(DCF!D8, 0)", "=IFERROR(DCF!D9, 0)"]
    }
    dashboard_df = pd.DataFrame(dashboard_data)
    dashboard_df.to_excel(writer, sheet_name="Dashboard", index=False)
    
    # 2. Assumptions: Input values for the model
    assumptions_data = {
        "Assumption": ["Clinical Probability", "Time to Market (years)", "Peak Annual Sales ($M)", "Discount Rate (%)"],
        "Value": [0.70, 3, 500, 10]
    }
    assumptions_df = pd.DataFrame(assumptions_data)
    assumptions_df.to_excel(writer, sheet_name="Assumptions", index=False)
    
    # 3. Revenue Forecast: Simple revenue projection with a sample formula
    revenue_data = {
        "Year": [2025, 2026, 2027, 2028, 2029],
        "Projected Revenue ($M)": [
            "=Assumptions!$C$2 * (1 + 0.2)^(A2 - Assumptions!$B$2)",  # Example: ramp-up formula
            None, None, None, None
        ]
    }
    revenue_df = pd.DataFrame(revenue_data)
    revenue_df.to_excel(writer, sheet_name="Revenue", index=False)
    
    # 4. Cost Structure: Example breakdown of costs
    costs_data = {
        "Year": [2025, 2026, 2027, 2028, 2029],
        "R&D Costs ($M)": [100, 50, 30, 20, 10],
        "Marketing Costs ($M)": [20, 30, 40, 50, 60]
    }
    costs_df = pd.DataFrame(costs_data)
    costs_df.to_excel(writer, sheet_name="Costs", index=False)
    
    # 5. DCF Calculation: Discounted Cash Flow basics
    dcf_data = {
        "Year": [2025, 2026, 2027, 2028, 2029],
        "Cash Flow ($M)": [50, 100, 150, 200, 250],
        "Discount Factor": [
            "=1/(1 + Assumptions!$D$2)^(A2 - Assumptions!$B$2)", None, None, None, None
        ],
        "Discounted Cash Flow": [
            "=B2 * C2", None, None, None, None
        ]
    }
    dcf_df = pd.DataFrame(dcf_data)
    dcf_df.to_excel(writer, sheet_name="DCF", index=False)
    
    # 6. Sensitivity Analysis: Test key assumptions
    sensitivity_data = {
        "Parameter": ["Discount Rate", "Clinical Probability", "Peak Sales"],
        "Base Value": [10, 70, 500],
        "Low": [8, 60, 450],
        "High": [12, 80, 550]
    }
    sensitivity_df = pd.DataFrame(sensitivity_data)
    sensitivity_df.to_excel(writer, sheet_name="Sensitivity Analysis", index=False)
    
    # 7. Notes & Documentation: Instructions and change log
    notes_data = {
        "Section": ["Assumptions", "Revenue", "Costs", "DCF", "Sensitivity"],
        "Instructions": [
            "Enter key input assumptions. Use a consistent color for inputs (e.g., light blue).",
            "Link revenue forecast to assumptions. Update formulas as necessary.",
            "Detail fixed and variable costs; include R&D and marketing costs separately.",
            "Apply discount factors to cash flows to calculate DCF. Adjust formulas if needed.",
            "Test sensitivity of key metrics (NPV, IRR) by varying assumptions."
        ]
    }
    notes_df = pd.DataFrame(notes_data)
    notes_df.to_excel(writer, sheet_name="Notes", index=False)

print("Pharma_Valuation_Model.xlsx has been created!")
