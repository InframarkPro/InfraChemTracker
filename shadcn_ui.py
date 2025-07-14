"""
ShadCN-inspired UI components for Streamlit

This module provides modern, enterprise-grade UI components inspired by the ShadCN UI library
but implemented for Streamlit using custom HTML/CSS.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from water_treatment_theme import get_palette, update_chart_theme
import pandas as pd
import numpy as np
import io
from typing import List, Dict, Any, Union, Optional

def load_shadcn_theme():
    """Load the ShadCN-inspired theme CSS"""
    st.markdown("""
    <style>
    /* Global font and radius variables */
    :root {
        --radius: 0.5rem;
        --primary: 222.2 47.4% 11.2%;
        --primary-foreground: 210 40% 98%;
        --secondary: 210 40% 96.1%;
        --card: 0 0% 100%;
        --card-foreground: 222.2 47.4% 11.2%;
        --border: 214.3 31.8% 91.4%;
        --muted: 210 40% 96.1%;
        --muted-foreground: 215.4 16.3% 46.9%;
        --accent: 210 40% 96.1%;
        --accent-foreground: 222.2 47.4% 11.2%;
        --success: 142, 76%, 36%;
        --info: 199, 89%, 48%;
        --warning: 38, 92%, 50%;
        --danger: 0, 84%, 60%;
    }
    
    /* Card component styling */
    .shadcn-card {
        background-color: white;
        border-radius: var(--radius);
        border: 1px solid hsl(var(--border));
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    .shadcn-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: var(--radius);
        transition: all 0.2s ease;
        font-weight: 500;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
        background-color: hsla(var(--muted));
        padding: 0.25rem;
        border-radius: var(--radius);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius);
        padding: 0.5rem 1rem;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: black;
        font-weight: 500;
    }
    
    /* Data tables */
    .stDataFrame {
        border-radius: var(--radius);
        border: 1px solid hsl(var(--border));
    }
    .stDataFrame [data-testid="stDataFrameResizable"] {
        border-radius: var(--radius);
        overflow: hidden;
    }
    
    /* Selectbox styling */
    div[data-baseweb="select"] > div {
        border-radius: var(--radius);
        transition: all 0.2s ease;
    }
    
    /* Slider styling */
    div[data-testid="stThumbValue"] {
        border-radius: 9999px;
        padding: 0.25rem 0.5rem;
        font-size: 0.875rem;
        background-color: hsl(var(--primary));
        color: hsl(var(--primary-foreground));
    }
    
    /* Number input styling */
    [data-testid="stNumberInput"] > div {
        border-radius: var(--radius);
    }
    
    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: hsl(var(--card-foreground));
        font-weight: 600;
    }
    
    /* Enterprise dashboard header */
    .enterprise-header {
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .enterprise-header h1 {
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #111827;
    }
    .enterprise-header p {
        color: #6B7280;
        margin-bottom: 0;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: hsla(var(--muted));
        border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    /* Dashboard section styling */
    .dashboard-section {
        margin-bottom: 1.5rem;
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    /* KPI metric styling */
    .kpi-metric {
        font-size: 1.875rem;
        font-weight: 700;
        line-height: 1.2;
        margin: 0.5rem 0 0.25rem 0;
    }
    .kpi-label {
        font-size: 0.875rem;
        color: hsl(var(--muted-foreground));
        margin: 0;
    }
    .kpi-title {
        font-size: 1rem;
        font-weight: 500;
        margin: 0 0 0.5rem 0;
        color: #374151;
    }
    
    /* Card colors */
    .blue-card {
        border-left: 4px solid #2563EB;
        background-color: #EFF6FF;
    }
    .green-card {
        border-left: 4px solid #10B981;
        background-color: #ECFDF5;
    }
    .amber-card {
        border-left: 4px solid #F59E0B;
        background-color: #FFFBEB;
    }
    .purple-card {
        border-left: 4px solid #8B5CF6;
        background-color: #F5F3FF;
    }
    .sky-card {
        border-left: 4px solid #0EA5E9;
        background-color: #F0F9FF;
    }
    
    /* Chart wrappers */
    .chart-wrapper {
        background-color: white;
        border-radius: var(--radius);
        padding: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        animation: fadeIn 0.6s ease-out forwards;
    }
    .chart-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #111827;
    }
    </style>
    """, unsafe_allow_html=True)


def shadcn_card(title: str, 
                content: str, 
                metric: Optional[str] = None, 
                icon: Optional[str] = None, 
                color_scheme: str = "blue",
                key: Optional[str] = None,
                detail_data: Optional[dict] = None):
    """
    Display a ShadCN-inspired card component with animation and interactive capability
    
    Args:
        title: Card title
        content: Card content text
        metric: Optional metric value (large number/value)
        icon: Optional icon (emoji or HTML)
        color_scheme: Color scheme (blue, green, amber, red, purple, sky)
        key: Optional unique key for the card (for session state)
        detail_data: Optional dictionary with detailed data to display when clicked
    """
    
    # Color class mapping
    color_class = {
        "blue": "blue-card",
        "green": "green-card", 
        "amber": "amber-card",
        "red": "red-card",
        "purple": "purple-card",
        "sky": "sky-card"
    }.get(color_scheme, "blue-card")
    
    # Generate a unique key if none provided
    if key is None:
        import hashlib
        key = f"card_{hashlib.md5((title + content + str(metric or '')).encode()).hexdigest()[:8]}"
    
    # Initialize session state for this card if it doesn't exist
    if f"show_details_{key}" not in st.session_state:
        st.session_state[f"show_details_{key}"] = False
    
    # Create a clickable container
    with st.container():
        # Build the card HTML with inline styles for clickability
        html = f"""
        <div class="shadcn-card {color_class} animate-fade-in" style="cursor: pointer; position: relative;" 
        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 12px 20px -5px rgba(0,0,0,0.1), 0 8px 16px -8px rgba(0,0,0,0.1)'; this.querySelector('.card-hint').style.opacity=1;"
        onmouseout="this.style.transform='none'; this.style.boxShadow='0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)'; this.querySelector('.card-hint').style.opacity=0;"
        onclick="
            // Use setTimeout to allow this to execute after the click
            setTimeout(function() {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: true,
                    dataType: 'bool', 
                    key: 'show_details_{key}'
                }}, '*');
            }}, 10);
        ">
            <div class="kpi-title">{title}</div>
            {f'<div class="kpi-metric">{metric}</div>' if metric else ''}
            <div class="kpi-label">{content}</div>
            {f'<div style="float:right;margin-top:-2.5rem;font-size:1.5rem;">{icon}</div>' if icon else ''}
            <div class="card-hint" style="opacity: 0; transition: opacity 0.3s ease; position: absolute; bottom: 5px; right: 10px; font-size: 0.7rem; color: #6b7280;">Click for details</div>
        </div>
        """
        
        st.markdown(html, unsafe_allow_html=True)
        
        # Use a hidden checkbox to toggle the details view
        # This is invisible but when clicked, it triggers rerun
        toggle = st.checkbox("Toggle", key=f"show_details_{key}", value=st.session_state[f"show_details_{key}"], label_visibility="hidden")
        
        # Show details if toggled
        if toggle and detail_data:
            with st.expander(f"Details for {title}", expanded=True):
                # Display the detailed information
                if isinstance(detail_data, dict):
                    for key, value in detail_data.items():
                        if isinstance(value, (list, pd.Series)) and len(value) > 0:
                            st.subheader(key)
                            
                            # Check if it's a dataframe-compatible object
                            if hasattr(value, 'values') and hasattr(value, 'index'):
                                # Display as a chart if it has index
                                try:
                                    chart_data = pd.DataFrame({key: value})
                                    st.bar_chart(chart_data)
                                except:
                                    # Fallback to displaying as text
                                    st.write(value)
                            else:
                                # Simple list display
                                st.write(value)
                        elif isinstance(value, dict):
                            st.subheader(key)
                            st.json(value)
                        else:
                            st.metric(key, value)
                else:
                    st.write(detail_data)
                
                # Add a button to close the details
                if st.button("Close Details", key=f"close_{key}"):
                    st.session_state[f"show_details_{key}"] = False
                    st.rerun()


def dashboard_header(title: str, subtitle: str = ""):
    """
    Display an enterprise dashboard header
    
    Args:
        title: Dashboard title
        subtitle: Dashboard subtitle or description
    """
    st.markdown(f"""
    <div class="enterprise-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, description: str = ""):
    """
    Display a styled section header
    
    Args:
        title: Section title
        description: Optional section description
    """
    st.markdown(f"""
    <div class="dashboard-section">
        <h2 style="font-size: 1.25rem; margin-bottom: 0.5rem;">{title}</h2>
        {f'<p style="color: #6B7280; margin-top: 0;">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)


def chart_container(chart_func, title: str = "", description: str = "", height: Optional[int] = None, 
                    show_download: bool = False, config_options: Optional[Dict[str, Any]] = None):
    """
    Wraps a chart in a styled container with enhanced interactivity and download options
    
    Args:
        chart_func: Function that generates and returns a plotly figure
        title: Chart title
        description: Optional chart description
        height: Optional chart height (px)
        show_download: Whether to show download options
        config_options: Additional Plotly config options
    """
    # Apply custom styles with theme-specific appearance
    active_theme = st.session_state.get('color_theme', 'matrix')
    
    if active_theme == 'industrial':
        # Industrial theme styling for chart container
        st.markdown(f"""
        <style>
        .enhanced-chart-wrapper {{
            background-color: #F5F5F5;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(249, 115, 22, 0.3);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease;
        }}
        .chart-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #1E293B;
            margin-bottom: 0.25rem;
            font-family: 'Inter', Arial, sans-serif;
        }}
        </style>
        <div class="enhanced-chart-wrapper">
            <div class="chart-title">{title}</div>
            {f'<p style="color: #475569; margin-top: 0.25rem; margin-bottom: 1rem; font-size: 0.875rem; font-family: Inter, Arial, sans-serif;">{description}</p>' if description else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Matrix theme styling for chart container
        st.markdown(f"""
        <style>
        .enhanced-chart-wrapper {{
            background-color: #000000;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid #00FF00;
            box-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
            transition: all 0.2s ease;
        }}
        .chart-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #00FF00;
            margin-bottom: 0.25rem;
            font-family: 'Courier New', monospace;
        }}
        </style>
        <div class="enhanced-chart-wrapper">
            <div class="chart-title">{title}</div>
            {f'<p style="color: #00FF00; margin-top: 0.25rem; margin-bottom: 1rem; font-size: 0.875rem; font-family: Courier New, monospace;">{description}</p>' if description else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # Generate the chart
    try:
        fig = chart_func()
        
        # Apply theme and configuration
        update_chart_theme(fig)
        
        # Set chart height if provided
        if height:
            fig.update_layout(height=height)
            
        # Enhance interactivity
        default_config = {
            'displayModeBar': True,
            'scrollZoom': True,
            'responsive': True,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'displaylogo': False,
        }
        
        # Merge with any custom config options
        if config_options:
            default_config.update(config_options)
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True, config=default_config)
        
        # Add download options if requested
        if show_download:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                # Download as PNG button (using Plotly's native functionality)
                st.markdown("""
                <div style="font-size: 0.75rem; color: #6B7280; margin-bottom: 0.5rem;">
                    Use the camera icon in the chart toolbar to download as PNG
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Error generating chart: {str(e)}")
        st.markdown(f"**{title}**: No data available to display")


def create_animated_bar_chart(df: pd.DataFrame, 
                              x_col: str,
                              y_col: str, 
                              color_col: Optional[str] = None,
                              title: str = "", 
                              orientation: str = 'h',
                              top_n: int = 10,
                              category_orders: Optional[Dict] = None):
    """
    Create an animated bar chart with ShadCN styling
    
    Args:
        df: DataFrame with the data
        x_col: Column for x-axis
        y_col: Column for y-axis
        color_col: Optional column for color
        title: Chart title
        orientation: Chart orientation ('h' for horizontal, 'v' for vertical)
        top_n: Number of top entries to include
        category_orders: Optional dict with category orders
        
    Returns:
        Plotly figure object
    """
    # Handle empty dataframe
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"{title} (No Data Available)",
            xaxis_title=x_col,
            yaxis_title=y_col
        )
        return fig
        
    # Get top N entries
    if orientation == 'h':
        sorted_df = df.sort_values(x_col, ascending=False).head(top_n)
        x, y = x_col, y_col
    else:
        sorted_df = df.sort_values(y_col, ascending=False).head(top_n)
        x, y = y_col, x_col
        
    # Create figure
    if color_col and color_col in df.columns:
        fig = px.bar(
            sorted_df,
            x=x,
            y=y,
            orientation=orientation,
            color=color_col,
            color_continuous_scale=get_palette(max(2, len(sorted_df))),
            title=title,
            category_orders=category_orders
        )
    else:
        fig = px.bar(
            sorted_df,
            x=x,
            y=y,
            orientation=orientation,
            color_discrete_sequence=get_palette(1),
            title=title,
            category_orders=category_orders
        )
    
    # Update layout for animation
    fig.update_layout(
        transition_duration=500,
        transition=dict(duration=500, easing='cubic-in-out'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis={'categoryorder': 'total ascending'} if orientation == 'h' else {},
        xaxis_title=None,
        yaxis_title=None,
        legend_title_text=color_col if color_col else None,
    )
    
    # Add hover template
    label_col = y if orientation == 'h' else x
    value_col = x if orientation == 'h' else y
    
    # Add text property to ensure hover works properly
    if orientation == 'h':
        fig.update_traces(text=sorted_df[y_col])
    else:
        fig.update_traces(text=sorted_df[x_col])
    
    # Check if it's a currency column
    if value_col.lower().find('spend') >= 0 or value_col.lower().find('cost') >= 0:
        # Currency format for currency columns
        if orientation == 'h':
            fig.update_traces(
                hovertemplate='<b>%{text}</b><br>$%{x:,.2f}'
            )
        else:
            fig.update_traces(
                hovertemplate='<b>%{text}</b><br>$%{y:,.2f}'
            )
    else:
        # Regular format with count information
        if orientation == 'h':
            fig.update_traces(
                hovertemplate='<b>%{text}</b><br>Count: %{x:,.0f}'
            )
        else:
            fig.update_traces(
                hovertemplate='<b>%{text}</b><br>Count: %{y:,.0f}'
            )
    
    # Improve overall chart interactivity
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#000000",
            font_size=14,
            font_family="Courier New, monospace",
            font_color="#00FF00"
        )
    )
    
    # Apply Matrix theme
    update_chart_theme(fig)
    
    return fig


