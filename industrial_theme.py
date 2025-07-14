"""
Industrial Theme Module

Contains functions for the Light Industrial theme.
This theme features a clean light gray background with orange accents,
designed to give a modern industrial look and feel.
"""

import streamlit as st
import numpy as np

# Industrial theme colors
industrial_colors = [
    '#F97316', '#FB923C', '#FDBA74', '#FED7AA', '#FFEDD5',  # Orange shades
    '#334155', '#475569', '#64748B', '#94A3B8', '#CBD5E1',  # Slate shades
    '#BE123C', '#E11D48', '#F43F5E', '#FB7185', '#FEA3B0',  # Red accents
    '#1E3A8A', '#1E40AF', '#2563EB', '#3B82F6', '#60A5FA'   # Blue accents
]

# Functions for getting theme properties
def get_industrial_fonts():
    """Get fonts appropriate for the Industrial theme"""
    # Industrial theme fonts
    return {
        'title': {'color': '#1E293B', 'size': 18},  # Dark slate for titles
        'subtitle': {'color': '#334155', 'size': 16},  # Slate for subtitles
        'text': {'color': '#475569', 'size': 14}  # Lighter slate for regular text
    }

def is_industrial_dark_theme():
    """Check if industrial theme is in dark mode"""
    # Industrial theme is always light
    return False

def get_industrial_palette(n):
    """Return n colors from the industrial palette
    
    Args:
        n: Number of colors to return
    """
    # Ensure we're requesting a valid number of colors to prevent zero division errors
    if n <= 0 or isinstance(n, float):
        n = 1  # Always return at least one color
    
    # Use minimum of requested colors or available colors
    num_colors = min(n, len(industrial_colors))
    
    return industrial_colors[:num_colors]

