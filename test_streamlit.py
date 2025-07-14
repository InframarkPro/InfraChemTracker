import streamlit as st
import pandas as pd
import numpy as np

st.title("Currency Formatting Test")
st.write("This test demonstrates consistent currency formatting across different display methods.")

# Create sample data
data = {
    'Supplier': ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 'Supplier E'],
    'Chemical': ['Sodium Hypochlorite', 'Sodium Hydroxide', 'Ferric Chloride', 'Polymer', 'Sulfuric Acid'],
    'Quantity': [150.5, 75.2, 200.0, 45.7, 120.3],
    'Total_Cost': [12345.67, 8765.43, 20543.21, 5432.10, 15876.54],
    'Unit_Price': [82.03, 116.56, 102.72, 118.86, 131.97]
}

df = pd.DataFrame(data)

# Create a formatter function for currency
def format_currency(value):
    """Format a numeric value as currency with dollar sign"""
    if pd.isna(value):
        return ""
    return f"${value:,.2f}"

# Show raw table first
st.subheader("Raw Data")
st.dataframe(df)

# Show table with formatted currency
st.subheader("Formatted Currency")
display_df = df.copy()
display_df['Total_Cost_Formatted'] = display_df['Total_Cost'].apply(format_currency)
display_df['Unit_Price_Formatted'] = display_df['Unit_Price'].apply(format_currency)
st.dataframe(display_df)

# Using column config
st.subheader("Using Column Config")
st.dataframe(
    df,
    column_config={
        "Total_Cost": st.column_config.NumberColumn(
            "Total Cost",
            help="Total cost with currency formatting",
            format="$%,.2f"
        ),
        "Unit_Price": st.column_config.NumberColumn(
            "Unit Price",
            help="Unit price with currency formatting",
            format="$%,.2f"
        )
    }
)

# Show metric cards
st.subheader("Metric Cards")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Spend", f"${df['Total_Cost'].sum():,.2f}")
with col2:
    st.metric("Average Unit Price", f"${df['Unit_Price'].mean():,.2f}")
with col3:
    st.metric("Total Quantity", f"{df['Quantity'].sum():,.1f}")