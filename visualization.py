import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_overview_chart(df, chart_type):
    """
    Creates overview charts based on the specified chart type.
    
    Args:
        df: DataFrame containing the data to visualize
        chart_type: Type of chart to create (monthly_trend, facility_distribution, etc.)
        
    Returns:
        plotly.graph_objects.Figure: The created chart
    """
    if chart_type == 'monthly_trend':
        # Create monthly trend line chart
        monthly_data = df.groupby(df['Date'].dt.to_period('M')).agg({
            'Total_Cost': 'sum'
        }).reset_index()
        
        # Convert Period to datetime for Plotly
        monthly_data['Date'] = monthly_data['Date'].dt.to_timestamp()
        
        fig = px.line(
            monthly_data, 
            x='Date', 
            y='Total_Cost',
            title='Monthly Chemical Spend Trend',
            labels={'Total_Cost': 'Total Spend ($)', 'Date': 'Month'},
            markers=True
        )
        
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Total Spend ($)',
            hovermode='x unified'
        )
        
        return fig
    
    elif chart_type == 'facility_distribution':
        # Create supplier distribution bar chart
        facility_data = df.groupby('Facility').agg({
            'Total_Cost': 'sum'
        }).reset_index().sort_values('Total_Cost', ascending=False)
        
        fig = px.bar(
            facility_data,
            x='Facility',
            y='Total_Cost',
            title='Chemical Spend by Supplier',
            labels={'Total_Cost': 'Total Spend ($)', 'Facility': 'Supplier'},
            color='Total_Cost',
            color_continuous_scale='blues'
        )
        
        fig.update_layout(
            xaxis_title='Supplier',
            yaxis_title='Total Spend ($)',
            coloraxis_showscale=False
        )
        
        return fig
    
    elif chart_type == 'chemical_distribution':
        # Create chemical distribution pie chart
        chemical_data = df.groupby('Chemical').agg({
            'Total_Cost': 'sum'
        }).reset_index().sort_values('Total_Cost', ascending=False)
        
        # Get top 5 chemicals and group the rest as "Others"
        if len(chemical_data) > 5:
            top_chemicals = chemical_data.iloc[:5]
            others = pd.DataFrame({
                'Chemical': ['Others'],
                'Total_Cost': [chemical_data.iloc[5:]['Total_Cost'].sum()]
            })
            chemical_data = pd.concat([top_chemicals, others])
        
        fig = px.pie(
            chemical_data,
            values='Total_Cost',
            names='Chemical',
            title='Chemical Spend Distribution',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    elif chart_type == 'treatment_comparison':
        # Create type comparison (Catalog vs Free Text) - simplified to only show total spend by PO type
        treatment_data = df.groupby('Type: Purchase Order').agg({
            'Total_Cost': 'sum'
        }).reset_index()
        
        # Map Type: Purchase Order to ensure proper categorization
        type_mapping = {
            'Water': 'Catalog',
            'Wastewater': 'Free Text',
            'Catalog': 'Catalog',
            'Free Text': 'Free Text',
            'Free text': 'Free Text',
            'Punch out': 'Free Text',  # Map Punch out to Free Text
            'Punchout': 'Free Text'    # Alternative spelling
        }
        
        # Apply mapping if the Type: Purchase Order is in the mapping
        treatment_data['Display_Type'] = treatment_data['Type: Purchase Order'].map(
            lambda x: type_mapping.get(x, 'Free Text' if 'text' in str(x).lower() or 'punch' in str(x).lower() else 'Catalog')
        )
        
        # Create a pie chart for total spend by purchase order type
        fig = px.pie(
            treatment_data,
            values='Total_Cost',
            names='Display_Type',
            title='Total Spend by Purchase Order Type',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Spend: $%{value:,.2f}<br>Percentage: %{percent}'
        )
        
        return fig
    
    elif chart_type == 'unit_price_trends':
        # Create unit price trends for top chemicals
        # First get the top 5 chemicals by total spend
        top_chemicals = df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False).head(5).index.tolist()
        
        # Filter data for top chemicals only
        filtered_df = df[df['Chemical'].isin(top_chemicals)]
        
        # Group by chemical and month to get average unit price
        price_data = filtered_df.groupby(['Chemical', filtered_df['Date'].dt.to_period('M')]).agg({
            'Unit_Price': 'mean'
        }).reset_index()
        
        # Convert Period to datetime for Plotly
        price_data['Date'] = price_data['Date'].dt.to_timestamp()
        
        fig = px.line(
            price_data,
            x='Date',
            y='Unit_Price',
            color='Chemical',
            title='Unit Price Trends for Top Chemicals',
            labels={'Unit_Price': 'Unit Price ($)', 'Date': 'Month', 'Chemical': 'Chemical Type'},
            markers=True
        )
        
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Average Unit Price ($)',
            hovermode='x unified',
            legend_title='Chemical'
        )
        
        return fig
    
    elif chart_type == 'quantity_by_chemical':
        # Create quantity by chemical horizontal bar chart
        quantity_data = df.groupby('Chemical').agg({
            'Quantity': 'sum'
        }).reset_index().sort_values('Quantity', ascending=True)
        
        # Get top 10 by quantity
        quantity_data = quantity_data.tail(10)
        
        fig = px.bar(
            quantity_data,
            y='Chemical',
            x='Quantity',
            title='Total Quantity by Chemical Type',
            labels={'Quantity': 'Total Quantity', 'Chemical': 'Chemical Type'},
            orientation='h',
            color='Quantity',
            color_continuous_scale='greens'
        )
        
        fig.update_layout(
            yaxis_title='Chemical Type',
            xaxis_title='Total Quantity',
            coloraxis_showscale=False
        )
        
        return fig
    
    elif chart_type == 'type_chemical_distribution':
        # Create a chart showing chemical distribution by order type (Catalog vs Free Text)
        # Ensure we're using the standardized order types
        mapped_df = df.copy()
        
        # Apply the same mapping logic to ensure consistency with data processing
        type_mapping = {
            'Water': 'Catalog',
            'Wastewater': 'Free Text',
            'Catalog': 'Catalog',
            'Free Text': 'Free Text',
            'Punch out': 'Free Text'
        }
        
        # Apply mapping if needed
        mapped_df['Type: Purchase Order'] = mapped_df['Type: Purchase Order'].map(
            lambda x: type_mapping.get(x, 'Free Text' if 'text' in str(x).lower() or 'punch' in str(x).lower() else 'Catalog')
        )
        
        # Now split the data
        catalog_df = mapped_df[mapped_df['Type: Purchase Order'] == 'Catalog']
        free_text_df = mapped_df[mapped_df['Type: Purchase Order'] == 'Free Text']
        
        # Get top chemicals by spend for each type
        catalog_chemicals = catalog_df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False).head(5)
        free_text_chemicals = free_text_df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False).head(5)
        
        # Prepare data for plotting
        catalog_data = pd.DataFrame({
            'Chemical': catalog_chemicals.index,
            'Total_Cost': catalog_chemicals.values,
            'Order_Type': ['Catalog'] * len(catalog_chemicals)
        })
        
        free_text_data = pd.DataFrame({
            'Chemical': free_text_chemicals.index,
            'Total_Cost': free_text_chemicals.values,
            'Order_Type': ['Free Text'] * len(free_text_chemicals)
        })
        
        # Combine data
        combined_data = pd.concat([catalog_data, free_text_data])
        
        # Create the grouped bar chart
        fig = px.bar(
            combined_data,
            x='Chemical',
            y='Total_Cost',
            color='Order_Type',
            barmode='group',
            title='Top Chemicals by Order Type',
            labels={'Total_Cost': 'Total Spend ($)', 'Chemical': 'Chemical', 'Order_Type': 'Order Type'},
            color_discrete_map={'Catalog': '#636EFA', 'Free Text': '#EF553B'}
        )
        
        fig.update_layout(
            xaxis_title='Chemical',
            yaxis_title='Total Spend ($)',
            legend_title='Order Type',
            xaxis={'categoryorder':'total descending'}  # Sort by total spend
        )
        
        return fig
    
    else:
        # Default empty figure if chart type not recognized
        fig = go.Figure()
        fig.update_layout(
            title="Chart type not recognized",
            xaxis_title="X",
            yaxis_title="Y"
        )
        return fig