def create_animated_pie_chart(df: pd.DataFrame, 
                             values_col: str,
                             names_col: str,
                             title: str = ""):
    """
    Create an animated pie chart with ShadCN styling
    
    Args:
        df: DataFrame with the data
        values_col: Column for slice values
        names_col: Column for slice names
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    # Handle empty dataframe
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"{title} (No Data Available)"
        )
        return fig
    
    # Make sure we're getting an appropriate number of colors
    num_categories = df[names_col].nunique()
    num_colors = max(1, min(num_categories, 20))  # Limit to 20 colors
    
    # Create figure
    fig = px.pie(
        df,
        values=values_col,
        names=names_col,
        color_discrete_sequence=get_palette(num_colors),
        title=title
    )
    
    # Ensure text inside pie slices is black
    fig.update_traces(
        textfont_color="#000000",
        insidetextfont=dict(color="#000000"),
        outsidetextfont=dict(color="#000000")
    )
    
    # Update layout for animation
    fig.update_layout(
        transition_duration=500,
        transition=dict(duration=500, easing='cubic-in-out'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=20, l=20, r=20),
        legend_title_text=names_col,
        font=dict(color="#000000"),  # Force black font color for all text
        title_font=dict(color="#000000"),  # Force black font color for title
        legend_font=dict(color="#000000")  # Force black font color for legend
    )
    
    # Add hover template with improved styling
    if values_col.lower().find('spend') >= 0 or values_col.lower().find('cost') >= 0:
        # Currency format for financial data
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}'
        )
    else:
        # Regular format with clear labels
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}'
        )
    
    # Improve hover label styling with Matrix theme
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#000000",
            font_size=14,
            font_family="Courier New, monospace",
            font_color="#00FF00"
        )
    )
    
    # Apply Matrix theme
    update_chart_theme(fig)
    
    return fig


def create_animated_line_chart(df: pd.DataFrame,
                              x_col: str,
                              y_col: Union[str, List[str]],
                              color_col: Optional[str] = None,
                              title: str = ""):
    """
    Create an animated line chart with ShadCN styling
    
    Args:
        df: DataFrame with the data
        x_col: Column for x-axis
        y_col: Column(s) for y-axis - can be a string or list of strings
        color_col: Optional column for color
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    # Handle empty dataframe
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"{title} (No Data Available)",
            xaxis_title=x_col,
            yaxis_title=y_col if isinstance(y_col, str) else "Value"
        )
        return fig
    
    # Create figure
    if isinstance(y_col, list):
        # Multiple y columns
        fig = go.Figure()
        for i, col in enumerate(y_col):
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                mode='lines+markers',
                name=col,
                line=dict(color=get_palette(len(y_col))[i], width=3),
                marker=dict(size=8)
            ))
    elif color_col and color_col in df.columns:
        # Single y column with color grouping
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            color_discrete_sequence=get_palette(df[color_col].nunique()),
            title=title,
            markers=True
        )
    else:
        # Simple line chart
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color_discrete_sequence=get_palette(1),
            title=title,
            markers=True
        )
    
    # Update layout for animation
    fig.update_layout(
        transition_duration=500,
        transition=dict(duration=500, easing='cubic-in-out'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title=None,
        yaxis_title=None,
        legend_title_text=color_col if color_col else None,
    )
    
    # Check if it's a currency column
    y_title = y_col if isinstance(y_col, str) else "Value"
    is_currency = y_title.lower().find('spend') >= 0 or y_title.lower().find('cost') >= 0
    
    if is_currency:
        # Currency format for y-axis
        fig.update_layout(
            yaxis=dict(
                tickprefix='$',
                tickformat=',.',
            )
        )
        
        # Add custom currency hover template
        if isinstance(y_col, list):
            for i in range(len(fig.data)):
                fig.data[i].hovertemplate = '<b>%{x}</b><br>$%{y:,.2f}'
        else:
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>$%{y:,.2f}'
            )
    else:
        # Regular hover template for non-currency
        if isinstance(y_col, list):
            for i in range(len(fig.data)):
                fig.data[i].hovertemplate = '<b>%{x}</b><br>Value: %{y:,.1f}'
        else:
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>Value: %{y:,.1f}'
            )
    
    # Improve hover styling with Matrix theme
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#000000",
            font_size=14,
            font_family="Courier New, monospace",
            font_color="#00FF00"
        )
    )
    
    # Apply Matrix theme
    update_chart_theme(fig)
    
    return fig


