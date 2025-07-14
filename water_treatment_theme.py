import streamlit as st
import numpy as np

# Theme Dispatcher - will import and use the appropriate theme modules
# Import monograph theme module
from utils.monograph_theme import (
    get_theme_fonts as get_monograph_fonts,
    is_dark_theme as is_monograph_dark_theme,
    get_palette as get_monograph_palette,
    get_theme_css as get_monograph_css,
    update_chart_theme as update_monograph_chart_theme
)

# Import industrial theme module
from utils.industrial_theme import (
    get_industrial_fonts,
    is_industrial_dark_theme,
    get_industrial_palette,
    get_industrial_css,
    update_industrial_chart_theme
)

# Matrix Green Color Palette - lighter shades to darker
light_theme_colors = [
    '#00FF00', '#00E500', '#00CC00', '#00B200', '#009900',
    '#008000', '#006600', '#004C00', '#003300', '#001A00'
]

# Matrix Dark Green Color Palette - for dark mode
dark_theme_colors = [
    '#00FF00', '#00E500', '#00CC00', '#00B200', '#009900',
    '#008000', '#006600', '#004C00', '#003300', '#001A00',
    '#00FF33', '#33FF33', '#66FF33', '#99FF33', '#CCFF33'
]

# Function to determine which theme to use
def get_active_theme():
    """Get the active theme based on session state"""
    # Set default theme if not already set
    if 'color_theme' not in st.session_state:
        st.session_state.color_theme = 'matrix'  # Default to Matrix theme
    
    # Return the selected theme
    return st.session_state.color_theme

# Title and text styling based on theme
def get_monograph_fonts():
    """Get fonts appropriate for the Monograph theme"""
    # Monograph theme fonts
    return {
        'title': {'color': '#000000', 'size': 18},  # Black for titles
        'subtitle': {'color': '#333333', 'size': 16},  # Dark gray for subtitles
        'text': {'color': '#333333', 'size': 14}  # Dark gray for regular text
    }

def get_theme_fonts():
    """Get fonts appropriate for the active theme"""
    active_theme = get_active_theme()
    
    if active_theme == 'monograph':
        return get_monograph_fonts()
    elif active_theme == 'industrial':
        return get_industrial_fonts()
    
    # Matrix theme fonts
    return {
        'title': {'color': '#FFFFFF', 'size': 16},  # White for titles
        'subtitle': {'color': '#00FF00', 'size': 14},  # Matrix green for subtitles
        'text': {'color': '#00FF00', 'size': 12}  # Matrix green for regular text
    }

def is_monograph_dark_theme():
    """Check if monograph theme is in dark mode (always False)"""
    # Monograph theme is always light
    return False

def is_dark_theme():
    """Return whether the active theme is dark"""
    # Always return True - only dark theme is used
    return True

# Custom palette functions
def get_monograph_palette(n):
    """Return n colors from the monograph palette
    
    Args:
        n: Number of colors to return
    """
    monograph_colors = [
        '#000000', '#333333', '#666666', '#999999', '#CCCCCC',
        '#444444', '#777777', '#AAAAAA', '#1A1A1A', '#4D4D4D',
        '#808080', '#B3B3B3', '#595959', '#8C8C8C', '#E6E6E6'
    ]
    
    # Ensure we're requesting a valid number of colors to prevent zero division errors
    if n <= 0 or isinstance(n, float):
        n = 1  # Always return at least one color
    
    # Use minimum of requested colors or available colors
    num_colors = min(n, len(monograph_colors))
    
    return monograph_colors[:num_colors]

def get_palette(n):
    """Return n colors from the active theme's color palette
    
    Args:
        n: Number of colors to return
    """
    # Safety check: ensure n is a positive integer
    if not isinstance(n, int) or n <= 0:
        n = 1
    
    active_theme = get_active_theme()
    
    if active_theme == 'monograph':
        return get_monograph_palette(n)
    elif active_theme == 'industrial':
        return get_industrial_palette(n)
    
    # Matrix theme palette logic
    # Always use Matrix theme colors
    colors = dark_theme_colors if is_dark_theme() else light_theme_colors
    
    # Use minimum of requested colors or available colors
    num_colors = min(n, len(colors))
    
    # Return at least one color even if num_colors is 0
    if num_colors <= 0:
        return ["#00FF00"]  # Return Matrix green as fallback
    
    return colors[:num_colors]