def get_industrial_css():
    """Return CSS for industrial theme (light gray with orange accents)"""
    return """
    <style>
    /* Light industrial theme with gray background and orange accents */
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"],
    .stTabs [data-testid="stVerticalBlock"], [data-baseweb="tab-panel"], [data-testid="stMarkdownContainer"],
    .streamlit-expanderHeader, .streamlit-expanderContent {
        background-color: #F5F5F5 !important;
        color: #333333 !important;
    }
    
    /* Input fields, selectboxes and buttons - light with slate accent */
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, 
    [data-testid="stSelectbox"], [data-testid="stMultiSelect"], [data-testid="stDateInput"] input,
    .stDateInput, .stTimeInput, [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    /* Fix for MultiSelect specifically - targeting all internal elements */
    [data-testid="stMultiSelect"] div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"],
    [data-testid="stMultiSelect"] div[data-baseweb="select"] div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] span,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] input,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] svg,
    [data-testid="stMultiSelect"] div[role="presentation"],
    div[data-baseweb="select"] [role="listbox"],
    div[role="combobox"],
    [data-testid="stMultiSelect"] div[data-baseweb="popover"],
    [data-testid="stMultiSelect"] div[data-baseweb="popover"] div,
    div[data-baseweb="popover"] div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[role="list"],
    div[role="menuitem"] {
        background-color: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* Specifically target the core select element that has black background */
    div[data-baseweb="select"] > div:first-child, 
    div[data-baseweb="select"] > div:first-child > div,
    div[data-baseweb="select"] > div > div {
        background-color: #FFFFFF !important;
    }
    
    /* Fix multiselect drop area */
    [data-testid="stMultiSelect"] [role="presentation"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    /* Fix multiselect dropdown menu */
    div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
        color: #333333 !important;
    }
    
    /* Fix multiselect tags */
    div[data-baseweb="tag"] {
        background-color: #F1F5F9 !important;
        color: #334155 !important;
    }
    
    /* Fix multiselect tag text */
    div[data-baseweb="tag"] span {
        color: #334155 !important;
    }
    
    /* Fix multiselect tag close button */
    div[data-baseweb="tag"] button {
        background-color: transparent !important;
        color: #64748B !important;
    }
    
    /* Button styles */
    [data-testid="baseButton-secondary"] {
        background-color: #F8FAFC !important;
        color: #334155 !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    [data-testid="baseButton-primary"] {
        background-color: #F97316 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    
    [data-testid="baseButton-secondary"]:hover {
        background-color: #F1F5F9 !important;
        border: 1px solid #64748B !important;
    }
    
    [data-testid="baseButton-primary"]:hover {
        background-color: #EA580C !important;
    }
    
    /* Text styling */
    h1, h2, h3, h4, h5, h6, p, span, div, label, [data-testid="stMarkdownContainer"] {
        color: #1E293B !important;
        font-family: 'Inter', 'Arial', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6,
    div.css-10trblm, div.css-1544g2n, .css-10trblm, .css-1544g2n,
    span.css-10trblm, span.css-1544g2n, p.css-10trblm, p.css-1544g2n,
    .stTitle, .stHeader, .stHeadingContainer, .stHeadingText,
    [data-testid="stHeader"], [data-testid="stHeader"] div, 
    [data-testid="stHeader"] span, [data-testid="stHeader"] p {
        color: #0F172A !important;
        background-color: transparent !important;
        font-family: 'Inter', 'Arial', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Table styles */
    .stDataFrame, [data-testid="stTable"] {
        background-color: #FFFFFF !important;
        color: #334155 !important;
    }
    
    .stDataFrame td, .stDataFrame th, [data-testid="stTable"] td, [data-testid="stTable"] th {
        background-color: #FFFFFF !important;
        color: #334155 !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    .stDataFrame th, [data-testid="stTable"] th {
        background-color: #F8FAFC !important;
    }
    
    /* Alert/message boxes */
    [data-testid="stAlert"] {
        background-color: #F8FAFC !important;
        color: #334155 !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    /* Progress bar with orange accent */
    [data-testid="stProgressBar"] {
        background-color: #E2E8F0 !important;
    }
    [data-testid="stProgressBar"] > div {
        background-color: #F97316 !important;
    }
    
    /* Code block styling */
    .stCode {
        background-color: #F8FAFC !important;
        color: #334155 !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    /* Sidebar navigation highlight */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] div:has(div:hover) {
        background-color: #F1F5F9 !important;
    }
    
    /* Checkbox accent color */
    [data-testid="stCheckbox"] {
        accent-color: #F97316 !important;
    }
    
    /* Dropdown Selectors - add highlight on hover */
    .stSelectbox:hover, .stMultiSelect:hover {
        border-color: #F97316 !important;
        box-shadow: 0 0 5px rgba(249, 115, 22, 0.3) !important;
    }
    
    /* Dropdown options */
    div[data-baseweb="select"] ul {
        background-color: #FFFFFF !important;
    }
    
    div[data-baseweb="select"] ul li {
        color: #334155 !important;
    }
    
    div[data-baseweb="select"] ul li:hover {
        background-color: #F1F5F9 !important;
    }
    
    /* Tabs styling */
    div[data-testid="stHorizontalBlock"] button[role="tab"] {
        background-color: #FFFFFF !important;
        color: #334155 !important;
    }
    
    div[data-testid="stHorizontalBlock"] button[role="tab"][aria-selected="true"] {
        background-color: #F1F5F9 !important;
        border-bottom-color: #F97316 !important;
    }
    
    /* Metric indicators */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.1) !important;
        padding: 10px !important;
    }
    [data-testid="stMetric"] label {
        color: #64748B !important;
    }
    [data-testid="stMetric"] svg {
        color: #F97316 !important;
    }
    
    /* Make sure dataframes are readable with custom styling */
    .dataframe {
        font-family: 'Inter', 'Arial', sans-serif !important;
    }
    .dataframe th {
        background-color: #F8FAFC !important;
        color: #334155 !important;
        font-weight: 600 !important;
        border: 1px solid #E2E8F0 !important;
        text-align: center !important;
    }
    .dataframe td {
        background-color: #FFFFFF !important;
        color: #334155 !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    /* Charts and plots - clean industrial look */
    .js-plotly-plot, .plotly, .plot-container {
        background-color: #FFFFFF !important;
    }
    
    /* Main header styling */
    .main-header {
        background-color: #FFFFFF !important;
        padding: 1.5rem !important;
        border-radius: 8px !important;
        color: #0F172A !important;
        text-align: center !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 4px 6px rgba(15, 23, 42, 0.1) !important;
        font-family: 'Inter', 'Arial', sans-serif !important;
        border-left: 4px solid #F97316 !important;
    }
    
    /* Ensure all labels and headers everywhere use industrial colors */
    span.main-header, div.main-header, 
    .stHeadingContainer div, .stHeadingContainer span, .stHeadingContainer p,
    div.stHeadingContainer, header, div[role="heading"],
    h1.stTitle, h1, h2, h3, 
    [data-testid="stHeader"] div, 
    [data-testid="stHeader"] span,
    .stHeadingText,
    .main-heading, div.main-heading, span.main-heading {
        color: #0F172A !important;
        background-color: transparent !important;
    }
    
    /* Force all links to use orange accent */
    a, a:link, a:visited, a:hover, a:active,
    a span, a div, a * {
        color: #F97316 !important;
        text-decoration: none !important;
    }
    
    a:hover, a:hover span, a:hover div, a:hover * {
        text-decoration: underline !important;
    }
    
    /* Force specific important elements to use industrial colors */
    h1, h2, h3, h4, h5, h6, 
    div[data-testid="stHeader"], button[kind="primary"],
    [data-testid="baseButton-primary"] {
        color: #0F172A !important;
    }
    
    /* Explicitly target the "Made with Streamlit" footer */
    footer, footer a, footer a:hover, .css-1lsmgbg,
    [data-testid="stFooter"], [data-testid="stFooter"] a, 
    [data-testid="stFooter"] span, small[data-testid="stFooter"], 
    div[data-testid="stFooter"], div[data-testid="stFooter"] a,
    div[data-testid="stFooter"] span {
        color: #64748B !important;
    }
    
    /* Subtle transition effect on hover */
    button, a, [data-testid="stWidgetLabel"] {
        transition: all 0.2s ease-in-out !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 1px dashed #CBD5E1 !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #F8FAFC !important;
        color: #334155 !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background-color: #F97316 !important;
        color: #FFFFFF !important;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        background-color: #F8FAFC;
    }
    
    ::-webkit-scrollbar-track {
        background-color: #F8FAFC;
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb {
        background-color: #CBD5E1;
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background-color: #94A3B8;
    }
    
    /* Card-like elements */
    div.element-container div.row-widget.stButton,
    div.element-container [data-testid="stMetric"],
    div.element-container [data-testid="stDataFrame"],
    div.element-container div.stSelectbox,
    div.element-container div.stMultiSelect,
    div.element-container div.stNumberInput {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.1) !important;
        padding: 1px !important;
        margin-bottom: 10px !important;
        border: 1px solid #F1F5F9 !important;
    }
    
    div.element-container div.row-widget.stButton:hover,
    div.element-container [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 6px rgba(15, 23, 42, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """

