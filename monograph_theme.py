"""
Monograph Theme Module

This module provides functions for the monograph theme (clean white/gray with blue accents).
"""
import streamlit as st
import numpy as np

# Theme color definitions
MONOGRAPH_COLORS = {
    # Base UI Colors
    "background": "#FFFFFF",         # White
    "text_primary": "#000000",       # Black
    "text_secondary": "#4A4A4A",     # Dark Gray
    "borders": "#E5E5E5",            # Light Gray
    "hover_bg": "#F9F9F9",           # Lightest Gray
    "button_accent": "#B0B0B0",      # Medium Gray
    
    # Graph & Chart Colors
    "primary_data": "#3A8EC7",       # Blue
    "secondary_data": "#A9C2D8",     # Soft Gray Blue
    "tertiary_data": "#9E9E9E",      # Cool Gray
    "highlight": "#1E60A6",          # Royal Blue
    "gridlines": "#DCDCDC",          # Light Gray
    "axis_text": "#6E6E6E",          # Medium Gray
}

def get_theme_fonts():
    """Get fonts appropriate for the Monograph theme"""
    return {
        "sans-serif": ["Arial", "Helvetica", "sans-serif"],
        "monospace": ["Consolas", "Monaco", "monospace"]
    }

def is_dark_theme():
    """Check if the theme is dark"""
    return False  # Monograph theme is light by default

def get_palette(n):
    """Return n colors from the Monograph color palette
    
    Args:
        n: Number of colors to return
    """
    # Core palette of blues, grays, and accent colors
    palette = [
        MONOGRAPH_COLORS["primary_data"],    # Blue
        MONOGRAPH_COLORS["secondary_data"],  # Soft Gray Blue
        MONOGRAPH_COLORS["tertiary_data"],   # Cool Gray
        MONOGRAPH_COLORS["highlight"],       # Royal Blue
        "#5B9BD5",                          # Light Blue
        "#8064A2",                          # Purple
        "#4472C4",                          # Medium Blue
        "#70AD47",                          # Green
        "#777777",                          # Gray
        "#C0504D"                           # Brick Red
    ]
    
    # If we need more colors than in our base palette, interpolate
    if n <= len(palette):
        return palette[:n]
    else:
        # For more colors, generate a continuous palette through interpolation
        base_palette = np.array([palette])
        indices = np.linspace(0, len(palette)-1, n)
        return [palette[int(i)] for i in indices]

def get_theme_css():
    """Return CSS styles for the Monograph theme"""
    return f"""
    <style>
        /* Base UI Styles */
        html, body, .stApp {{
            background-color: {MONOGRAPH_COLORS["background"]} !important;
            color: {MONOGRAPH_COLORS["text_primary"]} !important;
            font-family: Arial, sans-serif !important;
        }}
        
        /* Header styling */
        h1, h2, h3, h4, h5, h6 {{
            color: {MONOGRAPH_COLORS["text_primary"]} !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
        }}
        
        /* Main header styling */
        .main-header {{
            background-color: {MONOGRAPH_COLORS["primary_data"]} !important;
            color: white !important;
            padding: 1.5rem !important;
            border-radius: 0.5rem !important;
            margin-bottom: 2rem !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
            font-family: Arial, sans-serif !important;
        }}
        
        /* Paragraph and text styling */
        p, div, span {{
            color: {MONOGRAPH_COLORS["text_secondary"]} !important;
            line-height: 1.6 !important;
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {MONOGRAPH_COLORS["hover_bg"]} !important;
            border-right: 1px solid {MONOGRAPH_COLORS["borders"]} !important;
        }}
        
        /* Dataframe styling */
        .dataframe {{
            border-collapse: collapse !important;
            border: 1px solid {MONOGRAPH_COLORS["borders"]} !important;
            font-family: Arial, sans-serif !important;
        }}
        
        .dataframe thead th {{
            background-color: {MONOGRAPH_COLORS["primary_data"]} !important;
            color: white !important;
            text-align: left !important;
            padding: 0.5rem !important;
        }}
        
        .dataframe tbody tr:nth-of-type(even) {{
            background-color: {MONOGRAPH_COLORS["hover_bg"]} !important;
        }}
        
        .dataframe tbody tr:hover {{
            background-color: {MONOGRAPH_COLORS["borders"]} !important;
        }}
        
        /* Button styling */
        .stButton > button {{
            background-color: {MONOGRAPH_COLORS["primary_data"]} !important;
            color: white !important;
            border: none !important;
            border-radius: 0.3rem !important;
            padding: 0.4rem 1rem !important;
            transition: all 0.3s !important;
        }}
        
        .stButton > button:hover {{
            background-color: {MONOGRAPH_COLORS["highlight"]} !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
        }}
        
        /* Dropdown styling for select boxes */
        .stSelectbox [data-baseweb="select"] {{
            border-radius: 0.3rem !important;
            border: 1px solid {MONOGRAPH_COLORS["borders"]} !important;
        }}
        
        .stSelectbox [data-baseweb="option"]:hover {{
            background-color: {MONOGRAPH_COLORS["hover_bg"]} !important;
            color: {MONOGRAPH_COLORS["highlight"]} !important;
            font-weight: 500 !important;
        }}
        
        /* Special styling for saved report dropdown in sidebar */
        [key="saved_report_dropdown"] [data-baseweb="option"]:hover,
        [key*="saved_report_dropdown_"] [data-baseweb="option"]:hover {{
            background-color: {MONOGRAPH_COLORS["primary_data"]} !important;
            box-shadow: 0 0 4px rgba(30, 96, 166, 0.5) !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 4px !important;
            transition: all 0.2s ease !important;
        }}
        
        /* Metric card styling */
        [data-testid="stMetric"] {{
            background-color: {MONOGRAPH_COLORS["hover_bg"]} !important;
            border-radius: 0.5rem !important;
            padding: 1rem !important;
            border-left: 4px solid {MONOGRAPH_COLORS["primary_data"]} !important;
            margin-bottom: 1rem !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
        }}
        
        [data-testid="stMetricValue"] {{
            color: {MONOGRAPH_COLORS["highlight"]} !important;
            font-weight: 700 !important;
            font-size: 1.8rem !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {MONOGRAPH_COLORS["text_secondary"]} !important;
            font-size: 1rem !important;
        }}
        
        /* Chart container styling */
        [data-testid="stIframe"], .js-plotly-plot {{
            border-radius: 0.5rem !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
            padding: 0.5rem !important;
            margin-bottom: 1.5rem !important;
            background-color: white !important;
            border: 1px solid {MONOGRAPH_COLORS["borders"]} !important;
        }}
        
        /* Alert box styling */
        .stAlert {{
            border-radius: 0.3rem !important;
            border-left: 5px solid {MONOGRAPH_COLORS["primary_data"]} !important;
        }}
    </style>
    """