def get_monograph_css():
    """Return CSS for monograph theme (strict black and white with gray accents)"""
    return """
    <style>
    /* Clean white background with strict black and white theme */
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"],
    .stTabs [data-testid="stVerticalBlock"], [data-baseweb="tab-panel"], [data-testid="stMarkdownContainer"],
    .streamlit-expanderHeader, .streamlit-expanderContent {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Input fields, selectboxes and buttons - light with black accent */
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, 
    [data-testid="stSelectbox"], [data-testid="stDateInput"] input,
    .stDateInput, .stTimeInput, [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #DDDDDD !important;
    }
    
    /* Button styles */
    [data-testid="baseButton-secondary"] {
        background-color: #F5F5F5 !important;
        color: #333333 !important;
        border: 1px solid #DDDDDD !important;
    }
    
    [data-testid="baseButton-primary"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    
    [data-testid="baseButton-secondary"]:hover {
        background-color: #EEEEEE !important;
        border: 1px solid #000000 !important;
    }
    
    [data-testid="baseButton-primary"]:hover {
        background-color: #333333 !important;
    }
    
    /* Text styling */
    h1, h2, h3, h4, h5, h6, p, span, div, label, [data-testid="stMarkdownContainer"] {
        color: #333333 !important;
        font-family: 'Arial', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6,
    div.css-10trblm, div.css-1544g2n, .css-10trblm, .css-1544g2n,
    span.css-10trblm, span.css-1544g2n, p.css-10trblm, p.css-1544g2n,
    .stTitle, .stHeader, .stHeadingContainer, .stHeadingText,
    [data-testid="stHeader"], [data-testid="stHeader"] div, 
    [data-testid="stHeader"] span, [data-testid="stHeader"] p {
        color: #000000 !important;
        background-color: transparent !important;
        font-family: 'Arial', sans-serif !important;
        font-weight: bold !important;
    }
    
    /* Table styles */
    .stDataFrame, [data-testid="stTable"] {
        background-color: #FFFFFF !important;
        color: #333333 !important;
    }
    
    .stDataFrame td, .stDataFrame th, [data-testid="stTable"] td, [data-testid="stTable"] th {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        border: 1px solid #EEEEEE !important;
    }
    
    .stDataFrame th, [data-testid="stTable"] th {
        background-color: #F5F5F5 !important;
    }
    
    /* Alert/message boxes */
    [data-testid="stAlert"] {
        background-color: #F8F9FA !important;
        color: #333333 !important;
        border: 1px solid #DDDDDD !important;
    }
    
    /* Progress bar with black style */
    [data-testid="stProgressBar"] {
        background-color: #EEEEEE !important;
    }
    [data-testid="stProgressBar"] > div {
        background-color: #000000 !important;
    }
    
    /* Code block styling */
    .stCode {
        background-color: #F8F9FA !important;
        color: #333333 !important;
        border: 1px solid #DDDDDD !important;
    }
    
    /* Sidebar navigation highlight */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] div:has(div:hover) {
        background-color: #F5F5F5 !important;
    }
    
    /* Checkbox accent color */
    [data-testid="stCheckbox"] {
        accent-color: #000000 !important;
    }
    
    /* Dropdown Selectors - add highlight on hover */
    .stSelectbox:hover, .stMultiSelect:hover {
        border-color: #000000 !important;
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Dropdown options */
    div[data-baseweb="select"] ul {
        background-color: #FFFFFF !important;
    }
    
    div[data-baseweb="select"] ul li {
        color: #333333 !important;
    }
    
    div[data-baseweb="select"] ul li:hover {
        background-color: #F5F5F5 !important;
    }
    
    /* Tabs styling */
    div[data-testid="stHorizontalBlock"] button[role="tab"] {
        background-color: #FFFFFF !important;
        color: #333333 !important;
    }
    
    div[data-testid="stHorizontalBlock"] button[role="tab"][aria-selected="true"] {
        background-color: #F5F5F5 !important;
        border-bottom-color: #000000 !important;
    }
    
    /* Metric indicators */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
    }
    [data-testid="stMetric"] label {
        color: #666666 !important;
    }
    [data-testid="stMetric"] svg {
        color: #000000 !important;
    }
    
    /* Make sure dataframes are readable with custom styling */
    .dataframe {
        font-family: 'Arial', sans-serif !important;
    }
    .dataframe th {
        background-color: #F5F5F5 !important;
        color: #333333 !important;
        font-weight: bold !important;
        border: 1px solid #DDDDDD !important;
        text-align: center !important;
    }
    .dataframe td {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        border: 1px solid #EEEEEE !important;
    }
    
    /* Charts and plots - enforce black and white theme */
    .js-plotly-plot, .plotly, .plot-container {
        background-color: #FFFFFF !important;
    }
    
    /* Target ALL plotly chart elements */
    .js-plotly-plot .plotly .main-svg,
    .js-plotly-plot .plotly .main-svg .gridlayer path,
    .js-plotly-plot .plotly .main-svg .zerolinelayer path,
    .js-plotly-plot .plotly .main-svg .barlayer .point path,
    .js-plotly-plot .plotly .main-svg .xy .scatter .points path,
    .js-plotly-plot .plotly .main-svg .choropleth path,
    .js-plotly-plot .plotly .main-svg .heatmaplayer path,
    .js-plotly-plot .plotly .main-svg .contourlayer path,
    .js-plotly-plot .plotly .main-svg .xaxislayer-above path,
    .js-plotly-plot .plotly .main-svg .yaxislayer-above path,
    .js-plotly-plot .plotly .main-svg .xaxislayer-above text,
    .js-plotly-plot .plotly .main-svg .yaxislayer-above text,
    .js-plotly-plot .plotly .main-svg .overaxes-above text,
    .js-plotly-plot .plotly .main-svg .trace text,
    .js-plotly-plot .plotly .main-svg .legend text,
    .js-plotly-plot .plotly .main-svg .annotation text {
        stroke: #000000 !important;
        fill: #000000 !important;
        color: #000000 !important;
    }
    
    /* Specifically target colored traces to make them black */
    .js-plotly-plot .plotly .scatterlayer .trace path,
    .js-plotly-plot .plotly .scatterlayer .trace .lines,
    .js-plotly-plot .plotly .barlayer .trace .bars path {
        stroke: #000000 !important;
        fill: #666666 !important;
    }
    
    /* Ensure all labels and headers everywhere are black */
    span.main-header, div.main-header, 
    .stHeadingContainer div, .stHeadingContainer span, .stHeadingContainer p,
    div.stHeadingContainer, header, div[role="heading"],
    h1.stTitle, h1, h2, h3, 
    [data-testid="stHeader"] div, 
    [data-testid="stHeader"] span,
    .stHeadingText,
    .main-heading, div.main-heading, span.main-heading {
        color: #000000 !important;
        background-color: transparent !important;
    }
    
    /* Force all links to be black */
    a, a:link, a:visited, a:hover, a:active,
    a span, a div, a * {
        color: #000000 !important;
        text-decoration: underline !important;
    }
    
    /* Force ALL Streamlit elements to use only black, white, and gray colors */
    /* Target ALL UI elements first */
    .element-container, .stButton, .stDownloadButton, .stFileUploader,
    .stMarkdown, .stText, .stHeader, .stAlert, .stInfo, .stSuccess,
    .stWarning, .stError, .stTabs, .stWidgetLabel, .stRadio, .stCheckbox,
    .stMultiselect, .stSelectbox, .stSlider, .stDateInput, .stTimeInput,
    .stNumberInput, .stTextInput, .stTextArea, .stDataFrame, .stTable,
    .stImage, .stAudio, .stVideo, .stProgress, .stSpinner, .stBalloon,
    .stTooltip, .stSidebar, .stForm, .stExpander, .stContainer,
    .stPage, .stFooter, .streamlit-expanderHeader, .streamlit-expanderContent,
    .stLinkButton, .css-pkbazv, .css-1qrvfrg, .css-3mmywe, .css-18ni7ap,
    .css-1djdyxw, div[role="button"], div[role="tab"], div[role="tablist"],
    .st-bc, .st-dk, .st-bq, .st-ci, .st-cn, .st-co, .st-cp, .st-dl, .st-dm, 
    .css-1tptmrg, [data-baseweb="notification"] span, .css-15zrgzn, .css-2trqyj,
    .css-a1lqcs, .css-zt5igj, .css-15tx938, [data-testid="stExpander"],
    div[data-testid="stImage"], div[data-testid="stMarkdown"], 
    div[data-testid="stForm"], div[data-testid="stNotificationContent"],
    div[data-testid="stNotificationIcon"], div[data-testid="stFormSubmitButton"],
    div[data-testid="baseButton-secondary"], div[data-testid="baseButton-primary"], 
    div[data-testid="stPageLink"], div[data-testid="stCaptionContainer"],
    div[data-testid="caption"], div[data-testid="stAppViewBlockContainer"],
    div[data-testid="stAppViewContainer"], div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"], div[data-testid="stToolbar"],
    div[data-testid="stDecoration"], span[data-testid="stWidgetLabel"] {
        color: #333333 !important;
    }
    
    /* Add specific override for links - force ALL links to be black */
    a, a:link, a:visited, a:active, a:hover, 
    .stLinkButton, .stLinkButton:hover, .stLinkButton:visited,
    a[href="https://streamlit.io"], 
    a[href="https://streamlit.io"]:hover, 
    a[href="https://streamlit.io"]:visited,
    div[data-testid="stSidebarUserContent"] a,
    [data-testid="stSidebarNav"] a,
    section[data-testid="stSidebar"] a,
    div[data-testid="stDecoration"] a,
    footer a {
        color: #000000 !important;
        text-decoration: underline !important;
    }
    
    /* Force specific important elements to be pure black */
    h1, h2, h3, h4, h5, h6, 
    div[data-testid="stHeader"], button[kind="primary"],
    [data-testid="baseButton-primary"] {
        color: #000000 !important;
    }
    
    /* Additional selectors to ensure no blue slips through */
    /* All elements with any style attributes containing blue colors */
    *[style*="color: rgb(49, 51, 63)"], *[style*="color: rgb(0, 104, 201)"],
    *[style*="color: rgb(14, 16, 26)"], *[style*="color: rgb(49, 51, 63)"],
    *[style*="color: rgb(250, 250, 250)"], *[style*="color: rgb(38, 39, 48)"],
    *[style*="color: rgb(80, 80, 80)"], *[style*="color: rgb(38, 39, 48)"],
    *[style*="color: blue"], *[style*="color: #1E90FF"], *[style*="color:#0000FF"],
    *[style*="color:#000080"], *[style*="color:#4169E1"], *[style*="color:#00BFFF"],
    *[style*="color:#87CEEB"], *[style*="color:#ADD8E6"], *[style*="color:#7B68EE"],
    *[style*="color:#9370DB"], *[style*="color: #0068C9"],
    div[style*="background-color: rgb(240, 242, 246)"], 
    span[style*="color: rgb(38, 39, 48)"] {
        color: #000000 !important;
    }
    
    /* Explicitly target the "Made with Streamlit" footer */
    footer, footer a, footer a:hover, .css-1lsmgbg,
    [data-testid="stFooter"], [data-testid="stFooter"] a, 
    [data-testid="stFooter"] span, small[data-testid="stFooter"], 
    div[data-testid="stFooter"], div[data-testid="stFooter"] a,
    div[data-testid="stFooter"] span {
        color: #000000 !important;
    }
    
    /* Subtle transition effect on hover */
    button, a, [data-testid="stWidgetLabel"] {
        transition: all 0.2s ease-in-out !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 1px dashed #DDDDDD !important;
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #F5F5F5 !important;
        color: #333333 !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 10px;
        background-color: #F5F5F5;
    }
    
    ::-webkit-scrollbar-track {
        background-color: #F5F5F5;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background-color: #DDDDDD;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background-color: #000000;
    }
    </style>
    """