def plot_facility_comparison(df, facilities=None):
    """
    Creates a comparison chart for selected suppliers.
    
    Args:
        df: DataFrame containing the data
        facilities: List of suppliers to compare (if None, uses top 5)
        
    Returns:
        plotly.graph_objects.Figure: The supplier comparison chart
    """
    if facilities is None or len(facilities) == 0:
        # Get top 5 suppliers by total spend
        top_facilities = df.groupby('Facility')['Total_Cost'].sum().sort_values(ascending=False).head(5).index.tolist()
        facilities = top_facilities
    
    # Filter data for selected suppliers
    filtered_df = df[df['Facility'].isin(facilities)]
    
    # Create monthly data for each supplier
    facility_monthly = filtered_df.groupby(['Facility', filtered_df['Date'].dt.to_period('M')]).agg({
        'Total_Cost': 'sum'
    }).reset_index()
    
    # Convert Period to datetime for Plotly
    facility_monthly['Date'] = facility_monthly['Date'].dt.to_timestamp()
    
    # Create line chart
    fig = px.line(
        facility_monthly,
        x='Date',
        y='Total_Cost',
        color='Facility',
        title='Monthly Spend Comparison by Supplier',
        labels={'Total_Cost': 'Total Spend ($)', 'Date': 'Month', 'Facility': 'Supplier'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Total Spend ($)',
        hovermode='x unified',
        legend_title='Supplier'
    )
    
    return fig

def plot_chemical_usage_by_facility(df, chemical=None):
    """
    Creates a chart showing chemical usage across suppliers.
    
    Args:
        df: DataFrame containing the data
        chemical: Specific chemical to analyze (if None, uses top chemical by spend)
        
    Returns:
        plotly.graph_objects.Figure: The chemical usage chart
    """
    if chemical is None:
        # Get top chemical by total spend
        chemical = df.groupby('Chemical')['Total_Cost'].sum().sort_values(ascending=False).index[0]
    
    # Filter data for selected chemical
    filtered_df = df[df['Chemical'] == chemical]
    
    # Group by supplier
    facility_data = filtered_df.groupby('Facility').agg({
        'Quantity': 'sum',
        'Total_Cost': 'sum'
    }).reset_index().sort_values('Quantity', ascending=False)
    
    # Create bubble chart
    fig = px.scatter(
        facility_data,
        x='Quantity',
        y='Total_Cost',
        size='Quantity',
        color='Facility',
        hover_name='Facility',
        title=f'{chemical} Usage and Cost by Supplier',
        labels={'Quantity': 'Total Quantity', 'Total_Cost': 'Total Spend ($)', 'Facility': 'Supplier'}
    )
    
    fig.update_layout(
        xaxis_title='Total Quantity',
        yaxis_title='Total Spend ($)',
        hovermode='closest'
    )
    
    return fig

def plot_cost_efficiency(df):
    """
    Creates a chart showing cost efficiency (unit price) across suppliers.
    
    Args:
        df: DataFrame containing the data
        
    Returns:
        plotly.graph_objects.Figure: The cost efficiency chart
    """
    # Group by supplier and chemical to get average unit price
    efficiency_data = df.groupby(['Facility', 'Chemical']).agg({
        'Unit_Price': 'mean',
        'Quantity': 'sum',
        'Total_Cost': 'sum'
    }).reset_index()
    
    # Get top 5 chemicals by total quantity
    top_chemicals = df.groupby('Chemical')['Quantity'].sum().sort_values(ascending=False).head(5).index.tolist()
    
    # Filter for top chemicals
    filtered_data = efficiency_data[efficiency_data['Chemical'].isin(top_chemicals)]
    
    # Create grouped bar chart
    fig = px.bar(
        filtered_data,
        x='Chemical',
        y='Unit_Price',
        color='Facility',
        barmode='group',
        title='Cost Efficiency Comparison (Unit Price by Supplier)',
        labels={'Unit_Price': 'Average Unit Price ($)', 'Chemical': 'Chemical', 'Facility': 'Supplier'}
    )
    
    fig.update_layout(
        xaxis_title='Chemical',
        yaxis_title='Average Unit Price ($)',
        legend_title='Supplier'
    )
    
    return fig
