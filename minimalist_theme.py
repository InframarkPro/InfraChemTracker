"""
Minimalist Theme for Water Treatment Dashboard

A clean, minimalist theme with black, white, and blue tones.
"""
import streamlit as st
import numpy as np

def get_theme_fonts():
    """Get fonts appropriate for the Minimalist theme"""
    return {
        'title': 'Arial, sans-serif',
        'text': 'Arial, sans-serif',
        'code': 'Consolas, monospace'
    }

def is_dark_theme():
    """Return if we're using dark mode for this theme"""
    return False

def get_palette(n):
    """Return n colors from the Minimalist color palette
    
    Args:
        n: Number of colors to return
    """
    # Navy blues to light blues color palette
    colors = [
        '#0D1B2A',  # Dark navy blue
        '#1B263B',  # Navy blue
        '#415A77',  # Medium blue
        '#778DA9',  # Steel blue
        '#A9BCD0',  # Light blue
        '#E0E1DD',  # Off-white
    ]
    
    # If we need more colors than we have in our palette, interpolate
    if n <= len(colors):
        return colors[:n]
    else:
        # Interpolate to get more colors
        indices = np.linspace(0, len(colors) - 1, n)
        return [colors[int(i)] for i in indices]

def update_chart_theme(fig):
    """Apply the Minimalist theme to a plotly figure
    
    Args:
        fig: Plotly figure to apply theme to
    """
    # Define the minimalist color palette for charts
    background_color = '#FFFFFF'  # White
    text_color = '#000000'        # Black
    grid_color = '#E0E0E0'        # Light gray for grid
    accent_color = '#4682B4'      # Steel blue
    
    # Blue-gray color palette
    colors = [
        '#4682B4',  # Steel Blue
        '#6495ED',  # Cornflower Blue
        '#5F9EA0',  # Cadet Blue
        '#778899',  # Light Slate Gray
        '#B0C4DE',  # Light Steel Blue
        '#7B68EE',  # Medium Slate Blue
    ]
    
    # Update the layout with our minimalist theme
    fig.update_layout(
        # Set the background colors
        paper_bgcolor=background_color,
        plot_bgcolor=background_color,
        
        # Apply color palette
        colorway=colors,
        
        # Make the fonts clean and simple
        font={
            'family': 'Arial, sans-serif',
            'color': text_color,
            'size': 12
        },
        
        # Style the title
        title={
            'font': {
                'family': 'Arial, sans-serif',
                'color': text_color,
                'size': 18,
            },
            'x': 0.5,
            'xanchor': 'center'
        },
        
        # Style the axes
        xaxis={
            'gridcolor': grid_color,
            'zerolinecolor': accent_color,
            'zerolinewidth': 1,
            'showline': True,
            'linecolor': '#CCCCCC',
            'linewidth': 1,
            'ticks': 'outside',
            'tickcolor': '#999999',
            'tickfont': {'color': text_color}
        },
        yaxis={
            'gridcolor': grid_color,
            'zerolinecolor': accent_color,
            'zerolinewidth': 1,
            'showline': True,
            'linecolor': '#CCCCCC',
            'linewidth': 1,
            'ticks': 'outside',
            'tickcolor': '#999999',
            'tickfont': {'color': text_color}
        },
        
        # Set up the legend
        legend={
            'font': {'color': text_color, 'family': 'Arial, sans-serif'},
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': '#E0E0E0',
            'borderwidth': 1
        },
        
        # Adjust color axis for heatmaps
        coloraxis={
            'colorbar': {
                'outlinecolor': grid_color,
                'outlinewidth': 1,
                'tickcolor': text_color,
                'tickfont': {'color': text_color}
            },
            'colorscale': 'Blues'
        },
        
        # Clean up margins
        margin={'l': 40, 'r': 40, 't': 40, 'b': 40}
    )
    
    return fig

def get_theme_css():
    """Return CSS styles for the minimalist theme"""
    return """
    <style>
    /* Minimalist Theme CSS */
    .main-header {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #DDDDDD !important;
        box-shadow: 0 0 5px rgba(65, 90, 119, 0.3) !important;
        font-family: 'Arial', sans-serif !important;
        padding: 1rem !important;
        border-radius: 5px !important;
    }
    
    .minimalist-metric-container {
        background-color: #F8F9FA;
        border: 1px solid #E0E0E0;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .minimalist-metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #4682B4; /* Steel Blue */
        font-family: 'Arial', sans-serif;
    }
    
    .minimalist-metric-label {
        font-size: 14px;
        color: #666666; /* Gray */
        font-family: 'Arial', sans-serif;
        margin-top: 5px;
    }
    
    .minimalist-section-header {
        background-color: #F5F5F5;
        color: #333333;
        padding: 0.5rem 1rem;
        border-left: 4px solid #4682B4;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Style the tabs */
    div[data-testid="stHorizontalBlock"] > div[data-baseweb="tab-list"] {
        background-color: #FFFFFF !important;
        border-bottom: 1px solid #DDDDDD !important;
    }
    
    button[role="tab"] {
        background-color: #FFFFFF !important;
        color: #444444 !important;
        border-bottom: 2px solid transparent !important;
        font-family: 'Arial', sans-serif !important;
    }
    
    button[role="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #4682B4 !important;
        border-bottom: 2px solid #4682B4 !important;
        font-weight: bold !important;
    }
    
    /* Style the sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
        border-right: 1px solid #E0E0E0 !important;
    }
    
    /* Style buttons */
    button[kind="primary"] {
        background-color: #4682B4 !important;
        border: none !important;
    }
    
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #4682B4 !important;
        color: #4682B4 !important;
    }
    
    /* Style inputs */
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] input {
        background-color: #FFFFFF !important;
        border: 1px solid #DDDDDD !important;
        color: #333333 !important;
        border-radius: 4px !important;
    }
    
    /* Style dataframes */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E0E0E0 !important;
        border-radius: 5px !important;
    }
    
    /* Style tooltips */
    div[role="tooltip"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        color: #333333 !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Style the metrics */
    div[data-testid="metric-container"] {
        background-color: #F8F9FA;
        border-radius: 5px;
        padding: 10px;
        border: 1px solid #E0E0E0;
    }
    
    div[data-testid="metric-container"] label {
        color: #666666;
    }
    
    div[data-testid="metric-container"] p {
        color: #4682B4;
    }
    
    /* Style text elements */
    p, li, h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    div[data-testid="stMarkdownContainer"] > p {
        color: #333333 !important;
    }
    
    /* Style the app background */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Set default font for the entire app */
    .stApp, .stApp * {
        font-family: 'Arial', sans-serif;
    }
    </style>
    """