"""
Interactive Analysis Components

This module contains functions for the interactive analysis features 
that replace the static details views in the Chemical Spend Dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from water_treatment_theme import get_palette, update_chart_theme

def display_chemical_analysis(df, selected_chemical):
    """Display interactive chemical analysis dashboard
    
    Args:
        df (DataFrame): The full dataset to analyze
        selected_chemical (str): The chemical to analyze, or "SHOW_ALL" for overview
    """
    # Add a back button to return to the main dashboard
    col1, col2 = st.columns([1, 7])
    with col1:
        if st.button("← Back", key="chemical_back_button"):
            st.session_state.selected_chemical = None
            st.rerun()
    
    with col2:
        if selected_chemical == "SHOW_ALL":
            st.header("Chemical Analysis Overview")
        else:
            st.header(f"Chemical Analysis: {selected_chemical}")
    
    # Analysis sections
    if selected_chemical == "SHOW_ALL":
        # Show overview of all chemicals
        show_chemical_overview(df)
    else:
        # Filter for just this chemical
        chemical_df = df[df['Chemical'] == selected_chemical]
        
        # Check if we have data
        if chemical_df.empty:
            st.warning(f"No data found for chemical: {selected_chemical}")
            return
        
        # Show detailed analysis for this chemical
        show_chemical_details(df, chemical_df, selected_chemical)

def show_chemical_overview(df):
    """Show overview of all chemicals in the dataset"""
    # Top chemicals by spend amount
    st.subheader("Top Chemicals by Total Spend")
    
    # Calculate chemicals
    if 'Chemical' in df.columns and 'Total_Cost' in df.columns:
        # Get top 15 for chart
        top_chemical_spend = df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False).head(15)
        
        # Get all chemicals for table
        all_chemical_spend = df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False)
        
        # Create two columns
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create chart
            if not top_chemical_spend.empty:
                # Prepare data for chart
                chart_df = pd.DataFrame({
                    'Chemical': top_chemical_spend.index,
                    'Total Spend': top_chemical_spend.values
                })
                
                # Create horizontal bar chart
                fig = px.bar(
                    chart_df,
                    y="Chemical",
                    x="Total Spend",
                    color="Total Spend",
                    color_continuous_scale="Viridis", # Use a standard color scale instead of get_palette
                    orientation='h',
                    labels={'Total Spend': 'Total Spend ($)', 'Chemical': ''},
                    height=500
                )
                
                # Format x-axis to show dollar amounts
                fig.update_xaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Total Spend ($)",
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"Chart shows top 15 chemicals only. See table for all {len(all_chemical_spend)} chemicals.")
            else:
                st.info("No chemical data available for chart")
        
        with col2:
            # Show the data as a table with ALL chemicals
            table_df = pd.DataFrame({
                'Chemical': all_chemical_spend.index,
                'Total Spend': all_chemical_spend.values.round(2)
            })
            
            # Format the Total Spend column with dollar signs
            table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
            
            # Display the table
            st.dataframe(table_df, use_container_width=True, hide_index=True, height=500)
    
    # Chemical usage by units
    st.subheader("Chemical Usage by Units")
    if all(col in df.columns for col in ['Chemical', 'Quantity', 'Units']):
        # Group by chemical and sum quantities
        chemical_usage = df.groupby(['Chemical', 'Units']).agg({
            'Quantity': 'sum',
            'Total_Cost': 'sum'
        }).reset_index()
        
        # Sort by total cost
        chemical_usage = chemical_usage.sort_values(by='Total_Cost', ascending=False)
        
        # Create table
        usage_table = pd.DataFrame({
            'Chemical': chemical_usage['Chemical'],
            'Total Quantity': chemical_usage['Quantity'].round(2).astype(str) + ' ' + chemical_usage['Units'],
            'Average Unit Cost': (chemical_usage['Total_Cost'] / chemical_usage['Quantity']).round(2),
            'Total Spend': chemical_usage['Total_Cost'].round(2)
        })
        
        # Format currency columns
        usage_table['Average Unit Cost'] = usage_table['Average Unit Cost'].apply(lambda x: f"${x:,.2f}")
        usage_table['Total Spend'] = usage_table['Total Spend'].apply(lambda x: f"${x:,.2f}")
        
        # Display table with all chemical usage data
        st.dataframe(usage_table, use_container_width=True, hide_index=True, height=500)
    else:
        st.info("Insufficient data for chemical usage analysis")
    
    # Add a section showing chemicals by region
    if all(col in df.columns for col in ['Chemical', 'Project Region', 'Total_Cost']):
        st.subheader("Chemical Usage by Region")
        
        # Group by region and chemical
        region_chemical = df.pivot_table(
            index='Project Region',
            columns='Chemical',
            values='Total_Cost',
            aggfunc='sum',
            fill_value=0
        )
        
        # Get top 10 chemicals by spend for better visualization
        top_chemicals = df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False).head(10).index.tolist()
        
        if len(top_chemicals) > 0 and not region_chemical.empty:
            # Filter for top chemicals
            filtered_data = region_chemical[top_chemicals].copy()
            
            # Create a heatmap
            # Convert to long format for plotly
            heat_data = filtered_data.reset_index().melt(
                id_vars=['Project Region'],
                value_vars=top_chemicals,
                var_name='Chemical',
                value_name='Spend'
            )
            
            # Create custom green color scale for better visibility in Matrix theme
            matrix_scale = [
                [0, '#000000'],      # Pure black for zero values
                [0.1, '#003300'],    # Very dark green for low values
                [0.3, '#006600'],    # Dark green
                [0.5, '#009900'],    # Medium green
                [0.7, '#00CC00'],    # Bright green
                [0.9, '#00FF00'],    # Neon green
                [1.0, '#66FF66']     # Light neon green for highest values
            ]
            
            # Create heatmap with enhanced visibility
            fig = px.density_heatmap(
                heat_data,
                x='Chemical',
                y='Project Region',
                z='Spend',
                color_continuous_scale=matrix_scale,
                labels={'Spend': 'Total Spend ($)'},
                height=500
            )
            
            # Format hover template to show dollar amounts
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>%{x}: $%{z:,.2f}<extra></extra>'
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title="Chemical",
                yaxis_title="Region",
                paper_bgcolor='#000000',  # Pure black background
                plot_bgcolor='#000000',   # Pure black background
                font=dict(
                    color='#00FF00',      # Neon green text
                    family="Courier New, monospace"  # Matrix style font
                ),
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Spend ($)",
                        font=dict(color='#00FF00', family="Courier New, monospace")
                    ),
                    tickfont=dict(color='#00FF00', family="Courier New, monospace"),
                    outlinecolor='#00FF00'
                )
            )
            
            # Apply water treatment theme
            update_chart_theme(fig)
            
            # Show chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for region/chemical analysis")

def show_chemical_details(df, chemical_df, chemical_name):
    """Show detailed analysis for a specific chemical"""
    # Create tabs for organized data display
    tabs = st.tabs(["Overview", "Supplier Analysis", "Regional Analysis", "Invoice Details"])
    
    with tabs[0]:
        # Key metrics for this chemical
        st.subheader(f"{chemical_name} Key Metrics")
        
        # Calculate key metrics
        total_spend = chemical_df['Total_Cost'].sum() if 'Total_Cost' in chemical_df.columns else 0
        total_quantity = chemical_df['Quantity'].sum() if 'Quantity' in chemical_df.columns else 0
        avg_unit_price = total_spend / total_quantity if total_quantity > 0 else 0
        invoice_count = len(chemical_df)
        units = chemical_df['Units'].iloc[0] if 'Units' in chemical_df.columns and len(chemical_df) > 0 else ""
        
        # Create metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Spend", f"${total_spend:,.2f}")
        with col2:
            st.metric("Total Quantity", f"{total_quantity:,.2f} {units}")
        with col3:
            st.metric("Average Unit Price", f"${avg_unit_price:,.2f}")
        with col4:
            st.metric("Invoice Count", f"{invoice_count:,}")
        
        # Monthly trend if we have date data
        if 'Date' in chemical_df.columns:
            st.subheader("Monthly Spend Trend")
            
            # Group by month
            monthly_trend = chemical_df.groupby(pd.Grouper(key='Date', freq='M'))['Total_Cost'].sum()
            
            # Create line chart
            if len(monthly_trend) > 1:
                # Create dataframe for chart
                trend_df = pd.DataFrame({
                    'Month': monthly_trend.index,
                    'Total Spend': monthly_trend.values
                })
                
                # Create line chart
                fig = px.line(
                    trend_df,
                    x='Month',
                    y='Total Spend',
                    markers=True,
                    labels={'Total Spend': 'Total Spend ($)', 'Month': ''},
                    height=400
                )
                
                # Format y-axis to show dollar amounts
                fig.update_yaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Total Spend ($)"
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient time series data for trend chart")
    
    with tabs[1]:
        # Supplier analysis
        st.subheader(f"Suppliers for {chemical_name}")
        
        # Identify the supplier column
        supplier_column = 'Supplier' if 'Supplier' in chemical_df.columns else '{Vendor}' if '{Vendor}' in chemical_df.columns else None
        
        if supplier_column:
            # Get top suppliers
            supplier_spend = chemical_df.groupby(supplier_column)['Total_Cost'].sum().sort_values(ascending=False)
            
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create chart
                if not supplier_spend.empty:
                    # Prepare data for chart
                    chart_df = pd.DataFrame({
                        'Supplier': supplier_spend.index,
                        'Total Spend': supplier_spend.values
                    })
                    
                    # Create pie chart
                    fig = px.pie(
                        chart_df,
                        names='Supplier',
                        values='Total Spend',
                        color_discrete_sequence=get_palette(len(chart_df)),
                        height=400
                    )
                    
                    # Add hover formatting
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>'
                    )
                    
                    # Apply water treatment theme
                    update_chart_theme(fig)
                    
                    # Show chart
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No supplier data available for chart")
            
            with col2:
                # Show the data as a table
                if not supplier_spend.empty:
                    table_df = pd.DataFrame({
                        'Supplier': supplier_spend.index,
                        'Total Spend': supplier_spend.values.round(2)
                    })
                    
                    # Calculate percentage of total
                    table_df['% of Total'] = (table_df['Total Spend'] / table_df['Total Spend'].sum() * 100).round(1)
                    
                    # Format the columns
                    table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
                    table_df['% of Total'] = table_df['% of Total'].apply(lambda x: f"{x}%")
                    
                    # Display the table
                    st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("No supplier data available for table")
        else:
            st.info("No supplier column found in the dataset")
    
    with tabs[2]:
        # Regional analysis
        st.subheader(f"Regional Usage of {chemical_name}")
        
        if 'Project Region' in chemical_df.columns:
            # Get regional breakdown
            region_spend = chemical_df.groupby('Project Region')['Total_Cost'].sum().sort_values(ascending=False)
            
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create chart
                if not region_spend.empty:
                    # Prepare data for chart
                    chart_df = pd.DataFrame({
                        'Region': region_spend.index,
                        'Total Spend': region_spend.values
                    })
                    
                    # Create bar chart
                    fig = px.bar(
                        chart_df,
                        x='Region',
                        y='Total Spend',
                        color='Total Spend',
                        color_continuous_scale=get_palette(len(chart_df)),
                        labels={'Total Spend': 'Total Spend ($)', 'Region': ''},
                        height=400
                    )
                    
                    # Format y-axis to show dollar amounts
                    fig.update_yaxes(tickprefix="$", tickformat=",.2f")
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Region",
                        yaxis_title="Total Spend ($)"
                    )
                    
                    # Apply water treatment theme
                    update_chart_theme(fig)
                    
                    # Show chart
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No regional data available for chart")
            
            with col2:
                # Show the data as a table
                if not region_spend.empty:
                    table_df = pd.DataFrame({
                        'Region': region_spend.index,
                        'Total Spend': region_spend.values.round(2)
                    })
                    
                    # Calculate percentage of total
                    table_df['% of Total'] = (table_df['Total Spend'] / table_df['Total Spend'].sum() * 100).round(1)
                    
                    # Format the columns
                    table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
                    table_df['% of Total'] = table_df['% of Total'].apply(lambda x: f"{x}%")
                    
                    # Display the table
                    st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("No regional data available for table")
        else:
            st.info("No region column found in the dataset")
    
    with tabs[3]:
        # Invoice details
        st.subheader(f"Invoice Details for {chemical_name}")
        
        if not chemical_df.empty:
            # Create a clean dataframe for display
            display_cols = [col for col in chemical_df.columns if col not in ['index', 'level_0', 'selected']]
            
            # If we have a lot of columns, show a more compact view
            if len(display_cols) > 8:
                # Prioritize important columns
                priority_cols = [
                    'Date', 'Bill #', supplier_column if supplier_column else '',
                    'Project Region', 'Department', 'Chemical', 'Quantity', 'Units', 'Total_Cost'
                ]
                # Filter to only existing columns
                display_cols = [col for col in priority_cols if col in chemical_df.columns]
            
            # Create a copy to avoid modifying the original
            display_df = chemical_df[display_cols].copy()
            
            # Format any financial columns
            if 'Total_Cost' in display_df.columns:
                display_df['Total Cost'] = display_df['Total_Cost'].apply(lambda x: f"${x:,.2f}")
                display_df = display_df.drop(columns=['Total_Cost'])
            
            # Display with pagination
            st.dataframe(display_df, use_container_width=True, height=500)
        else:
            st.info("No invoice data available")

def display_supplier_analysis(df, selected_supplier, supplier_column):
    """Display interactive supplier analysis dashboard
    
    Args:
        df (DataFrame): The full dataset to analyze
        selected_supplier (str): The supplier to analyze, or "SHOW_ALL" for overview
        supplier_column (str): The column containing supplier names
    """
    # Add a back button to return to the main dashboard
    col1, col2 = st.columns([1, 7])
    with col1:
        if st.button("← Back", key="supplier_back_button"):
            st.session_state.selected_supplier = None
            st.rerun()
    
    with col2:
        if selected_supplier == "SHOW_ALL":
            st.header("Supplier Analysis Overview")
        else:
            st.header(f"Supplier Analysis: {selected_supplier}")
    
    # Analysis sections
    if selected_supplier == "SHOW_ALL":
        # Show overview of all suppliers
        show_supplier_overview(df, supplier_column)
    else:
        # Filter for just this supplier
        supplier_df = df[df[supplier_column] == selected_supplier]
        
        # Check if we have data
        if supplier_df.empty:
            st.warning(f"No data found for supplier: {selected_supplier}")
            return
        
        # Show detailed analysis for this supplier
        show_supplier_details(df, supplier_df, selected_supplier, supplier_column)

def show_supplier_overview(df, supplier_column):
    """Show overview of all suppliers in the dataset"""
    # Top suppliers by spend amount
    st.subheader("Top Suppliers by Total Spend")
    
    # Calculate all suppliers (not just top 15)
    if supplier_column in df.columns and 'Total_Cost' in df.columns:
        # Get top 15 for the chart visualization
        top_supplier_spend = df.groupby(supplier_column)['Total_Cost'].sum().sort_values(ascending=False).head(15)
        
        # Get all suppliers for the table
        all_supplier_spend = df.groupby(supplier_column)['Total_Cost'].sum().sort_values(ascending=False)
        
        # Create two columns
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create chart
            if not top_supplier_spend.empty:
                # Prepare data for chart
                chart_df = pd.DataFrame({
                    'Supplier': top_supplier_spend.index,
                    'Total Spend': top_supplier_spend.values
                })
                
                # Create horizontal bar chart
                # Check if we have data to avoid division by zero
                if len(chart_df) > 0:
                    # Use color_discrete_sequence for a single item to avoid division by zero
                    if len(chart_df) == 1:
                        fig = px.bar(
                            chart_df,
                            y="Supplier",
                            x="Total Spend",
                            color_discrete_sequence=[get_palette(1)[0]],  # Use single color
                            orientation='h',
                            labels={'Total Spend': 'Total Spend ($)', 'Supplier': ''},
                            height=500
                        )
                    else:
                        fig = px.bar(
                            chart_df,
                            y="Supplier",
                            x="Total Spend",
                            color="Total Spend",
                            color_continuous_scale=get_palette(len(chart_df)),
                            orientation='h',
                            labels={'Total Spend': 'Total Spend ($)', 'Supplier': ''},
                            height=500
                        )
                else:
                    # Create empty figure if no data
                    fig = go.Figure()
                    fig.update_layout(
                        title="Top Suppliers by Spend (No Data Available)",
                        xaxis_title="Total Spend ($)",
                        yaxis_title="Supplier"
                    )
                
                # Format x-axis to show dollar amounts
                fig.update_xaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Total Spend ($)",
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart (displaying only top 15)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"Chart shows top 15 suppliers only. See table for all {len(all_supplier_spend)} suppliers.")
            else:
                st.info("No supplier data available for chart")
        
        with col2:
            # Show the data as a table with ALL suppliers
            table_df = pd.DataFrame({
                'Supplier': all_supplier_spend.index,
                'Total Spend': all_supplier_spend.values.round(2)
            })
            
            # Format the Total Spend column with dollar signs
            table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
            
            # Display the table with all suppliers
            st.dataframe(table_df, use_container_width=True, hide_index=True, height=500)
    
    # Supplier concentration chart
    st.subheader("Supplier Concentration")
    
    if supplier_column in df.columns and 'Total_Cost' in df.columns:
        # Group by supplier and calculate spend
        supplier_totals = df.groupby(supplier_column)['Total_Cost'].sum().sort_values(ascending=False)
        
        # Calculate cumulative percentage for Pareto analysis
        total_spend = supplier_totals.sum()
        supplier_pareto = pd.DataFrame({
            'Supplier': supplier_totals.index,
            'Spend': supplier_totals.values,
            'Percent': (supplier_totals.values / total_spend * 100)
        })
        supplier_pareto['Cumulative %'] = supplier_pareto['Percent'].cumsum()
        
        # Create two columns
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create Pareto chart
            if not supplier_pareto.empty:
                # Create figure with two y-axes
                fig = px.bar(
                    supplier_pareto.head(15),
                    x='Supplier',
                    y='Percent',
                    color='Percent',
                    color_continuous_scale=get_palette(15),
                    labels={'Percent': 'Percentage of Total (%)', 'Supplier': ''},
                    height=400
                )
                
                # Add cumulative line
                fig.add_scatter(
                    x=supplier_pareto.head(15)['Supplier'],
                    y=supplier_pareto.head(15)['Cumulative %'],
                    mode='lines+markers',
                    name='Cumulative %',
                    line=dict(color='red', width=2),
                    marker=dict(size=8, color='red'),
                    yaxis='y2'
                )
                
                # Set up layout with second y-axis
                fig.update_layout(
                    xaxis_title="Supplier",
                    yaxis_title="Percentage of Total (%)",
                    yaxis2=dict(
                        title="Cumulative %",
                        overlaying='y',
                        side='right',
                        range=[0, 100],
                        ticksuffix='%'
                    ),
                    yaxis=dict(
                        ticksuffix='%'
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient data for supplier concentration analysis")
        
        with col2:
            # Calculate concentration metrics
            top_3_perc = supplier_pareto.iloc[:3]['Percent'].sum()
            top_5_perc = supplier_pareto.iloc[:5]['Percent'].sum()
            top_10_perc = supplier_pareto.iloc[:10]['Percent'].sum() if len(supplier_pareto) >= 10 else 100
            
            # Display concentration metrics
            st.metric("Top 3 Suppliers", f"{top_3_perc:.1f}%")
            st.metric("Top 5 Suppliers", f"{top_5_perc:.1f}%")
            st.metric("Top 10 Suppliers", f"{top_10_perc:.1f}%")
            
            # Add supplier count metric
            st.metric("Total Supplier Count", f"{len(supplier_totals):,}")

def show_supplier_details(df, supplier_df, supplier_name, supplier_column):
    """Show detailed analysis for a specific supplier"""
    # Create tabs for organized data display
    tabs = st.tabs(["Overview", "Chemical Analysis", "Regional Analysis", "Invoice Details"])
    
    with tabs[0]:
        # Key metrics for this supplier
        st.subheader(f"{supplier_name} Key Metrics")
        
        # Calculate key metrics
        total_spend = supplier_df['Total_Cost'].sum() if 'Total_Cost' in supplier_df.columns else 0
        invoice_count = len(supplier_df)
        chemical_count = supplier_df['Chemical'].nunique() if 'Chemical' in supplier_df.columns else 0
        region_count = supplier_df['Project Region'].nunique() if 'Project Region' in supplier_df.columns else 0
        
        # Create metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Spend", f"${total_spend:,.2f}")
        with col2:
            st.metric("Invoice Count", f"{invoice_count:,}")
        with col3:
            st.metric("Chemical Types", f"{chemical_count:,}")
        with col4:
            st.metric("Regions Served", f"{region_count:,}")
        
        # Monthly trend if we have date data
        if 'Date' in supplier_df.columns:
            st.subheader("Monthly Spend Trend")
            
            # Group by month
            monthly_trend = supplier_df.groupby(pd.Grouper(key='Date', freq='M'))['Total_Cost'].sum()
            
            # Create line chart
            if len(monthly_trend) > 1:
                # Create dataframe for chart
                trend_df = pd.DataFrame({
                    'Month': monthly_trend.index,
                    'Total Spend': monthly_trend.values
                })
                
                # Create line chart
                fig = px.line(
                    trend_df,
                    x='Month',
                    y='Total Spend',
                    markers=True,
                    labels={'Total Spend': 'Total Spend ($)', 'Month': ''},
                    height=400
                )
                
                # Format y-axis to show dollar amounts
                fig.update_yaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Total Spend ($)"
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient time series data for trend chart")
    
    with tabs[1]:
        # Chemical analysis
        st.subheader(f"Chemicals Supplied by {supplier_name}")
        
        if 'Chemical' in supplier_df.columns:
            # Get top chemicals
            chemical_spend = supplier_df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False)
            
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create chart
                if not chemical_spend.empty:
                    # Prepare data for chart
                    chart_df = pd.DataFrame({
                        'Chemical': chemical_spend.index,
                        'Total Spend': chemical_spend.values
                    })
                    
                    # Create pie chart
                    fig = px.pie(
                        chart_df,
                        names='Chemical',
                        values='Total Spend',
                        color_discrete_sequence=get_palette(len(chart_df)),
                        height=400
                    )
                    
                    # Add hover formatting
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>'
                    )
                    
                    # Apply water treatment theme
                    update_chart_theme(fig)
                    
                    # Show chart
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No chemical data available for chart")
            
            with col2:
                # Show the data as a table
                if not chemical_spend.empty:
                    table_df = pd.DataFrame({
                        'Chemical': chemical_spend.index,
                        'Total Spend': chemical_spend.values.round(2)
                    })
                    
                    # Calculate percentage of total
                    table_df['% of Total'] = (table_df['Total Spend'] / table_df['Total Spend'].sum() * 100).round(1)
                    
                    # Format the columns
                    table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
                    table_df['% of Total'] = table_df['% of Total'].apply(lambda x: f"{x}%")
                    
                    # Display the table
                    st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("No chemical data available for table")
        else:
            st.info("No chemical column found in the dataset")
    
    with tabs[2]:
        # Regional analysis
        st.subheader(f"Regions Served by {supplier_name}")
        
        if 'Project Region' in supplier_df.columns:
            # Get regional breakdown
            region_spend = supplier_df.groupby('Project Region')['Total_Cost'].sum().sort_values(ascending=False)
            
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create chart
                if not region_spend.empty:
                    # Prepare data for chart
                    chart_df = pd.DataFrame({
                        'Region': region_spend.index,
                        'Total Spend': region_spend.values
                    })
                    
                    # Create bar chart
                    fig = px.bar(
                        chart_df,
                        x='Region',
                        y='Total Spend',
                        color='Total Spend',
                        color_continuous_scale=get_palette(len(chart_df)),
                        labels={'Total Spend': 'Total Spend ($)', 'Region': ''},
                        height=400
                    )
                    
                    # Format y-axis to show dollar amounts
                    fig.update_yaxes(tickprefix="$", tickformat=",.2f")
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Region",
                        yaxis_title="Total Spend ($)"
                    )
                    
                    # Apply water treatment theme
                    update_chart_theme(fig)
                    
                    # Show chart
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No regional data available for chart")
            
            with col2:
                # Show the data as a table
                if not region_spend.empty:
                    table_df = pd.DataFrame({
                        'Region': region_spend.index,
                        'Total Spend': region_spend.values.round(2)
                    })
                    
                    # Calculate percentage of total
                    table_df['% of Total'] = (table_df['Total Spend'] / table_df['Total Spend'].sum() * 100).round(1)
                    
                    # Format the columns
                    table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
                    table_df['% of Total'] = table_df['% of Total'].apply(lambda x: f"{x}%")
                    
                    # Display the table
                    st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("No regional data available for table")
        else:
            st.info("No region column found in the dataset")
    
    with tabs[3]:
        # Invoice details
        st.subheader(f"Invoice Details for {supplier_name}")
        
        if not supplier_df.empty:
            # Create a clean dataframe for display
            display_cols = [col for col in supplier_df.columns if col not in ['index', 'level_0', 'selected']]
            
            # If we have a lot of columns, show a more compact view
            if len(display_cols) > 8:
                # Prioritize important columns
                priority_cols = [
                    'Date', 'Bill #', supplier_column,
                    'Project Region', 'Department', 'Chemical', 'Quantity', 'Units', 'Total_Cost'
                ]
                # Filter to only existing columns
                display_cols = [col for col in priority_cols if col in supplier_df.columns]
            
            # Create a copy to avoid modifying the original
            display_df = supplier_df[display_cols].copy()
            
            # Format any financial columns
            if 'Total_Cost' in display_df.columns:
                display_df['Total Cost'] = display_df['Total_Cost'].apply(lambda x: f"${x:,.2f}")
                display_df = display_df.drop(columns=['Total_Cost'])
            
            # Display with pagination
            st.dataframe(display_df, use_container_width=True, height=500)
        else:
            st.info("No invoice data available")

def display_region_analysis(df, selected_region):
    """Display interactive region analysis dashboard
    
    Args:
        df (DataFrame): The full dataset to analyze
        selected_region (str): The region to analyze, or "SHOW_ALL" for overview
    """
    # Add a back button to return to the main dashboard
    col1, col2 = st.columns([1, 7])
    with col1:
        if st.button("← Back", key="region_back_button"):
            st.session_state.selected_region = None
            st.rerun()
    
    with col2:
        if selected_region == "SHOW_ALL":
            st.header("Region Analysis Overview")
        else:
            st.header(f"Region Analysis: {selected_region}")
    
    # Analysis sections
    if selected_region == "SHOW_ALL":
        # Show overview of all regions
        show_region_overview(df)
    else:
        # Filter for just this region
        region_df = df[df['Project Region'] == selected_region]
        
        # Check if we have data
        if region_df.empty:
            st.warning(f"No data found for region: {selected_region}")
            return
        
        # Show detailed analysis for this region
        show_region_details(df, region_df, selected_region)

def show_region_overview(df):
    """Show overview of all regions in the dataset"""
    # Top regions by spend amount
    st.subheader("Top Regions by Total Spend")
    
    # Calculate top regions
    if 'Project Region' in df.columns and 'Total_Cost' in df.columns:
        region_spend = df.groupby('Project Region')['Total_Cost'].sum().sort_values(ascending=False)
        
        # Create two columns
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create chart
            if not region_spend.empty:
                # Prepare data for chart
                chart_df = pd.DataFrame({
                    'Region': region_spend.index,
                    'Total Spend': region_spend.values
                })
                
                # Create bar chart
                fig = px.bar(
                    chart_df,
                    x="Region",
                    y="Total Spend",
                    color="Total Spend",
                    color_continuous_scale=get_palette(len(chart_df)),
                    labels={'Total Spend': 'Total Spend ($)', 'Region': ''},
                    height=500
                )
                
                # Format y-axis to show dollar amounts
                fig.update_yaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Region",
                    yaxis_title="Total Spend ($)"
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No region data available for chart")
        
        with col2:
            # Show the data as a table
            table_df = pd.DataFrame({
                'Region': region_spend.index,
                'Total Spend': region_spend.values.round(2)
            })
            
            # Format the Total Spend column with dollar signs
            table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
            
            # Display the table
            st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
    
    # Region comparison by chemicals
    st.subheader("Chemical Usage by Region")
    if all(col in df.columns for col in ['Project Region', 'Chemical', 'Total_Cost']):
        # Get top 10 chemicals for better visualization
        top_chemicals = df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False).head(10).index.tolist()
        
        if top_chemicals:
            # Filter for only top chemicals
            chemical_df = df[df['Chemical'].isin(top_chemicals)]
            
            # Group by region and chemical
            region_chemical = chemical_df.pivot_table(
                index='Project Region',
                columns='Chemical',
                values='Total_Cost',
                aggfunc='sum',
                fill_value=0
            )
            
            # Create a stacked bar chart
            if not region_chemical.empty:
                # Convert to long format for plotly
                plot_data = region_chemical.reset_index().melt(
                    id_vars=['Project Region'],
                    value_vars=top_chemicals,
                    var_name='Chemical',
                    value_name='Spend'
                )
                
                # Create enhanced Matrix green color palette for chemicals
                matrix_colors = [
                    '#00FF00',   # Neon green
                    '#33FF33',   # Light neon green
                    '#00CCFF',   # Cyan (contrast)
                    '#66FF66',   # Lighter green
                    '#00FF99',   # Green-cyan
                    '#33FFCC',   # Light green-cyan
                    '#00CC00',   # Medium green
                    '#CCFF33',   # Yellow-green
                    '#99FF33',   # Light yellow-green
                    '#00FF33'    # Green-yellow
                ]
                
                # Create stacked bar chart with enhanced colors
                fig = px.bar(
                    plot_data,
                    x='Project Region',
                    y='Spend',
                    color='Chemical',
                    color_discrete_sequence=matrix_colors[:len(top_chemicals)],
                    labels={'Spend': 'Total Spend ($)', 'Project Region': 'Region', 'Chemical': 'Chemical'},
                    height=500
                )
                
                # Format y-axis to show dollar amounts
                fig.update_yaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout with Matrix theme elements
                fig.update_layout(
                    xaxis_title="Region",
                    yaxis_title="Total Spend ($)",
                    legend_title="Chemical",
                    paper_bgcolor='#000000',  # Pure black background
                    plot_bgcolor='#000000',   # Pure black background
                    font=dict(
                        color='#00FF00',      # Neon green text
                        family="Courier New, monospace"  # Matrix style font
                    ),
                    legend=dict(
                        font=dict(
                            color='#00FF00',  # Neon green text for legend
                            family="Courier New, monospace"
                        ),
                        bordercolor='#00FF00',
                        borderwidth=1
                    )
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient data for region/chemical analysis")
        else:
            st.info("No chemical data available")

def show_region_details(df, region_df, region_name):
    """Show detailed analysis for a specific region"""
    # Create tabs for organized data display
    tabs = st.tabs(["Overview", "Chemical Analysis", "Supplier Analysis", "Invoice Details"])
    
    with tabs[0]:
        # Key metrics for this region
        st.subheader(f"{region_name} Key Metrics")
        
        # Calculate key metrics
        total_spend = region_df['Total_Cost'].sum() if 'Total_Cost' in region_df.columns else 0
        invoice_count = len(region_df)
        chemical_count = region_df['Chemical'].nunique() if 'Chemical' in region_df.columns else 0
        
        # Identify the supplier column
        supplier_column = 'Supplier' if 'Supplier' in region_df.columns else '{Vendor}' if '{Vendor}' in region_df.columns else None
        supplier_count = region_df[supplier_column].nunique() if supplier_column else 0
        
        # Create metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Spend", f"${total_spend:,.2f}")
        with col2:
            st.metric("Invoice Count", f"{invoice_count:,}")
        with col3:
            st.metric("Chemical Types", f"{chemical_count:,}")
        with col4:
            st.metric("Supplier Count", f"{supplier_count:,}")
        
        # Monthly trend if we have date data
        if 'Date' in region_df.columns:
            st.subheader("Monthly Spend Trend")
            
            # Group by month
            monthly_trend = region_df.groupby(pd.Grouper(key='Date', freq='M'))['Total_Cost'].sum()
            
            # Create line chart
            if len(monthly_trend) > 1:
                # Create dataframe for chart
                trend_df = pd.DataFrame({
                    'Month': monthly_trend.index,
                    'Total Spend': monthly_trend.values
                })
                
                # Create line chart
                fig = px.line(
                    trend_df,
                    x='Month',
                    y='Total Spend',
                    markers=True,
                    labels={'Total Spend': 'Total Spend ($)', 'Month': ''},
                    height=400
                )
                
                # Format y-axis to show dollar amounts
                fig.update_yaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Total Spend ($)"
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient time series data for trend chart")
    
    with tabs[1]:
        # Chemical analysis
        st.subheader(f"Chemical Usage in {region_name}")
        
        if 'Chemical' in region_df.columns:
            # Get top chemicals
            chemical_spend = region_df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False)
            
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create chart
                if not chemical_spend.empty:
                    # Prepare data for chart
                    chart_df = pd.DataFrame({
                        'Chemical': chemical_spend.index,
                        'Total Spend': chemical_spend.values
                    })
                    
                    # Create pie chart
                    fig = px.pie(
                        chart_df,
                        names='Chemical',
                        values='Total Spend',
                        color_discrete_sequence=get_palette(len(chart_df)),
                        height=400
                    )
                    
                    # Add hover formatting
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>'
                    )
                    
                    # Apply water treatment theme
                    update_chart_theme(fig)
                    
                    # Show chart
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No chemical data available for chart")
            
            with col2:
                # Show the data as a table
                if not chemical_spend.empty:
                    table_df = pd.DataFrame({
                        'Chemical': chemical_spend.index,
                        'Total Spend': chemical_spend.values.round(2)
                    })
                    
                    # Calculate percentage of total
                    table_df['% of Total'] = (table_df['Total Spend'] / table_df['Total Spend'].sum() * 100).round(1)
                    
                    # Format the columns
                    table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
                    table_df['% of Total'] = table_df['% of Total'].apply(lambda x: f"{x}%")
                    
                    # Display the table
                    st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("No chemical data available for table")
        else:
            st.info("No chemical column found in the dataset")
    
    with tabs[2]:
        # Supplier analysis
        st.subheader(f"Suppliers in {region_name}")
        
        # Identify the supplier column
        supplier_column = 'Supplier' if 'Supplier' in region_df.columns else '{Vendor}' if '{Vendor}' in region_df.columns else None
        
        if supplier_column:
            # Get top suppliers
            supplier_spend = region_df.groupby(supplier_column)['Total_Cost'].sum().sort_values(ascending=False)
            
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create chart
                if not supplier_spend.empty:
                    # Prepare data for chart
                    chart_df = pd.DataFrame({
                        'Supplier': supplier_spend.index,
                        'Total Spend': supplier_spend.values
                    })
                    
                    # Create bar chart
                    fig = px.bar(
                        chart_df,
                        y='Supplier',
                        x='Total Spend',
                        color='Total Spend',
                        color_continuous_scale=get_palette(len(chart_df)),
                        orientation='h',
                        labels={'Total Spend': 'Total Spend ($)', 'Supplier': ''},
                        height=400
                    )
                    
                    # Format x-axis to show dollar amounts
                    fig.update_xaxes(tickprefix="$", tickformat=",.2f")
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Total Spend ($)",
                        yaxis_title="Supplier",
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    
                    # Apply water treatment theme
                    update_chart_theme(fig)
                    
                    # Show chart
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No supplier data available for chart")
            
            with col2:
                # Show the data as a table
                if not supplier_spend.empty:
                    table_df = pd.DataFrame({
                        'Supplier': supplier_spend.index,
                        'Total Spend': supplier_spend.values.round(2)
                    })
                    
                    # Calculate percentage of total
                    table_df['% of Total'] = (table_df['Total Spend'] / table_df['Total Spend'].sum() * 100).round(1)
                    
                    # Format the columns
                    table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
                    table_df['% of Total'] = table_df['% of Total'].apply(lambda x: f"{x}%")
                    
                    # Display the table
                    st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("No supplier data available for table")
        else:
            st.info("No supplier column found in the dataset")
    
    with tabs[3]:
        # Invoice details
        st.subheader(f"Invoice Details for {region_name}")
        
        if not region_df.empty:
            # Create a clean dataframe for display
            display_cols = [col for col in region_df.columns if col not in ['index', 'level_0', 'selected']]
            
            # If we have a lot of columns, show a more compact view
            if len(display_cols) > 8:
                # Prioritize important columns
                priority_cols = [
                    'Date', 'Bill #', supplier_column if supplier_column else '',
                    'Project Region', 'Department', 'Chemical', 'Quantity', 'Units', 'Total_Cost'
                ]
                # Filter to only existing columns
                display_cols = [col for col in priority_cols if col in region_df.columns]
            
            # Create a copy to avoid modifying the original
            display_df = region_df[display_cols].copy()
            
            # Format any financial columns
            if 'Total_Cost' in display_df.columns:
                display_df['Total Cost'] = display_df['Total_Cost'].apply(lambda x: f"${x:,.2f}")
                display_df = display_df.drop(columns=['Total_Cost'])
            
            # Display with pagination
            st.dataframe(display_df, use_container_width=True, height=500)
        else:
            st.info("No invoice data available")

def display_service_analysis(df, selected_service):
    """Display interactive Line of Service analysis dashboard
    
    Args:
        df (DataFrame): The full dataset to analyze
        selected_service (str): The service to analyze, or "SHOW_ALL" for overview
    """
    # Add a back button to return to the main dashboard
    col1, col2 = st.columns([1, 7])
    with col1:
        if st.button("← Back", key="service_back_button"):
            st.session_state.selected_service = None
            st.rerun()
    
    with col2:
        if selected_service == "SHOW_ALL":
            st.header("Line of Service Analysis Overview")
        else:
            st.header(f"Line of Service Analysis: {selected_service}")
    
    # Analysis sections
    if selected_service != "SHOW_ALL":
        # Filter for just this service
        service_df = df[df['Line of Service: Name'] == selected_service]
        
        # Check if we have data
        if service_df.empty:
            st.warning(f"No data found for Line of Service: {selected_service}")
            return
        
        # Show detailed analysis for this service FIRST
        show_service_details(df, service_df, selected_service)
        
        # Add a separator
        st.markdown("---")
        st.subheader("All Lines of Service Comparison")
    
    # Show overview of all services (always shown, but after details if a specific service is selected)
    show_service_overview(df)

def show_service_overview(df):
    """Show overview of all Line of Service categories in the dataset"""
    # Top services by spend amount
    st.subheader("Line of Service by Total Spend")
    
    # Calculate top services
    if 'Line of Service: Name' in df.columns and 'Total_Cost' in df.columns:
        service_spend = df.groupby('Line of Service: Name')['Total_Cost'].sum().sort_values(ascending=False)
        
        # Show button selection first
        if not service_spend.empty:
            # First add service selection buttons above everything else
            st.write("Select a Line of Service below to see detailed analysis:")
            
            # Create multiple columns for buttons
            num_cols = 3  # Using 3 columns to fit more buttons on one line
            cols = st.columns(num_cols)
            
            # Distribute buttons across columns
            for i, service in enumerate(service_spend.index):
                col_idx = i % num_cols
                with cols[col_idx]:
                    if st.button(service, key=f"service_button_{i}"):
                        st.session_state.selected_service = service
                        st.rerun()
            
            # Add comparison of contract cap components right after the service selection buttons
            if 'Date' in df.columns:
                st.subheader("Comparison of Contract Cap Components")
                
                # Ensure Date is datetime type
                if not pd.api.types.is_datetime64_any_dtype(df['Date']):
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                
                # Group by month and Line of Service
                monthly_service_trend = df.pivot_table(
                    index=pd.Grouper(key='Date', freq='M'),
                    columns='Line of Service: Name',
                    values='Total_Cost',
                    aggfunc='sum',
                    fill_value=0
                )
                
                # Specific services to compare
                specific_services = ["Chemical Cap", "Maintenance Cap", "Sludge Cap", "Base Fee"]
                
                # Check which services are actually in the data
                available_services = [s for s in specific_services if s in monthly_service_trend.columns]
                
                if len(available_services) > 0 and not monthly_service_trend.empty:
                    # Reset index to make Date a column
                    trend_data = monthly_service_trend.reset_index()
                    
                    # Create line chart
                    fig_trend = go.Figure()
                    
                    # Custom color palette for the specific services
                    colors = {
                        "Chemical Cap": "#00A86B",  # Jade Green
                        "Maintenance Cap": "#4169E1",  # Royal Blue
                        "Sludge Cap": "#8A2BE2",  # Blue Violet
                        "Base Fee": "#FF8C00"   # Dark Orange
                    }
                    
                    # Add a line for each specified service
                    for service in available_services:
                        if service in trend_data.columns:
                            fig_trend.add_trace(go.Scatter(
                                x=trend_data['Date'],
                                y=trend_data[service],
                                mode='lines+markers',
                                name=service,
                                line=dict(color=colors.get(service)),
                                hovertemplate='<b>%{x|%b %Y}</b><br>%{y:$,.2f}<extra></extra>'
                            ))
                    
                    # Update layout
                    fig_trend.update_layout(
                        xaxis_title="Month",
                        yaxis_title="Total Spend ($)",
                        yaxis=dict(tickprefix="$", tickformat=",.2f"),
                        height=400,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    # Apply water treatment theme
                    update_chart_theme(fig_trend)
                    
                    # Show chart
                    st.plotly_chart(fig_trend, use_container_width=True, key="contract_cap_comparison_chart")
                    st.caption("Monthly spend comparison between contract components")
                    
                    # Show message if any specified services aren't available
                    missing_services = [s for s in specific_services if s not in available_services]
                    if missing_services:
                        st.info(f"Note: The following requested services are not in the current dataset: {', '.join(missing_services)}")
                else:
                    st.info("No data available for the specified Line of Service categories")
        
        # Create two columns for chart and table
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create chart
            if not service_spend.empty:
                # Prepare data for chart
                chart_df = pd.DataFrame({
                    'Line of Service': service_spend.index,
                    'Total Spend': service_spend.values
                })
                
                # Create bar chart
                fig = px.bar(
                    chart_df,
                    x='Line of Service',
                    y='Total Spend',
                    color='Total Spend',
                    color_continuous_scale=get_palette(len(chart_df)),
                    labels={'Total Spend': 'Total Spend ($)', 'Line of Service': 'Service Category'},
                    height=500
                )
                
                # Format y-axis to show dollar amounts
                fig.update_yaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Line of Service",
                    yaxis_title="Total Spend ($)"
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Make the chart interactive for drilling down
                fig.update_traces(
                    marker_line_width=1,
                    marker_line_color="white",
                    hovertemplate="<b>%{x}</b><br>Total Spend: $%{y:,.2f}<br><i>Click to see details</i>"
                )
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Add click instruction
                st.caption("Click on a service category to see detailed analysis")
                
                # Handle chart clicks
                if st.button("View All Line of Service Details", key="view_all_services"):
                    for service in service_spend.index:
                        st.session_state.selected_service = service
                        st.rerun()
                
            else:
                st.info("No Line of Service data available")
        
        with col2:
            # Show the data as a table
            if not service_spend.empty:
                table_df = pd.DataFrame({
                    'Line of Service': service_spend.index,
                    'Total Spend': service_spend.values.round(2)
                })
                
                # Calculate percentage of total
                total = table_df['Total Spend'].sum()
                table_df['Percentage'] = (table_df['Total Spend'] / total * 100).round(1)
                
                # Format columns
                table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
                table_df['Percentage'] = table_df['Percentage'].apply(lambda x: f"{x}%")
                
                # Add clickable links for each service
                table_df['Actions'] = [
                    f"[View Details](#{service.replace(' ', '_')})" for service in service_spend.index
                ]
                
                # Display the table
                st.dataframe(table_df, use_container_width=True, hide_index=True)
            else:
                st.info("No Line of Service data available")
                
def show_service_details(df, service_df, service_name):
    """Show detailed analysis for a specific Line of Service
    
    Args:
        df: Full dataset (for comparison)
        service_df: Filtered dataset for selected service
        service_name: Name of the selected service
    """
    # Basic metrics
    total_service_spend = service_df['Total_Cost'].sum()
    total_all_spend = df['Total_Cost'].sum()
    
    # Calculate percentage of total spend
    percentage = (total_service_spend / total_all_spend * 100) if total_all_spend > 0 else 0
    
    # Count invoices
    if 'Order_ID' in service_df.columns:
        invoice_count = service_df['Order_ID'].nunique()
    elif 'Bill # (Supplier Invoice #)' in service_df.columns:
        invoice_count = service_df['Bill # (Supplier Invoice #)'].nunique()
    else:
        invoice_count = len(service_df)
    
    # Calculate average invoice value
    avg_invoice_value = total_service_spend / invoice_count if invoice_count > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Spend", f"${total_service_spend:,.2f}")
    with col2:
        st.metric("% of Total", f"{percentage:.1f}%")
    with col3:
        st.metric("Invoice Count", f"{invoice_count}")
    with col4:
        st.metric("Average Value", f"${avg_invoice_value:,.2f}")
    
    # Chemicals used in this service
    st.subheader(f"Chemicals Used in {service_name}")
    if 'Chemical' in service_df.columns:
        chemical_spend = service_df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False).reset_index()
        chemical_spend['Percentage'] = (chemical_spend['Total_Cost'] / total_service_spend * 100).round(1)
        
        # Display as a table
        chemical_table = chemical_spend.copy()
        chemical_table['Total Spend'] = chemical_table['Total_Cost'].apply(lambda x: f"${x:,.2f}")
        chemical_table['Percentage'] = chemical_table['Percentage'].apply(lambda x: f"{x}%")
        chemical_table = chemical_table[['Chemical', 'Total Spend', 'Percentage']]
        
        st.dataframe(chemical_table, use_container_width=True)
        
        # Create visualization
        if len(chemical_spend) > 0:
            # Use top 10 for chart if more than 10
            chart_data = chemical_spend.head(10) if len(chemical_spend) > 10 else chemical_spend
            
            fig = px.pie(
                chart_data,
                values='Total_Cost',
                names='Chemical',
                title=f"Chemical Distribution for {service_name}",
                color_discrete_sequence=get_palette(len(chart_data))
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Total Spend: $%{value:,.2f}<br>Percentage: %{percent}'
            )
            update_chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
            
            if len(chemical_spend) > 10:
                st.caption("Chart shows top 10 chemicals only. See table for complete list.")
    else:
        st.info(f"No chemical data available for {service_name}")
    
    # Regions using this service
    st.subheader(f"Regions Using {service_name}")
    if 'Project Region' in service_df.columns:
        region_spend = service_df.groupby('Project Region')['Total_Cost'].sum().sort_values(ascending=False).reset_index()
        region_spend['Percentage'] = (region_spend['Total_Cost'] / total_service_spend * 100).round(1)
        
        # Display as a table
        region_table = region_spend.copy()
        region_table['Total Spend'] = region_table['Total_Cost'].apply(lambda x: f"${x:,.2f}")
        region_table['Percentage'] = region_table['Percentage'].apply(lambda x: f"{x}%")
        region_table = region_table[['Project Region', 'Total Spend', 'Percentage']]
        
        st.dataframe(region_table, use_container_width=True)
        
        # Create visualization
        if len(region_spend) > 0:
            fig = px.bar(
                region_spend,
                x='Project Region',
                y='Total_Cost',
                color='Total_Cost',
                color_continuous_scale=get_palette(len(region_spend)),
                labels={'Total_Cost': 'Total Spend ($)', 'Project Region': 'Region'}
            )
            fig.update_yaxes(tickprefix="$", tickformat=",.2f")
            update_chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No region data available for {service_name}")
    
    # Monthly trend for this service
    st.subheader(f"Monthly Spend Trend for {service_name}")
    if 'Date' in service_df.columns:
        # Ensure Date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(service_df['Date']):
            try:
                service_df['Date'] = pd.to_datetime(service_df['Date'])
            except:
                st.error("Could not convert Date column to datetime format")
                return
        
        # Group by month and sum
        service_df['Month'] = service_df['Date'].dt.to_period('M')
        monthly_spend = service_df.groupby('Month')['Total_Cost'].sum().reset_index()
        monthly_spend['Month'] = monthly_spend['Month'].dt.to_timestamp()
        
        # Create line chart
        if len(monthly_spend) > 0:
            fig = px.line(
                monthly_spend,
                x='Month',
                y='Total_Cost',
                markers=True,
                labels={'Total_Cost': 'Total Spend ($)', 'Month': 'Month'}
            )
            fig.update_yaxes(tickprefix="$", tickformat=",.2f")
            update_chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No trend data available for {service_name}")
    else:
        st.info(f"No date information available for {service_name}")

def display_department_analysis(df, selected_department):
    """Display interactive department analysis dashboard
    
    Args:
        df (DataFrame): The full dataset to analyze
        selected_department (str): The department to analyze, or "SHOW_ALL" for overview
    """
    # Add a back button to return to the main dashboard
    col1, col2 = st.columns([1, 7])
    with col1:
        if st.button("← Back", key="department_back_button"):
            st.session_state.selected_department = None
            st.rerun()
    
    with col2:
        if selected_department == "SHOW_ALL":
            st.header("Department Analysis Overview")
        else:
            st.header(f"Department Analysis: {selected_department}")
    
    # Identify the department column - look for both common patterns
    dept_column = None
    for col in df.columns:
        if col == 'Department' or col == 'Department: Name':
            dept_column = col
            break
    
    if not dept_column:
        st.warning("No department column found in the dataset")
        return
    
    # Analysis sections
    if selected_department == "SHOW_ALL":
        # Show overview of all departments
        show_department_overview(df, dept_column)
    else:
        # Filter for just this department
        dept_df = df[df[dept_column] == selected_department]
        
        # Check if we have data
        if dept_df.empty:
            st.warning(f"No data found for department: {selected_department}")
            return
        
        # Show detailed analysis for this department
        show_department_details(df, dept_df, selected_department, dept_column)

def show_department_overview(df, dept_column):
    """Show overview of all departments in the dataset"""
    # Top departments by spend amount
    st.subheader("Top Departments by Total Spend")
    
    # Calculate top departments
    if dept_column in df.columns and 'Total_Cost' in df.columns:
        dept_spend = df.groupby(dept_column)['Total_Cost'].sum().sort_values(ascending=False).head(15)
        
        # Create two columns
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create chart
            if not dept_spend.empty:
                # Prepare data for chart
                chart_df = pd.DataFrame({
                    'Department': dept_spend.index,
                    'Total Spend': dept_spend.values
                })
                
                # Create horizontal bar chart
                fig = px.bar(
                    chart_df,
                    y="Department",
                    x="Total Spend",
                    color="Total Spend",
                    color_continuous_scale=get_palette(len(chart_df)),
                    orientation='h',
                    labels={'Total Spend': 'Total Spend ($)', 'Department': ''},
                    height=500
                )
                
                # Format x-axis to show dollar amounts
                fig.update_xaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Total Spend ($)",
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No department data available for chart")
        
        with col2:
            # Show the data as a table
            table_df = pd.DataFrame({
                'Department': dept_spend.index,
                'Total Spend': dept_spend.values.round(2)
            })
            
            # Format the Total Spend column with dollar signs
            table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
            
            # Display the table
            st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
    
    # Department distribution by region
    st.subheader("Department Distribution by Region")
    if all(col in df.columns for col in [dept_column, 'Project Region', 'Total_Cost']):
        # Group by region and department
        region_dept = df.pivot_table(
            index='Project Region',
            columns=dept_column,
            values='Total_Cost',
            aggfunc='sum',
            fill_value=0
        )
        
        # Get top departments for better visualization
        top_depts = df.groupby(dept_column)['Total_Cost'].sum().sort_values(ascending=False).head(10).index.tolist()
        
        if top_depts and not region_dept.empty:
            # Filter for top departments
            if all(dept in region_dept.columns for dept in top_depts):
                filtered_data = region_dept[top_depts].copy()
                
                # Create a heatmap
                # Convert to long format for plotly
                heat_data = filtered_data.reset_index().melt(
                    id_vars=['Project Region'],
                    value_vars=top_depts,
                    var_name='Department',
                    value_name='Spend'
                )
                
                # Create custom green color scale for better visibility in Matrix theme
                matrix_scale = [
                    [0, '#000000'],      # Pure black for zero values
                    [0.1, '#003300'],    # Very dark green for low values
                    [0.3, '#006600'],    # Dark green
                    [0.5, '#009900'],    # Medium green
                    [0.7, '#00CC00'],    # Bright green
                    [0.9, '#00FF00'],    # Neon green
                    [1.0, '#66FF66']     # Light neon green for highest values
                ]
                
                # Create heatmap with enhanced visibility
                fig = px.density_heatmap(
                    heat_data,
                    x='Department',
                    y='Project Region',
                    z='Spend',
                    color_continuous_scale=matrix_scale,
                    labels={'Spend': 'Total Spend ($)'},
                    height=500
                )
                
                # Format hover template to show dollar amounts
                fig.update_traces(
                    hovertemplate='<b>%{y}</b><br>%{x}: $%{z:,.2f}<extra></extra>'
                )
                
                # Update layout with Matrix theme elements
                fig.update_layout(
                    xaxis_title="Department",
                    yaxis_title="Region",
                    paper_bgcolor='#000000',  # Pure black background
                    plot_bgcolor='#000000',   # Pure black background
                    font=dict(
                        color='#00FF00',      # Neon green text
                        family="Courier New, monospace"  # Matrix style font
                    ),
                    coloraxis_colorbar=dict(
                        title=dict(
                            text="Spend ($)",
                            font=dict(color='#00FF00', family="Courier New, monospace")
                        ),
                        tickfont=dict(color='#00FF00', family="Courier New, monospace"),
                        outlinecolor='#00FF00'
                    )
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient data for region/department analysis")
        else:
            st.info("Insufficient data for region/department analysis")

def show_department_details(df, dept_df, dept_name, dept_column):
    """Show detailed analysis for a specific department"""
    # Create tabs for organized data display
    tabs = st.tabs(["Overview", "Chemical Analysis", "Supplier Analysis", "Invoice Details"])
    
    with tabs[0]:
        # Key metrics for this department
        st.subheader(f"{dept_name} Key Metrics")
        
        # Calculate key metrics
        total_spend = dept_df['Total_Cost'].sum() if 'Total_Cost' in dept_df.columns else 0
        invoice_count = len(dept_df)
        chemical_count = dept_df['Chemical'].nunique() if 'Chemical' in dept_df.columns else 0
        region_count = dept_df['Project Region'].nunique() if 'Project Region' in dept_df.columns else 0
        
        # Create metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Spend", f"${total_spend:,.2f}")
        with col2:
            st.metric("Invoice Count", f"{invoice_count:,}")
        with col3:
            st.metric("Chemical Types", f"{chemical_count:,}")
        with col4:
            st.metric("Regions", f"{region_count:,}")
        
        # Monthly trend if we have date data
        if 'Date' in dept_df.columns:
            st.subheader("Monthly Spend Trend")
            
            # Group by month
            monthly_trend = dept_df.groupby(pd.Grouper(key='Date', freq='M'))['Total_Cost'].sum()
            
            # Create line chart
            if len(monthly_trend) > 1:
                # Create dataframe for chart
                trend_df = pd.DataFrame({
                    'Month': monthly_trend.index,
                    'Total Spend': monthly_trend.values
                })
                
                # Create line chart
                fig = px.line(
                    trend_df,
                    x='Month',
                    y='Total Spend',
                    markers=True,
                    labels={'Total Spend': 'Total Spend ($)', 'Month': ''},
                    height=400
                )
                
                # Format y-axis to show dollar amounts
                fig.update_yaxes(tickprefix="$", tickformat=",.2f")
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Total Spend ($)"
                )
                
                # Apply water treatment theme
                update_chart_theme(fig)
                
                # Show chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient time series data for trend chart")
    
    with tabs[1]:
        # Chemical analysis
        st.subheader(f"Chemical Usage in {dept_name}")
        
        if 'Chemical' in dept_df.columns:
            # Get top chemicals
            chemical_spend = dept_df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False)
            
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create chart
                if not chemical_spend.empty:
                    # Prepare data for chart
                    chart_df = pd.DataFrame({
                        'Chemical': chemical_spend.index,
                        'Total Spend': chemical_spend.values
                    })
                    
                    # Create pie chart
                    fig = px.pie(
                        chart_df,
                        names='Chemical',
                        values='Total Spend',
                        color_discrete_sequence=get_palette(len(chart_df)),
                        height=400
                    )
                    
                    # Add hover formatting
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>'
                    )
                    
                    # Apply water treatment theme
                    update_chart_theme(fig)
                    
                    # Show chart
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No chemical data available for chart")
            
            with col2:
                # Show the data as a table
                if not chemical_spend.empty:
                    table_df = pd.DataFrame({
                        'Chemical': chemical_spend.index,
                        'Total Spend': chemical_spend.values.round(2)
                    })
                    
                    # Calculate percentage of total
                    table_df['% of Total'] = (table_df['Total Spend'] / table_df['Total Spend'].sum() * 100).round(1)
                    
                    # Format the columns
                    table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
                    table_df['% of Total'] = table_df['% of Total'].apply(lambda x: f"{x}%")
                    
                    # Display the table
                    st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("No chemical data available for table")
        else:
            st.info("No chemical column found in the dataset")
    
    with tabs[2]:
        # Supplier analysis
        st.subheader(f"Suppliers for {dept_name}")
        
        # Identify the supplier column
        supplier_column = 'Supplier' if 'Supplier' in dept_df.columns else '{Vendor}' if '{Vendor}' in dept_df.columns else None
        
        if supplier_column:
            # Get top suppliers
            supplier_spend = dept_df.groupby(supplier_column)['Total_Cost'].sum().sort_values(ascending=False)
            
            # Create two columns
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create chart
                if not supplier_spend.empty:
                    # Prepare data for chart
                    chart_df = pd.DataFrame({
                        'Supplier': supplier_spend.index,
                        'Total Spend': supplier_spend.values
                    })
                    
                    # Create bar chart
                    fig = px.bar(
                        chart_df,
                        y='Supplier',
                        x='Total Spend',
                        color='Total Spend',
                        color_continuous_scale=get_palette(len(chart_df)),
                        orientation='h',
                        labels={'Total Spend': 'Total Spend ($)', 'Supplier': ''},
                        height=400
                    )
                    
                    # Format x-axis to show dollar amounts
                    fig.update_xaxes(tickprefix="$", tickformat=",.2f")
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Total Spend ($)",
                        yaxis_title="Supplier",
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    
                    # Apply water treatment theme
                    update_chart_theme(fig)
                    
                    # Show chart
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No supplier data available for chart")
            
            with col2:
                # Show the data as a table
                if not supplier_spend.empty:
                    table_df = pd.DataFrame({
                        'Supplier': supplier_spend.index,
                        'Total Spend': supplier_spend.values.round(2)
                    })
                    
                    # Calculate percentage of total
                    table_df['% of Total'] = (table_df['Total Spend'] / table_df['Total Spend'].sum() * 100).round(1)
                    
                    # Format the columns
                    table_df['Total Spend'] = table_df['Total Spend'].apply(lambda x: f"${x:,.2f}")
                    table_df['% of Total'] = table_df['% of Total'].apply(lambda x: f"{x}%")
                    
                    # Display the table
                    st.dataframe(table_df, use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("No supplier data available for table")
        else:
            st.info("No supplier column found in the dataset")
    
    with tabs[3]:
        # Invoice details
        st.subheader(f"Invoice Details for {dept_name}")
        
        if not dept_df.empty:
            # Create a clean dataframe for display
            display_cols = [col for col in dept_df.columns if col not in ['index', 'level_0', 'selected']]
            
            # If we have a lot of columns, show a more compact view
            if len(display_cols) > 8:
                # Prioritize important columns
                priority_cols = [
                    'Date', 'Bill #', supplier_column if supplier_column else '',
                    'Project Region', dept_column, 'Chemical', 'Quantity', 'Units', 'Total_Cost'
                ]
                # Filter to only existing columns
                display_cols = [col for col in priority_cols if col in dept_df.columns]
            
            # Create a copy to avoid modifying the original
            display_df = dept_df[display_cols].copy()
            
            # Format any financial columns
            if 'Total_Cost' in display_df.columns:
                display_df['Total Cost'] = display_df['Total_Cost'].apply(lambda x: f"${x:,.2f}")
                display_df = display_df.drop(columns=['Total_Cost'])
            
            # Display with pagination
            st.dataframe(display_df, use_container_width=True, height=500)
        else:
            st.info("No invoice data available")