def update_industrial_chart_theme(fig):
    """Apply the industrial theme to a plotly figure
    
    Args:
        fig: Plotly figure to apply theme to
    """
    fonts = get_industrial_fonts()
    
    # White background
    bg_color = '#FFFFFF'
    
    # Industrial theme colors
    grid_color = 'rgba(241, 245, 249, 0.9)'  # Light slate grid
    line_color = '#CBD5E1'  # Slate lines
    accent_color = '#F97316'  # Orange accent
    
    # Industrial colorway
    theme_colors = [
        '#F97316', '#334155', '#3B82F6', '#10B981', '#A855F7',
        '#EC4899', '#EF4444', '#F59E0B', '#84CC16', '#06B6D4'
    ]
    
    # Industrial font colors
    title_color = '#0F172A'  # Dark slate titles
    text_color = '#334155'  # Slate text
    
    # Apply styling
    fig.update_layout(
        title_font=dict(
            color=title_color, 
            size=fonts['title']['size'] if isinstance(fonts, dict) and 'title' in fonts and 'size' in fonts['title'] else 18,
            family="Inter, Arial, sans-serif"
        ),
        font=dict(
            color=text_color,
            family="Inter, Arial, sans-serif"
        ),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        legend=dict(
            font=dict(
                color=text_color, 
                size=12,
                family="Inter, Arial, sans-serif"
            )
        )
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor=grid_color, 
        zerolinecolor=line_color, 
        zeroline=True, 
        zerolinewidth=1.5,
        title_font=dict(family="Inter, Arial, sans-serif"),
        tickfont=dict(family="Inter, Arial, sans-serif", color=text_color)
    )
    fig.update_yaxes(
        gridcolor=grid_color, 
        zerolinecolor=line_color, 
        zeroline=True, 
        zerolinewidth=1.5,
        title_font=dict(family="Inter, Arial, sans-serif"),
        tickfont=dict(family="Inter, Arial, sans-serif", color=text_color)
    )
    
    # Apply theme colorway
    fig.update_layout(colorway=theme_colors)
    
    # Add subtle effect to the plot
    for trace in fig.data:
        if hasattr(trace, 'line'):
            if hasattr(trace.line, 'color'):
                if not trace.line.color:
                    trace.line.color = accent_color  # Theme accent color
            # Skip line.width modification completely as it causes issues with arrays
            pass
        if hasattr(trace, 'marker'):
            if hasattr(trace.marker, 'color'):
                # Check if it's a scalar attribute we can modify
                try:
                    if not isinstance(trace.marker.color, (list, np.ndarray)):
                        trace.marker.color = accent_color  # Theme accent color
                except:
                    pass  # Skip if there's any issue
            if hasattr(trace.marker, 'line'):
                try:
                    trace.marker.line = dict(color='#FFFFFF', width=1)  # White border
                except:
                    pass  # Skip if there's any issue
    
    return fig