import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

def app():
    """
    Customized Dashboard with additional metrics for All Projects by Spend table
    """
    st.title("Chemical Spend by Project Analysis - Enhanced View")

    # Get datasets directly from session state
    po_data = st.session_state.po_data if 'po_data' in st.session_state else None
    non_po_data = st.session_state.non_po_data if 'non_po_data' in st.session_state else None

    # Check if any data is loaded
    if po_data is None and non_po_data is None:
        st.info("Please upload data on the home page to use this dashboard.")
        return

    # Create tabs
    tab1, tab2 = st.tabs(["PO Analysis", "Non-PO Analysis"])

    with tab1:
        if po_data is not None:
            display_enhanced_po_metrics(po_data)
        else:
            st.info("No PO Line Detail data available. Please upload a PO Line Detail report on the home page.")

    with tab2:
        if non_po_data is not None:
            display_non_po_metrics(non_po_data)
        else:
            st.info("No Non-PO Invoice data available. Please upload a Non-PO Invoice Chemical GL report on the home page.")

def display_enhanced_po_metrics(df):
    """Display enhanced metrics specific to PO Line Detail data with additional count columns"""
    if df is None or len(df) == 0:
        st.info("No PO Line Detail data available.")
        return

    st.header("PO Line Detail Analysis - Enhanced View")
    
    # Add date range information
    if 'Date' in df.columns:
        min_date = df['Date'].min().strftime('%Y-%m-%d') if not pd.isna(df['Date'].min()) else "Unknown"
        max_date = df['Date'].max().strftime('%Y-%m-%d') if not pd.isna(df['Date'].max()) else "Unknown"
        st.write(f"**Report Period:** {min_date} to {max_date}")

    # PO Metrics containers - Expanded for separate metrics
    col1, col2, col3, col4 = st.columns(4)

    # Debug info about the dataframe
    print(f"DEBUG - DataFrame shape: {df.shape}")
    if 'Type: Purchase Order' in df.columns:
        print(f"DEBUG - Types in dataframe: {df['Type: Purchase Order'].value_counts().to_dict()}")

    # Calculate total metrics (for all records)
    total_po_spend = df['Total_Cost'].sum() if 'Total_Cost' in df.columns else 0
    po_count = len(df['Order_ID'].unique())
    avg_po_value = total_po_spend / po_count if po_count > 0 else 0

    # Extract the actual order type values from the dataframe
    order_types = df['Type: Purchase Order'].value_counts().index.tolist() if 'Type: Purchase Order' in df.columns else []
    print(f"DEBUG - Actual order types in dataframe: {order_types}")

    # Find which value represents catalog vs free text
    catalog_type = None
    free_text_type = None

    for order_type in order_types:
        if 'catalog' in str(order_type).lower():
            catalog_type = order_type
        elif 'free' in str(order_type).lower():
            free_text_type = order_type

    print(f"DEBUG - Identified catalog_type: {catalog_type}")
    print(f"DEBUG - Identified free_text_type: {free_text_type}")

    # Filter based on the exact values we found
    if catalog_type and 'Type: Purchase Order' in df.columns:
        catalog_df = df[df['Type: Purchase Order'] == catalog_type]
    else:
        catalog_df = pd.DataFrame(columns=df.columns)  # Empty dataframe with same columns

    if free_text_type and 'Type: Purchase Order' in df.columns:
        free_text_df = df[df['Type: Purchase Order'] == free_text_type]
    else:
        free_text_df = pd.DataFrame(columns=df.columns)  # Empty dataframe with same columns

    # Calculate metrics using the filtered dataframes
    catalog_spend = catalog_df['Total_Cost'].sum() if len(catalog_df) > 0 else 0
    catalog_count = len(catalog_df['Order_ID'].unique()) if len(catalog_df) > 0 else 0
    avg_catalog_value = catalog_spend / catalog_count if catalog_count > 0 else 0

    free_text_spend = free_text_df['Total_Cost'].sum() if len(free_text_df) > 0 else 0
    free_text_count = len(free_text_df['Order_ID'].unique()) if len(free_text_df) > 0 else 0
    avg_free_text_value = free_text_spend / free_text_count if free_text_count > 0 else 0

    # Debug information about the filtered data
    print(f"DEBUG - Catalog records: {len(catalog_df)}, spend: ${catalog_spend:,.2f}")
    print(f"DEBUG - Free Text records: {len(free_text_df)}, spend: ${free_text_spend:,.2f}")

    # Calculate percentages
    catalog_percentage = (catalog_spend / total_po_spend * 100) if total_po_spend > 0 else 0
    free_text_percentage = (free_text_spend / total_po_spend * 100) if total_po_spend > 0 else 0
    catalog_count_pct = (catalog_count / po_count * 100) if po_count > 0 else 0

    # Display the metrics in the columns
    with col1:
        st.metric("Total PO Spend", f"${total_po_spend:,.2f}")
        st.metric("Total PO Count", str(po_count))
        st.metric("Average PO Value", f"${avg_po_value:,.2f}")

    with col2:
        st.metric("Catalog Spend", f"${catalog_spend:,.2f}")
        st.metric("Catalog PO Count", str(catalog_count))
        st.metric("Avg Catalog PO Value", f"${avg_catalog_value:,.2f}")

    with col3:
        st.metric("Free Text Spend", f"${free_text_spend:,.2f}")
        st.metric("Free Text PO Count", str(free_text_count))
        st.metric("Avg Free Text PO Value", f"${avg_free_text_value:,.2f}")

    with col4:
        # Display percentage metrics
        st.metric("Catalog Spend %", f"{catalog_percentage:.1f}%")
        st.metric("Free Text Spend %", f"{free_text_percentage:.1f}%")
        st.metric("Catalog Count %", f"{catalog_count_pct:.1f}%")

    # Add KPI target tracking for Catalog Purchase Orders
    if 'Type: Purchase Order' in df.columns:
        st.subheader("Catalog Purchase Orders Target")
        st.write("Progress towards 100% Catalog Purchase Orders")

        # Create columns for progress and gauge
        prog_col1, prog_col2 = st.columns([3, 2])
        
        with prog_col1:
            # Create progress bar
            st.progress(min(catalog_percentage / 100, 1.0))
            
            # Display current state
            st.write(f"**Current: {catalog_percentage:.1f}%** Catalog Purchase Orders ({catalog_count} out of {po_count} POs)")
            st.write(f"**Target Gap: {100 - catalog_percentage:.1f}%** ({free_text_count} orders to convert from Free Text to Catalog)")
            
        with prog_col2:
            # Create gauge chart for catalog percentage with water treatment theme colors
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=catalog_percentage,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "% Catalog Orders", 'font': {'color': '#003049', 'size': 16}},
                number={'font': {'color': '#0077B6', 'size': 24}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#003049'},
                    'bar': {'color': "#0077B6"},  # Ocean blue
                    'bgcolor': "#E0F2F1",  # Light teal
                    'borderwidth': 2,
                    'bordercolor': "#003049",  # Deep navy
                    'steps': [
                        {'range': [0, 20], 'color': '#CAF0F8'},   # Lightest blue
                        {'range': [20, 40], 'color': '#90E0EF'},  # Light blue
                        {'range': [40, 60], 'color': '#48CAE4'},  # Medium blue
                        {'range': [60, 80], 'color': '#00B4D8'},  # Blue
                        {'range': [80, 100], 'color': '#0077B6'}  # Deep blue
                    ],
                    'threshold': {
                        'line': {'color': "#2A9D8F", 'width': 4},  # Teal
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ))
            
            # Update the layout
            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
            )
            
            st.plotly_chart(fig, use_container_width=True, key="catalog_gauge_chart")

        # Order count visualization
        order_type_data = pd.DataFrame({
            'Order Type': ['Catalog', 'Free Text'],
            'Count': [catalog_count, free_text_count]
        })
        
        # Create pie chart with water treatment theme colors
        fig_count = px.pie(
            order_type_data,
            values='Count',
            names='Order Type',
            title='Order Type Distribution (Count)',
            color='Order Type',
            color_discrete_sequence=['#0077B6', '#2A9D8F']  # Ocean blue for Catalog, Teal for Free Text
        )
        fig_count.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(color='white', size=14)
        )
        fig_count.update_layout(
            title_font=dict(color='#003049', size=16),
            legend=dict(font=dict(color='#003049'))
        )
        st.plotly_chart(fig_count, use_container_width=True, key="order_type_count_pie")
        
