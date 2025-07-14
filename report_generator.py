"""
Dashboard Report Generator

This module provides utilities for generating dashboard metrics and visualizations
for the Chemical Dashboard data.
"""

import os
import datetime
import logging
from typing import Dict, List, Optional, Union

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# Configure logging
logger = logging.getLogger(__name__)

def get_color_palette(n: int) -> List[str]:
    """
    Get color palette for charts
    
    Args:
        n: Number of colors needed
        
    Returns:
        List of color hex values
    """
    # Primary color palette for Matrix theme (green shades)
    matrix_colors = [
        '#00FF00',  # Bright green
        '#00CC00',  # Medium green
        '#009900',  # Dark green
        '#99FF99',  # Light green
        '#66FF66',  # Pale green
        '#33FF33',  # Bright light green
        '#CCFFCC',  # Very pale green
        '#003300',  # Very dark green
        '#006600',  # Deep green
        '#00FF33',  # Bright lime green
        '#00FF66',  # Mint green
        '#00FF99',  # Sea green
        '#00FFCC',  # Aqua green
        '#33FF00',  # Yellow green
        '#66FF00',  # Lime green
    ]
    
    # Ensure we have enough colors
    if n <= len(matrix_colors):
        return matrix_colors[:n]
    
    # If we need more colors, repeat the palette
    return (matrix_colors * (n // len(matrix_colors) + 1))[:n]

def format_currency(value) -> str:
    """Format a numeric value as currency with dollar sign"""
    if pd.isna(value):
        return "$0.00"
    return f"${float(value):,.2f}"

def format_percentage(value, decimals=1) -> str:
    """Format a numeric value as percentage"""
    if pd.isna(value):
        return "0.0%"
    return f"{float(value):.{decimals}f}%"

def format_number(value) -> str:
    """Format a numeric value with comma separators"""
    if pd.isna(value):
        return "0"
    return f"{int(value):,}"

def generate_dashboard_metrics(df: pd.DataFrame) -> Dict[str, Union[float, int, str]]:
    """
    Generate dashboard metrics from dataset
    
    Args:
        df: DataFrame with dashboard data
        
    Returns:
        Dictionary of metrics values
    """
    metrics = {}
    
    # Basic count metrics
    metrics["Total Records"] = len(df)
    
    # Cost metrics if available
    if 'Total_Cost' in df.columns:
        total_cost = df['Total_Cost'].sum()
        metrics["Total Cost"] = total_cost
    
    # Region metrics if available
    if 'Region' in df.columns:
        region_count = df['Region'].nunique()
        metrics["Region Count"] = region_count
        
        # Get region with highest spend
        if 'Total_Cost' in df.columns:
            region_spend = df.groupby('Region')['Total_Cost'].sum().reset_index()
            if not region_spend.empty:
                top_region = region_spend.sort_values('Total_Cost', ascending=False).iloc[0]
                metrics["Top Region"] = top_region['Region']
                metrics["Top Region Spend"] = top_region['Total_Cost']
                if total_cost > 0:
                    metrics["Top Region Share"] = (top_region['Total_Cost'] / total_cost) * 100
    
    # Invoice/Order metrics if available
    if 'Order_ID' in df.columns:
        invoice_count = df['Order_ID'].nunique()
        metrics["Total Invoice Count"] = invoice_count
    
    # Supplier metrics if available
    if 'Supplier' in df.columns:
        supplier_count = df['Supplier'].nunique()
        metrics["Supplier Count"] = supplier_count
        
        # Get supplier with highest spend
        if 'Total_Cost' in df.columns:
            supplier_spend = df.groupby('Supplier')['Total_Cost'].sum().reset_index()
            if not supplier_spend.empty:
                top_supplier = supplier_spend.sort_values('Total_Cost', ascending=False).iloc[0]
                metrics["Top Supplier"] = top_supplier['Supplier']
                metrics["Top Supplier Spend"] = top_supplier['Total_Cost']
                if total_cost > 0:
                    metrics["Top Supplier Share"] = (top_supplier['Total_Cost'] / total_cost) * 100
    
    # Chemical metrics if available
    if 'Chemical' in df.columns:
        chemical_count = df['Chemical'].nunique()
        metrics["Chemical Count"] = chemical_count
        
        # Get chemical with highest spend
        if 'Total_Cost' in df.columns:
            chemical_spend = df.groupby('Chemical')['Total_Cost'].sum().reset_index()
            if not chemical_spend.empty:
                top_chemical = chemical_spend.sort_values('Total_Cost', ascending=False).iloc[0]
                metrics["Top Chemical"] = top_chemical['Chemical']
                metrics["Top Chemical Spend"] = top_chemical['Total_Cost']
                if total_cost > 0:
                    metrics["Top Chemical Share"] = (top_chemical['Total_Cost'] / total_cost) * 100
    
    return metrics

def generate_chemical_analysis_charts(df: pd.DataFrame) -> List[go.Figure]:
    """
    Generate chemical analysis charts from dataset
    
    Args:
        df: DataFrame with dashboard data
        
    Returns:
        List of Plotly figures
    """
    charts = []
    
    if 'Chemical' not in df.columns or 'Total_Cost' not in df.columns:
        return charts
    
    # Create chemical spend pie chart
    chemical_spend = df.groupby('Chemical')['Total_Cost'].sum().reset_index()
    chemical_spend = chemical_spend.sort_values('Total_Cost', ascending=False)
    
    # Keep top 10 chemicals, group the rest as "Other"
    if len(chemical_spend) > 10:
        top_chemicals = chemical_spend.head(10).copy()
        other_chemicals = pd.DataFrame({
            'Chemical': ['Other Chemicals'],
            'Total_Cost': [chemical_spend.iloc[10:]['Total_Cost'].sum()]
        })
        chemical_spend = pd.concat([top_chemicals, other_chemicals], ignore_index=True)
    
    # Create pie chart
    fig = px.pie(
        chemical_spend,
        names='Chemical',
        values='Total_Cost',
        title='Chemical Spend Distribution',
        color_discrete_sequence=get_color_palette(len(chemical_spend)),
        hole=0.4
    )
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        legend_title_text='Chemical',
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Add to charts list
    charts.append(fig)
    
    # Create chemical spend trend chart if Date column exists
    if 'Date' in df.columns:
        # Convert Date to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Group by month and chemical
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_chemical_spend = df.groupby(['Month', 'Chemical'])['Total_Cost'].sum().reset_index()
        monthly_chemical_spend['Month'] = monthly_chemical_spend['Month'].dt.to_timestamp()
        
        # Get top 5 chemicals by total spend
        top_chemicals = chemical_spend.head(5)['Chemical'].tolist()
        filtered_spend = monthly_chemical_spend[monthly_chemical_spend['Chemical'].isin(top_chemicals)]
        
        # Create line chart
        fig = px.line(
            filtered_spend,
            x='Month',
            y='Total_Cost',
            color='Chemical',
            title='Top 5 Chemicals - Monthly Spend',
            color_discrete_sequence=get_color_palette(len(top_chemicals))
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Total Cost',
            legend_title_text='Chemical',
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        # Format y-axis as currency
        fig.update_yaxes(tickprefix='$', tickformat=',.0f')
        
        # Add to charts list
        charts.append(fig)
    
    return charts

def generate_supplier_analysis_charts(df: pd.DataFrame) -> List[go.Figure]:
    """
    Generate supplier analysis charts from dataset
    
    Args:
        df: DataFrame with dashboard data
        
    Returns:
        List of Plotly figures
    """
    charts = []
    
    if 'Supplier' not in df.columns or 'Total_Cost' not in df.columns:
        return charts
    
    # Create supplier spend bar chart
    supplier_spend = df.groupby('Supplier')['Total_Cost'].sum().reset_index()
    supplier_spend = supplier_spend.sort_values('Total_Cost', ascending=False)
    
    # Keep top 10 suppliers
    supplier_spend = supplier_spend.head(10)
    
    # Create bar chart
    fig = px.bar(
        supplier_spend,
        x='Supplier',
        y='Total_Cost',
        title='Top 10 Suppliers by Spend',
        color='Total_Cost',
        color_continuous_scale=[(0, '#00AA00'), (1, '#00FF00')]
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Supplier',
        yaxis_title='Total Cost',
        xaxis_tickangle=-45,
        margin=dict(l=10, r=10, t=50, b=100),
        height=500
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickprefix='$', tickformat=',.0f')
    
    # Add to charts list
    charts.append(fig)
    
    # Create supplier spend trend chart if Date column exists
    if 'Date' in df.columns:
        # Convert Date to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Group by month and supplier
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_supplier_spend = df.groupby(['Month', 'Supplier'])['Total_Cost'].sum().reset_index()
        monthly_supplier_spend['Month'] = monthly_supplier_spend['Month'].dt.to_timestamp()
        
        # Get top 5 suppliers by total spend
        top_suppliers = supplier_spend.head(5)['Supplier'].tolist()
        filtered_spend = monthly_supplier_spend[monthly_supplier_spend['Supplier'].isin(top_suppliers)]
        
        # Create line chart
        fig = px.line(
            filtered_spend,
            x='Month',
            y='Total_Cost',
            color='Supplier',
            title='Top 5 Suppliers - Monthly Spend',
            color_discrete_sequence=get_color_palette(len(top_suppliers))
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Total Cost',
            legend_title_text='Supplier',
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        # Format y-axis as currency
        fig.update_yaxes(tickprefix='$', tickformat=',.0f')
        
        # Add to charts list
        charts.append(fig)
    
    return charts

def generate_region_analysis_charts(df: pd.DataFrame) -> List[go.Figure]:
    """
    Generate region analysis charts from dataset
    
    Args:
        df: DataFrame with dashboard data
        
    Returns:
        List of Plotly figures
    """
    charts = []
    
    if 'Region' not in df.columns or 'Total_Cost' not in df.columns:
        return charts
    
    # Create region spend pie chart
    region_spend = df.groupby('Region')['Total_Cost'].sum().reset_index()
    region_spend = region_spend.sort_values('Total_Cost', ascending=False)
    
    # Create pie chart
    fig = px.pie(
        region_spend,
        names='Region',
        values='Total_Cost',
        title='Region Spend Distribution',
        color_discrete_sequence=get_color_palette(len(region_spend)),
        hole=0.4
    )
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        legend_title_text='Region',
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Add to charts list
    charts.append(fig)
    
    # Create region spend bar chart
    fig = px.bar(
        region_spend,
        x='Region',
        y='Total_Cost',
        title='Region Spend Comparison',
        color='Total_Cost',
        color_continuous_scale=[(0, '#00AA00'), (1, '#00FF00')]
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Region',
        yaxis_title='Total Cost',
        xaxis_tickangle=-45,
        margin=dict(l=10, r=10, t=50, b=100),
        height=500
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickprefix='$', tickformat=',.0f')
    
    # Add to charts list
    charts.append(fig)
    
    # Create region spend trend chart if Date column exists
    if 'Date' in df.columns:
        # Convert Date to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Group by month and region
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_region_spend = df.groupby(['Month', 'Region'])['Total_Cost'].sum().reset_index()
        monthly_region_spend['Month'] = monthly_region_spend['Month'].dt.to_timestamp()
        
        # Get top 5 regions by total spend
        top_regions = region_spend.head(5)['Region'].tolist()
        filtered_spend = monthly_region_spend[monthly_region_spend['Region'].isin(top_regions)]
        
        # Create line chart
        fig = px.line(
            filtered_spend,
            x='Month',
            y='Total_Cost',
            color='Region',
            title='Top 5 Regions - Monthly Spend',
            color_discrete_sequence=get_color_palette(len(top_regions))
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Total Cost',
            legend_title_text='Region',
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        # Format y-axis as currency
        fig.update_yaxes(tickprefix='$', tickformat=',.0f')
        
        # Add to charts list
        charts.append(fig)
    
    return charts

def generate_region_analysis_tables(df: pd.DataFrame) -> List[pd.DataFrame]:
    """
    Generate region analysis tables from dataset
    
    Args:
        df: DataFrame with dashboard data
        
    Returns:
        List of pandas DataFrames with analysis tables
    """
    tables = []
    
    if 'Region' not in df.columns or 'Total_Cost' not in df.columns:
        return tables
    
    # Create region summary table
    region_summary = df.groupby('Region').agg({
        'Total_Cost': 'sum',
        'Order_ID': pd.Series.nunique if 'Order_ID' in df.columns else 'count'
    }).reset_index()
    
    # Rename columns
    column_names = {
        'Total_Cost': 'Total Cost',
        'Order_ID': 'Invoice Count'
    }
    region_summary = region_summary.rename(columns=column_names)
    
    # Sort by total cost
    region_summary = region_summary.sort_values('Total Cost', ascending=False)
    
    # Add to tables list
    tables.append(region_summary)
    
    # Create region chemical summary table if Chemical column exists
    if 'Chemical' in df.columns:
        # Group by region and chemical
        region_chemical = df.groupby(['Region', 'Chemical'])['Total_Cost'].sum().reset_index()
        
        # Create pivot table
        region_chemical_cross = region_chemical.pivot_table(
            index='Region',
            columns='Chemical',
            values='Total_Cost',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Add to tables list
        tables.append(region_chemical_cross)
    
    return tables

# PDF export functionality has been removed

def generate_po_analysis_charts(df: pd.DataFrame) -> List[go.Figure]:
    """
    Generate PO analysis charts from dataset
    
    Args:
        df: DataFrame with dashboard data
        
    Returns:
        List of Plotly figures
    """
    charts = []
    
    # Add basic charts
    charts.extend(generate_region_analysis_charts(df))
    charts.extend(generate_chemical_analysis_charts(df))
    charts.extend(generate_supplier_analysis_charts(df))
    
    # Add PO-specific charts
    if 'Type: Purchase Order' in df.columns:
        # Create PO Type distribution pie chart
        po_type_dist = df.groupby('Type: Purchase Order')['Total_Cost'].sum().reset_index()
        po_type_dist = po_type_dist.sort_values('Total_Cost', ascending=False)
        
        # Create pie chart
        fig = px.pie(
            po_type_dist,
            names='Type: Purchase Order',
            values='Total_Cost',
            title='PO Type Distribution',
            color_discrete_sequence=get_color_palette(len(po_type_dist)),
            hole=0.4
        )
        
        # Update layout
        fig.update_layout(
            showlegend=True,
            legend_title_text='PO Type',
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        # Add to charts list
        charts.append(fig)
        
        # Create PO Type trend chart if Date column exists
        if 'Date' in df.columns:
            # Convert Date to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Group by month and PO type
            df['Month'] = df['Date'].dt.to_period('M')
            monthly_po_type = df.groupby(['Month', 'Type: Purchase Order'])['Total_Cost'].sum().reset_index()
            monthly_po_type['Month'] = monthly_po_type['Month'].dt.to_timestamp()
            
            # Create line chart
            fig = px.line(
                monthly_po_type,
                x='Month',
                y='Total_Cost',
                color='Type: Purchase Order',
                title='PO Type - Monthly Spend',
                color_discrete_sequence=get_color_palette(po_type_dist['Type: Purchase Order'].nunique())
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title='Month',
                yaxis_title='Total Cost',
                legend_title_text='PO Type',
                margin=dict(l=10, r=10, t=50, b=10)
            )
            
            # Format y-axis as currency
            fig.update_yaxes(tickprefix='$', tickformat=',.0f')
            
            # Add to charts list
            charts.append(fig)
    
    return charts

def generate_non_po_analysis_charts(df: pd.DataFrame) -> List[go.Figure]:
    """
    Generate Non-PO analysis charts from dataset
    
    Args:
        df: DataFrame with dashboard data
        
    Returns:
        List of Plotly figures
    """
    charts = []
    
    # Add basic charts
    charts.extend(generate_region_analysis_charts(df))
    charts.extend(generate_chemical_analysis_charts(df))
    charts.extend(generate_supplier_analysis_charts(df))
    
    # Add Non-PO-specific charts
    if 'Invoice: Processing Status' in df.columns:
        # Create Processing Status distribution pie chart
        status_dist = df.groupby('Invoice: Processing Status')['Total_Cost'].sum().reset_index()
        status_dist = status_dist.sort_values('Total_Cost', ascending=False)
        
        # Create pie chart
        fig = px.pie(
            status_dist,
            names='Invoice: Processing Status',
            values='Total_Cost',
            title='Invoice Processing Status Distribution',
            color_discrete_sequence=get_color_palette(len(status_dist)),
            hole=0.4
        )
        
        # Update layout
        fig.update_layout(
            showlegend=True,
            legend_title_text='Processing Status',
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        # Add to charts list
        charts.append(fig)
    
    return charts

def apply_filters_to_dataframe(
    df: pd.DataFrame,
    filters: Dict[str, str],
    include_date_filter: bool = True
) -> pd.DataFrame:
    """
    Apply filters to a DataFrame
    
    Args:
        df: DataFrame to filter
        filters: Dictionary of filter values
        include_date_filter: Whether to include date filtering
        
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Apply standard column filters
    for col, value in filters.items():
        if col in df.columns and isinstance(value, str) and not value.startswith('All '):
            filtered_df = filtered_df[filtered_df[col] == value]
    
    # Apply date filter if requested
    if include_date_filter and 'Date' in df.columns and 'start_date' in filters and 'end_date' in filters:
        # Convert to pandas Timestamp objects
        start_date = pd.Timestamp(filters['start_date'])
        # Add one day to end_date to make it inclusive
        end_date = pd.Timestamp(filters['end_date']) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        # Apply date filter
        if not pd.api.types.is_datetime64_any_dtype(filtered_df['Date']):
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
            
        filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]
    
    return filtered_df

def add_filters(
    df: pd.DataFrame,
    container: Optional[st.container] = None,
    key_prefix: str = "dashboard",
    include_region_filter: bool = True,
    include_supplier_filter: bool = True,
    include_chemical_filter: bool = True,
    include_date_filter: bool = True
) -> Dict[str, str]:
    """
    Add filter controls to a dashboard
    
    Args:
        df: DataFrame with dashboard data
        container: Optional Streamlit container to place filters in
        key_prefix: Prefix for Streamlit widget keys
        include_region_filter: Whether to include region filter
        include_supplier_filter: Whether to include supplier filter 
        include_chemical_filter: Whether to include chemical filter
        include_date_filter: Whether to include date filter
        
    Returns:
        Dictionary of selected filter values
    """
    if container is None:
        container = st
    
    # Filter options
    filters = {}
    
    # Region filter if applicable
    if include_region_filter and 'Region' in df.columns:
        # Convert all values to strings before sorting to avoid type comparison issues
        regions = df['Region'].fillna('Unknown').astype(str).unique().tolist()
        regions = ['All Regions'] + sorted(regions)
        filters['region'] = container.selectbox(
            "Filter by Region:",
            options=regions,
            key=f"{key_prefix}_region_filter"
        )
        
    # Supplier filter if applicable
    if include_supplier_filter and 'Supplier' in df.columns:
        # Convert all values to strings before sorting to avoid type comparison issues
        suppliers = df['Supplier'].fillna('Unknown').astype(str).unique().tolist()
        suppliers = ['All Suppliers'] + sorted(suppliers)
        
        filters['supplier'] = container.selectbox(
            "Filter by Supplier:",
            options=suppliers,
            key=f"{key_prefix}_supplier_filter"
        )
    
    # Chemical filter if applicable
    if include_chemical_filter and 'Chemical' in df.columns:
        # Convert all values to strings before sorting to avoid type comparison issues
        chemicals = df['Chemical'].fillna('Unknown').astype(str).unique().tolist()
        chemicals = ['All Chemicals'] + sorted(chemicals)
        
        filters['chemical'] = container.selectbox(
            "Filter by Chemical:",
            options=chemicals,
            key=f"{key_prefix}_chemical_filter"
        )
    
    # Date range filter if applicable
    if include_date_filter and 'Date' in df.columns:
        try:
            # Get date range from the data
            if not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                
            # Get min and max dates, handling NaT values
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            
            if pd.isna(min_date):
                min_date = datetime.datetime.now() - datetime.timedelta(days=365)
            if pd.isna(max_date):
                max_date = datetime.datetime.now()
            
            # Convert to datetime.date objects
            min_date = min_date.date() if hasattr(min_date, 'date') else min_date
            max_date = max_date.date() if hasattr(max_date, 'date') else max_date
            
            # Add date picker for start date
            start_date = container.date_input(
                "Start Date:",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key=f"{key_prefix}_start_date"
            )
            
            # Add date picker for end date
            end_date = container.date_input(
                "End Date:",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key=f"{key_prefix}_end_date"
            )
            
            filters['start_date'] = start_date
            filters['end_date'] = end_date
        except Exception as e:
            logger.error(f"Error setting up date filter: {str(e)}")
            # Skip date filter if there's an error
    
    return filters