def create_shadcn_table(df: pd.DataFrame, 
                       page_size: int = 10,
                       title: str = "",
                       description: str = "",
                       column_config: Optional[Dict] = None,
                       enable_search: bool = True,
                       key_prefix: str = "table"):
    """
    Display a styled paginated table with ShadCN styling and improved functionality
    
    Args:
        df: DataFrame to display
        page_size: Number of rows per page
        title: Table title
        description: Table description
        column_config: Optional column configuration for st.dataframe
        enable_search: Whether to enable a search box
        key_prefix: Prefix for the keys used in session state to avoid conflicts
    """
    # Get the active theme
    active_theme = st.session_state.get('color_theme', 'matrix')
    
    if active_theme == 'industrial':
        # Industrial theme styling for tables
        st.markdown("""
        <style>
        .enhanced-table-wrapper {
            background-color: #F5F5F5;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(249, 115, 22, 0.3);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        .table-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1E293B;
            margin-bottom: 0.25rem;
            font-family: 'Inter', 'Arial', sans-serif;
        }
        .table-description {
            color: #475569; 
            font-size: 0.875rem;
            margin-bottom: 1rem;
            font-family: 'Inter', 'Arial', sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Matrix theme styling for tables
        st.markdown("""
        <style>
        .enhanced-table-wrapper {
            background-color: #000000;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid #00FF00;
            box-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
        }
        .table-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #00FF00;
            margin-bottom: 0.25rem;
            font-family: 'Courier New', monospace;
        }
        .table-description {
            color: #00FF00; 
            font-size: 0.875rem;
            margin-bottom: 1rem;
            font-family: 'Courier New', monospace;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="enhanced-table-wrapper">
        {f'<div class="table-title">{title}</div>' if title else ''}
        {f'<div class="table-description">{description}</div>' if description else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for this table if it doesn't exist
    filter_key = f"{key_prefix}_filter"
    page_key = f"{key_prefix}_page"
    rows_key = f"{key_prefix}_rows"
    
    if filter_key not in st.session_state:
        st.session_state[filter_key] = ""
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    if rows_key not in st.session_state:
        st.session_state[rows_key] = page_size
    
    # Search functionality
    filtered_df = df.copy()
    if enable_search:
        search_term = st.text_input(
            "Search table",
            value=st.session_state[filter_key],
            placeholder="Enter search term...",
            key=f"{key_prefix}_search"
        )
        
        # Update session state when search changes
        if search_term != st.session_state[filter_key]:
            st.session_state[filter_key] = search_term
            st.session_state[page_key] = 1  # Reset to first page on new search
            
        if search_term:
            # Case-insensitive search on string columns
            mask = pd.Series(False, index=filtered_df.index)
            for col in filtered_df.select_dtypes(include=['object', 'string']).columns:
                mask |= filtered_df[col].astype(str).str.contains(search_term, case=False, na=False)
            filtered_df = filtered_df[mask]
    
    # Calculate pagination
    total_rows = len(filtered_df)
    max_pages = max(1, (total_rows - 1) // st.session_state[rows_key] + 1) if total_rows > 0 else 1
    
    # Ensure current page is valid
    if st.session_state[page_key] > max_pages:
        st.session_state[page_key] = max_pages
    
    # Page controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        rows_per_page = st.select_slider(
            "Rows per page",
            options=[10, 25, 50, 100],
            value=st.session_state[rows_key],
            key=f"{key_prefix}_rows_slider"
        )
        # Update session state when rows per page changes
        if rows_per_page != st.session_state[rows_key]:
            st.session_state[rows_key] = rows_per_page
            # Adjust page number if needed
            max_pages_new = max(1, (total_rows - 1) // rows_per_page + 1) if total_rows > 0 else 1
            if st.session_state[page_key] > max_pages_new:
                st.session_state[page_key] = max_pages_new
    
    with col2:
        page_number = st.number_input(
            "Page",
            min_value=1,
            max_value=max_pages,
            value=st.session_state[page_key],
            step=1,
            key=f"{key_prefix}_page_input"
        )
        # Update session state when page number changes
        if page_number != st.session_state[page_key]:
            st.session_state[page_key] = page_number
    
    with col3:
        active_theme = st.session_state.get('color_theme', 'matrix')
        if active_theme == 'industrial':
            st.markdown(
                f'<div style="padding-top:2rem; color: #1E293B; font-family: Inter, Arial, sans-serif;">Showing {min(1, total_rows)}-{min(st.session_state[page_key] * st.session_state[rows_key], total_rows)} of {total_rows} rows</div>', 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="padding-top:2rem; color: #00FF00; font-family: Courier New, monospace;">Showing {min(1, total_rows)}-{min(st.session_state[page_key] * st.session_state[rows_key], total_rows)} of {total_rows} rows</div>', 
                unsafe_allow_html=True
            )
    
    # Add quick navigation buttons
    cols = st.columns([1, 1, 1, 1])
    with cols[0]:
        # Convert to boolean to ensure proper type
        first_disabled = bool(st.session_state.get(page_key, 1) == 1)
        if st.button("⏮️ First", key=f"{key_prefix}_first", disabled=first_disabled):
            st.session_state[page_key] = 1
            st.rerun()
    
    with cols[1]:
        # Convert to boolean to ensure proper type
        prev_disabled = bool(st.session_state.get(page_key, 1) == 1)
        if st.button("◀️ Previous", key=f"{key_prefix}_prev", disabled=prev_disabled):
            st.session_state[page_key] -= 1
            st.rerun()
    
    with cols[2]:
        # Convert to boolean to ensure proper type
        next_disabled = bool(st.session_state.get(page_key, 1) == max_pages)
        if st.button("Next ▶️", key=f"{key_prefix}_next", disabled=next_disabled):
            st.session_state[page_key] += 1
            st.rerun()
    
    with cols[3]:
        # Convert to boolean to ensure proper type
        last_disabled = bool(st.session_state.get(page_key, 1) == max_pages)
        if st.button("Last ⏭️", key=f"{key_prefix}_last", disabled=last_disabled):
            st.session_state[page_key] = max_pages
            st.rerun()
    
    # Calculate start and end indices
    start_idx = (st.session_state[page_key] - 1) * st.session_state[rows_key]
    end_idx = min(start_idx + st.session_state[rows_key], total_rows)
    
    # Display the data with column configuration if provided
    if column_config:
        st.dataframe(
            filtered_df.iloc[start_idx:end_idx],
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
    else:
        st.dataframe(
            filtered_df.iloc[start_idx:end_idx],
            use_container_width=True,
            hide_index=True
        )
    
    # Display filtered row count
    if total_rows < len(df) and enable_search:
        active_theme = st.session_state.get('color_theme', 'matrix')
        if active_theme == 'industrial':
            st.markdown(f'<div style="color: #1E293B; font-family: Inter, Arial, sans-serif; font-size: 0.875rem; margin-top: 0.5rem;">Filtered from {len(df):,} to {total_rows:,} rows based on search.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color: #00FF00; font-family: Courier New, monospace; font-size: 0.875rem; margin-top: 0.5rem;">Filtered from {len(df):,} to {total_rows:,} rows based on search.</div>', unsafe_allow_html=True)
    
    # Add download options with two formats
    col1, col2 = st.columns(2)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"{title.lower().replace(' ', '_')}_data.csv" if title else "data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Excel export
        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Data')
            
            excel_data = buffer.getvalue()
            
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name=f"{title.lower().replace(' ', '_')}_data.xlsx" if title else "data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Excel export error: {str(e)}")


def format_currency(value):
    """Format a value as currency with dollar sign"""
    if pd.isna(value):
        return "-"
    return f"${value:,.2f}"


def create_animated_scatter_chart(df: pd.DataFrame,
                                x_col: str,
                                y_col: str,
                                color_col: Optional[str] = None,
                                title: str = ""):
    """
    Create an animated scatter chart with trend line
    
    Args:
        df: DataFrame with the data
        x_col: Column for x-axis
        y_col: Column for y-axis
        color_col: Optional column for color grouping
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    # Handle empty dataframe
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"{title} (No Data Available)",
            xaxis_title=x_col,
            yaxis_title=y_col
        )
        return fig
    
    # Create scatter plot
    if color_col and color_col in df.columns:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            color_discrete_sequence=get_palette(df[color_col].nunique()),
            title=title,
            trendline="ols", # Add trend line
            trendline_scope="overall", # One trend line for all data
            opacity=0.7
        )
    else:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color_discrete_sequence=get_palette(1),
            title=title,
            trendline="ols", # Add trend line
            opacity=0.7
        )
    
    # Update layout for animation
    fig.update_layout(
        transition_duration=500,
        transition=dict(duration=500, easing='cubic-in-out'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title=x_col,
        yaxis_title=y_col,
        legend_title_text=color_col if color_col else None
    )
    
    # Improve hover styling
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#000000",
            font_size=14,
            font_family="Courier New, monospace",
            font_color="#00FF00"
        )
    )
    
    # Apply theme
    update_chart_theme(fig)
    
    return fig