def update_chart_theme(fig):
    """Apply the Monograph theme to a plotly figure
    
    Args:
        fig: Plotly figure to apply theme to
    """
    # Map color names to hex codes for monograph theme
    color_map = {
        "background": MONOGRAPH_COLORS["background"],
        "text": MONOGRAPH_COLORS["text_secondary"],
        "grid": MONOGRAPH_COLORS["gridlines"],
        "plot_bg": "white",
        "paper_bg": "white"
    }
    
    if hasattr(fig, 'update_layout'):
        # Apply base theme settings
        fig.update_layout(
            plot_bgcolor=color_map["plot_bg"],
            paper_bgcolor=color_map["paper_bg"],
            font=dict(
                family="Arial, sans-serif",
                color=color_map["text"],
                size=12
            ),
            margin=dict(t=60, r=40, b=60, l=40),
            legend=dict(
                font=dict(size=12, color=color_map["text"]),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor=MONOGRAPH_COLORS["borders"],
                borderwidth=1
            ),
            hovermode="closest"
        )
        
        # Update axis styling
        fig.update_xaxes(
            showgrid=True,
            gridcolor=color_map["grid"],
            linecolor=MONOGRAPH_COLORS["borders"],
            title_font=dict(size=14, color=MONOGRAPH_COLORS["text_primary"]),
            tickfont=dict(size=12, color=MONOGRAPH_COLORS["axis_text"]),
            showline=True,
            linewidth=1
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridcolor=color_map["grid"],
            linecolor=MONOGRAPH_COLORS["borders"],
            title_font=dict(size=14, color=MONOGRAPH_COLORS["text_primary"]),
            tickfont=dict(size=12, color=MONOGRAPH_COLORS["axis_text"]),
            showline=True,
            linewidth=1
        )
        
        # Update colorscales for heatmaps and 3D plots
        if any(trace.get('type', '') in ['heatmap', 'surface'] for trace in fig.data):
            for trace in fig.data:
                if trace.get('type', '') in ['heatmap', 'surface']:
                    trace.update(colorscale='Blues')
        
        # If there's a coloraxis, update it
        if hasattr(fig.layout, 'coloraxis') and fig.layout.coloraxis:
            fig.layout.coloraxis.colorscale = 'Blues'
            if hasattr(fig.layout.coloraxis, 'colorbar'):
                fig.layout.coloraxis.colorbar.title.font.color = color_map["text"]
                fig.layout.coloraxis.colorbar.tickfont.color = color_map["text"]