def get_theme_css():
    """Return CSS styles for the active theme"""
    active_theme = get_active_theme()
    
    if active_theme == 'monograph':
        return get_monograph_css()
    elif active_theme == 'industrial':
        return get_industrial_css()
    return """
    <style>
    /* Matrix Theme CSS - COMPREHENSIVE OVERRIDE */
    /* Base background styles for ALL elements */
    .stApp, 
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarUserContent"],
    .block-container,
    div[data-layout="wide"],
    div[data-testid="stVerticalBlock"],
    div.element-container,
    div.row-widget,
    div.stTabs,
    div[data-baseweb="tab-panel"],
    div.streamlit-expanderHeader,
    div.streamlit-expanderContent,
    .stSelectbox, 
    .stMultiSelect,
    .stSlider, 
    [data-testid="stWidgetLabel"],
    [data-testid="stExpander"], 
    .stAlert, 
    .stInfo, 
    .stWarning, 
    .stError, 
    .stSuccess,
    .main-header,
    div[data-testid="stHorizontalBlock"] {
        background-color: #000000 !important;
        color: #00FF00 !important;
    }
    
    /* Main header styling */
    .main-header {
        background-color: #000000 !important;
        color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
        box-shadow: 0 0 10px #00FF00 !important;
        font-family: 'Courier New', monospace !important;
        padding: 1rem !important;
        border-radius: 5px !important;
    }
    
    .matrix-metric-container {
        background-color: #000000;
        border: 1px solid #00AA00;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 0 5px #00FF00;
    }
    
    .matrix-metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #00FF00;
        font-family: 'Courier New', monospace;
    }
    
    .matrix-metric-label {
        font-size: 14px;
        color: #00AA00;
        font-family: 'Courier New', monospace;
        margin-top: 5px;
    }
    
    .matrix-section-header {
        background-color: #001100;
        color: #00FF00;
        padding: 0.5rem 1rem;
        border: 1px solid #00AA00;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
        text-shadow: 0 0 5px #00FF00;
    }
    
    /* Style the tabs */
    div[data-testid="stHorizontalBlock"] > div[data-baseweb="tab-list"] {
        background-color: #000000 !important;
        border-bottom: 1px solid #00AA00 !important;
    }
    
    button[role="tab"] {
        background-color: #000000 !important;
        color: #00AA00 !important;
        border-bottom: 2px solid transparent !important;
        font-family: 'Courier New', monospace !important;
    }
    
    button[role="tab"][aria-selected="true"] {
        background-color: #000000 !important;
        color: #00FF00 !important;
        border-bottom: 2px solid #00FF00 !important;
        font-weight: bold !important;
    }
    
    /* Style the sidebar */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #00AA00 !important;
    }
    
    /* Style buttons */
    button[kind="primary"] {
        background-color: #001100 !important;
        border: 1px solid #00AA00 !important;
    }
    
    button[kind="secondary"] {
        background-color: #000000 !important;
        border: 1px solid #00AA00 !important;
        color: #00FF00 !important;
    }
    
    /* Style inputs */
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] input {
        background-color: #000000 !important;
        border: 1px solid #00AA00 !important;
        color: #00FF00 !important;
        border-radius: 4px !important;
    }
    
    /* Style dataframes */
    div[data-testid="stDataFrame"] {
        border: 1px solid #00AA00 !important;
        border-radius: 5px !important;
    }
    
    /* Style tooltips */
    div[role="tooltip"] {
        background-color: #000000 !important;
        border: 1px solid #00AA00 !important;
        color: #00FF00 !important;
        box-shadow: 0 0 5px #00FF00 !important;
    }
    
    /* Universal selector for ALL text elements */
    .stApp *, 
    [data-testid="stSidebar"] *,
    [data-testid="stHeader"] *, 
    .stTabs *, 
    [data-testid="stExpander"] *, 
    [data-testid="stWidgetLabel"] *,
    .stAlert *, 
    .stInfo *, 
    [data-testid="stMarkdownContainer"] * {
        color: #00FF00 !important; /* Matrix green text everywhere */
    }
    
    /* Strong selector for headings */
    h1, h2, h3, h4, h5, h6, 
    div[role="heading"], 
    [data-testid="stHeading"], 
    .stTitle, 
    .stHeader, 
    [data-testid="stHeader"] * {
        color: #00FF00 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Button styling - neon green with black text */
    [data-testid="baseButton-primary"] {
        background-color: #00FF00 !important;
        color: #000000 !important;
        border: 1px solid #00FF00 !important;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.7) !important;
    }
    
    /* Tables */
    .stDataFrame, 
    .stDataFrame th, 
    .stDataFrame td,
    .stTable, 
    .stTable th, 
    .stTable td,
    table, 
    th, 
    td, 
    tr {
        background-color: #000000 !important;
        color: #00FF00 !important;
        border-color: #00FF00 !important;
    }
    
    /* Force chart text to be Matrix green */
    .js-plotly-plot .plotly .main-svg text {
        fill: #00FF00 !important;
    }
    
    /* Ensure sidebar text is green */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div,
    /* Additional sidebar dropdown selectors */
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] option,
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="base-input"],
    [data-testid="stSidebar"] [data-baseweb="select-dropdown"],
    [data-testid="stSidebar"] [data-baseweb="popover"] div,
    [data-testid="stSidebar"] [data-baseweb="menu"] div,
    [data-testid="stSidebar"] [data-baseweb="select"] div, 
    [data-testid="stSidebar"] [data-baseweb="select"] input,
    [data-testid="stSidebar"] [role="listbox"],
    [data-testid="stSidebar"] [role="option"],
    [data-testid="stSidebar"] div[role="option"] {
        color: #00FF00 !important;
        background-color: #000000 !important;
    }
    
    /* Specifically target dropdown menus - very important for theme switching */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[data-baseweb="select-dropdown"],
    div[data-baseweb="select"] ul,
    div[data-baseweb="select"] li,
    div[role="listbox"],
    div[role="option"] {
        background-color: #000000 !important;
        color: #00FF00 !important;
        border-color: #00FF00 !important;
    }
    </style>
    """

def update_monograph_chart_theme(fig):
    """Apply the monograph theme to a plotly figure
    
    Args:
        fig: Plotly figure to apply theme to
    """
    # Clean white background
    bg_color = 'rgba(255,255,255,1)'
    
    # Monograph theme - black and gray
    grid_color = 'rgba(200,200,200,0.3)'  # Light gray grid
    line_color = '#000000'  # Black lines
    accent_color = '#000000'  # Black accent
    
    # Monograph colorway - strictly grayscale
    theme_colors = [
        '#000000', '#333333', '#666666', '#999999', '#CCCCCC',
        '#444444', '#777777', '#AAAAAA', '#1A1A1A', '#4D4D4D'
    ]
    
    # Monograph font colors
    title_color = '#000000'  # Black titles
    text_color = '#333333'  # Dark gray text
    
    # Apply strict monograph styling
    fig.update_layout(
        title_font=dict(
            color=title_color, 
            size=18,
            family="Arial, sans-serif"
        ),
        font=dict(
            color=text_color,
            family="Arial, sans-serif"
        ),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        legend=dict(
            font=dict(
                color=text_color, 
                size=12,
                family="Arial, sans-serif"
            )
        ),
        colorway=theme_colors,  # Use strictly grayscale colors
        hovermode="closest"
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor=grid_color, 
        zerolinecolor='#999999', 
        zeroline=True, 
        zerolinewidth=1,
        title_font=dict(family="Arial, sans-serif", color=title_color),
        tickfont=dict(family="Arial, sans-serif", color=text_color),
        color=text_color  # Ensure axis lines are black/gray
    )
    fig.update_yaxes(
        gridcolor=grid_color, 
        zerolinecolor='#999999', 
        zeroline=True, 
        zerolinewidth=1,
        title_font=dict(family="Arial, sans-serif", color=title_color),
        tickfont=dict(family="Arial, sans-serif", color=text_color),
        color=text_color  # Ensure axis lines are black/gray
    )
    
    # Force all traces to use appropriate theme colors - much more aggressive approach
    for i, trace in enumerate(fig.data):
        # Determine which grayscale color to use based on index
        color_index = i % len(theme_colors)
        gray_color = theme_colors[color_index]
        
        # Force color change for ALL trace elements
        if hasattr(trace, 'marker'):
            if hasattr(trace.marker, 'color'):
                # Only set scalar colors, not arrays (preserve heatmaps, etc.)
                try:
                    if not isinstance(trace.marker.color, (list, np.ndarray)):
                        trace.marker.color = gray_color
                except:
                    trace.marker.color = gray_color
                    
            if hasattr(trace.marker, 'line'):
                try:
                    trace.marker.line.color = '#FFFFFF'
                except:
                    pass
                    
        # Force line colors
        if hasattr(trace, 'line'):
            try:
                trace.line.color = gray_color
            except:
                pass
                
        # Force bar colors
        if trace.type == 'bar':
            try:
                trace.marker.color = gray_color
            except:
                pass
                
        # Handle pie charts
        if trace.type == 'pie':
            trace.marker.colors = theme_colors
            
        # Force scatter colors
        if trace.type == 'scatter':
            try:
                trace.marker.color = gray_color
            except:
                pass
        
        # Force box plot colors
        if trace.type in ['box', 'violin']:
            try:
                trace.marker.color = gray_color
                trace.line.color = gray_color
            except:
                pass
                
    # Extra handling for specific chart types (e.g., heatmaps)
    for trace in fig.data:
        if hasattr(trace, 'colorscale'):
            try:
                # Replace with grayscale colorscale
                trace.colorscale = [[0, '#FFFFFF'], [0.5, '#999999'], [1, '#000000']]
            except:
                pass
    
    return fig

def update_chart_theme(fig):
    """Apply the appropriate theme to a plotly figure based on active theme
    
    Args:
        fig: Plotly figure to apply theme to
    """
    active_theme = get_active_theme()
    
    # If monograph theme is active, use its chart theme function
    if active_theme == 'monograph':
        return update_monograph_chart_theme(fig)
    # If industrial theme is active, use its chart theme function
    elif active_theme == 'industrial':
        return update_industrial_chart_theme(fig)
    
    # Otherwise apply Matrix theme
    fonts = get_theme_fonts()
    
    # Pure black background
    bg_color = 'rgba(0,0,0,1)'
    
    # Matrix theme - neon green
    grid_color = 'rgba(0,255,0,0.2)'  # Green grid
    line_color = '#00FF00'  # Neon green lines
    accent_color = '#00FF00'  # Green accent
    
    # Matrix colorway
    theme_colors = [
        '#00FF00', '#33FF33', '#66FF66', '#00CC00', '#00FF33',
        '#33FF00', '#66FF33', '#00DD00', '#00BB00', '#009900'
    ]
    
    # Check if this is a pie chart (to preserve custom font colors)
    # Instead of trying to detect pie chart type, we'll directly check if the figure was created by create_animated_pie_chart
    # This is a safer approach as different Plotly figure objects have different structures
    is_pie_chart = False
    try:
        # If we have a layout.annotations with 'pie' in their text, it's likely a pie chart
        if hasattr(fig, 'layout') and hasattr(fig.layout, 'annotations'):
            for annotation in fig.layout.annotations:
                if hasattr(annotation, 'text') and 'pie' in str(annotation.text).lower():
                    is_pie_chart = True
                    break
        
        # Also check for specific pie chart properties in data
        for trace in fig.data:
            if hasattr(trace, 'type') and getattr(trace, 'type') == 'pie':
                is_pie_chart = True
                break
            if hasattr(trace, 'hole') or hasattr(trace, 'values') or hasattr(trace, 'labels'):
                is_pie_chart = True
                break
    except:
        # If any error occurs during detection, assume it's not a pie chart
        is_pie_chart = False
    
    # Matrix font colors
    title_color = '#FFFFFF'  # White titles
    text_color = '#000000' if is_pie_chart else '#00FF00'  # Black text for pie charts, green text otherwise
    
    # Apply styling - for pie charts, use black text for better readability
    layout_update = {
        'title_font': dict(
            color=title_color, 
            size=fonts['title']['size'] if isinstance(fonts, dict) and 'title' in fonts and 'size' in fonts['title'] else 16,
            family="Courier New, monospace"  # Force monospace
        ),
        'paper_bgcolor': bg_color,
        'plot_bgcolor': bg_color,
    }
    
    # Only update font color if not a pie chart, otherwise keep the custom black color
    if not is_pie_chart:
        layout_update['font'] = dict(
            color=text_color,
            family="Courier New, monospace"  # Force monospace
        )
        layout_update['legend'] = dict(
            font=dict(
                color=text_color, 
                size=12,
                family="Courier New, monospace"  # Force monospace
            )
        )
    
    fig.update_layout(**layout_update)
    
    # Update axes
    fig.update_xaxes(
        gridcolor=grid_color, 
        zerolinecolor=line_color, 
        zeroline=True, 
        zerolinewidth=2,
        title_font=dict(family="Courier New, monospace"),
        tickfont=dict(family="Courier New, monospace", color=text_color)
    )
    fig.update_yaxes(
        gridcolor=grid_color, 
        zerolinecolor=line_color, 
        zeroline=True, 
        zerolinewidth=2,
        title_font=dict(family="Courier New, monospace"),
        tickfont=dict(family="Courier New, monospace", color=text_color)
    )
    
    # Apply theme colorway
    fig.update_layout(colorway=theme_colors)
    
    # Add subtle effect to the plot with slightly glowing lines
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