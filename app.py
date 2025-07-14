import streamlit as st
import pandas as pd
import os
import io
import datetime
import toml
import logging
from utils.standardized_processor import extract_standard_data, validate_data
from utils.visualization import plot_overview_chart
from utils.unified_database import save_uploaded_data, load_saved_dataset, list_saved_datasets, delete_dataset
from utils.report_processor_manager import process_report
from hidden_pages import customized_dashboard
from utils.direct_tab_fix import direct_fix_component
# Import the water treatment theme (modified for theme switching)
from water_treatment_theme import get_palette, update_chart_theme, is_dark_theme
# Import authentication utilities
from utils.auth import is_authenticated, logout, initialize_admin
from pages.auth_pages import app as display_auth_page
# Import session management utilities
from utils.session_manager import initialize_session_state, reload_datasets_if_needed, update_loaded_report_id, remove_loaded_report_id, update_combined_data

# Run database persistence fixes at startup
try:
    from run_db_fixes import run_all_fixes
    run_all_fixes()
    logging.info("Successfully ran database persistence fixes at startup")
except Exception as e:
    logging.error(f"Error running database fixes: {str(e)}")

# Function to delete all reports and clean session state
def delete_all_data():
    """Delete all datasets and clear session state"""
    # Get all reports from the database
    reports = list_saved_datasets()
    
    # Count deleted datasets
    deleted_count = 0
    
    # Delete each report
    for report in reports:
        if 'id' in report:
            success = delete_dataset(report['id'])
            if success:
                deleted_count += 1
    
    # Clear session state for data
    if 'chemical_spend_data' in st.session_state:
        del st.session_state.chemical_spend_data
    if 'chemical_spend_filename' in st.session_state:
        del st.session_state.chemical_spend_filename
    if 'po_data' in st.session_state:
        del st.session_state.po_data
    if 'non_po_data' in st.session_state:
        del st.session_state.non_po_data
    if 'data' in st.session_state:
        del st.session_state.data
        
    # Clear session manager's report IDs
    if 'loaded_report_ids' in st.session_state:
        st.session_state.loaded_report_ids = {}
    
    # Return number of deleted reports
    return deleted_count

# Set page configuration
st.set_page_config(
    page_title="CST - Inframark",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Allow sidebar to be accessible but initially collapsed
st.markdown("""
<style>
    /* Sidebar is available but collapsed initially */
    
    /* Ensure main content uses full width */
    .main .block-container {
        max-width: 100% !important; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# The redirect mechanism has been replaced with direct Streamlit buttons 
# that use st.switch_page() for more reliable navigation

# Import the full theme CSS
from water_treatment_theme import get_theme_css, get_active_theme

# Get the current theme for CSS styling
theme_mode = "dark" if is_dark_theme() else "light"
active_theme = get_active_theme()  # This will be either 'matrix' or 'monograph'

# Apply the appropriate theme CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Add custom CSS for supplier elements with matrix theme styling
st.markdown("""
<style>
/* Matrix theme styling for multiselect boxes - black background with bright green text */
.st-bg div[data-testid="stMultiSelect"] span {
    color: #00FF00 !important;
    background-color: #000000 !important;
}

/* Target all multiselect elements */
div[data-testid="stMultiSelect"] span {
    color: #00FF00 !important;
    background-color: #000000 !important;
}

/* Make dropdown items match the theme */
div[role="listbox"] div[role="option"] {
    color: #00FF00 !important;
    background-color: #121212 !important;
}

/* Fix the selected items (chips) */
div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {
    background-color: #000000 !important;
    border: 1px solid #00FF00 !important;
}

div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span {
    color: #00FF00 !important;
}

/* Make supplier text in tables match the theme */
.stDataFrame td:nth-child(2), 
.stDataFrame th:nth-child(2) {
    color: #00FF00 !important;
}

/* Hover effect for dropdown options */
div[role="listbox"] div[role="option"]:hover {
    background-color: #1E1E1E !important;
}
</style>
""", unsafe_allow_html=True)

# Add any additional custom CSS based on active theme
if active_theme == 'matrix':
    # Matrix theme additional custom CSS
    st.markdown("""
    <style>
        /* Header styling - Matrix dark mode */
        .main-header {
            background-color: #000000;
            padding: 1rem;
            border-radius: 0.5rem;
            color: #00FF00;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
            font-family: 'Courier New', monospace;
            border: 1px solid #00FF00;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 10px #00FF00;
        }
        
        /* Improved contrast between headers and body text - Matrix dark mode */
        h1, h2, h3, h4, h5, h6 {
            font-weight: 700 !important;
            color: #00FF00 !important; /* Matrix green for headers */
            letter-spacing: -0.01em !important;
            margin-top: 0.8em !important;
            margin-bottom: 0.4em !important;
            font-family: 'Courier New', monospace !important;
        }
        
        /* Header size hierarchy - Matrix dark mode */
        h1 {
            font-size: 2.5rem !important;
            border-bottom: 2px solid #00FF00 !important;
            padding-bottom: 0.3em !important;
            text-shadow: 0 0 5px #00FF00 !important;
        }
        
        h2 {
            font-size: 2rem !important;
            border-bottom: 1px solid #00FF00 !important;
            padding-bottom: 0.2em !important;
        }
        
        h3 {
            font-size: 1.5rem !important;
            color: #00FF00 !important;
        }
        
        h4 {
            font-size: 1.25rem !important;
            color: #00FF00 !important;
        }
        
        /* Metric cards with improved styling - dark mode */
        div.metric-card {
            background-color: #000000 !important;
            border-radius: 0.5rem !important;
            padding: 1rem !important;
            box-shadow: 0 0 10px rgba(0,255,0,0.3) !important;
            margin-bottom: 1rem !important;
            border-left: 4px solid #00FF00 !important;
            font-family: 'Courier New', monospace !important;
        }
        
        div.metric-card h4 {
            margin-top: 0 !important;
            color: #00FF00 !important;
            font-weight: 600 !important;
            margin-bottom: 0.5rem !important;
            font-family: 'Courier New', monospace !important;
        }
        
        /* Main header additional styling - Matrix theme */
        .main-header {
            margin-bottom: 1.5rem !important;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.6) !important;
            border: 1px solid #00FF00 !important;
            letter-spacing: 2px !important;
        }
        
        /* Card styling for metrics - Matrix dark mode */
        .metric-card {
            background-color: #000000;
            border-radius: 0.5rem;
            padding: 1rem;
            border-left: 5px solid #00FF00;
            margin-bottom: 1rem;
            box-shadow: 0 0 8px rgba(0, 255, 0, 0.4);
            font-family: 'Courier New', monospace;
        }
        
        /* Table styling - Matrix dark mode */
        .dataframe {
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 1.1rem !important;
            font-family: 'Courier New', monospace !important;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
            border: 1px solid #003300;
        }
        .dataframe thead th {
            background-color: #003300;
            color: #00FF00;
            text-align: left;
            font-size: 1.2rem !important;
            padding: 0.7rem !important;
            font-weight: bold;
        }
        .dataframe tbody tr:nth-of-type(even) {
            background-color: #000000;
        }
        .dataframe tbody tr:nth-of-type(odd) {
            background-color: #001100;
        }
        .dataframe tbody tr:hover {
            background-color: #002200;
            color: #00FF00 !important;
            text-shadow: 0 0 5px #00FF00;
        }
        
        /* Metric values styling for better visibility - Matrix theme */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: #00FF00 !important;
            font-family: 'Courier New', monospace !important;
            text-shadow: 0 0 10px #00FF00;
        }
        
        /* Metric labels styling for better readability - Matrix theme */
        [data-testid="stMetricLabel"] {
            font-size: 1.1rem !important;
            color: #00FF00 !important;
            font-family: 'Courier New', monospace !important;
        }
        
        /* Button styling - Matrix dark mode */
        .stButton button {
            background-color: #000000;
            color: #00FF00;
            border: 1px solid #00FF00;
            border-radius: 0.3rem;
            transition: all 0.3s;
            font-family: 'Courier New', monospace !important;
            text-transform: uppercase;
            box-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
        }
        .stButton button:hover {
            background-color: #001500;
            color: #00FF00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.8);
            text-shadow: 0 0 5px #00FF00;
        }
        
        /* Tab styling - Matrix dark mode */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #000000 !important;
            color: #00FF00 !important;
            border-radius: 4px 4px 0 0;
            border: 1px solid #003300;
            padding: 10px 16px;
            font-weight: 600;
            font-family: 'Courier New', monospace !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #003300 !important;
            color: #00FF00 !important;
            border: 1px solid #00FF00;
            box-shadow: 0 0 5px #00FF00;
        }
        
        /* Main tab containers (fixing the gray tabs) */
        div[data-testid="stHorizontalBlock"] button[role="tab"] {
            background-color: #000000 !important;
            color: #00FF00 !important;
            border: 1px solid #003300 !important;
            border-radius: 4px !important;
            font-family: 'Courier New', monospace !important;
            margin: 0 2px !important;
        }
        
        div[data-testid="stHorizontalBlock"] button[role="tab"][aria-selected="true"] {
            background-color: #003300 !important;
            color: #00FF00 !important;
            border: 1px solid #00FF00 !important;
            box-shadow: 0 0 5px rgba(0, 255, 0, 0.5) !important;
            text-shadow: 0 0 2px #00FF00 !important;
        }
        
        div[data-testid="stHorizontalBlock"] div[role="tablist"] {
            background-color: #000000 !important;
            border-bottom: 1px solid #003300 !important;
        }
        
        /* Section title styling in Matrix dark mode */
        .section-title {
            color: #00FF00 !important;
            font-weight: 600 !important;
            background-color: #000000;
            padding: 8px 15px;
            border-radius: 4px;
            margin-bottom: 10px;
            border: 1px solid #00FF00;
            text-transform: uppercase;
            font-family: 'Courier New', monospace !important;
        }
        
        /* Analysis titles - Matrix dark mode */
        .analysis-title {
            color: #00FF00 !important;
            background-color: #000000;
            padding: 8px 12px;
            border-radius: 4px;
            font-weight: 600;
            margin: 10px 0;
            border: 1px solid #00FF00;
            box-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
            font-family: 'Courier New', monospace !important;
        }
        
        /* Info box styling - Matrix dark mode */
        .stAlert {
            border-radius: 0.5rem;
            border-left: 5px solid #00FF00;
            background-color: #000000 !important;
            box-shadow: 0 0 8px rgba(0, 255, 0, 0.3);
            font-family: 'Courier New', monospace !important;
        }
        
        /* Make text more readable in Matrix dark mode */
        p, span, div, label {
            color: #00FF00 !important;
            font-family: 'Courier New', monospace !important;
        }
        
        /* Multiselect dropdown styling - Matrix theme */
        .stMultiSelect [data-baseweb="select"] {
            background-color: #000000 !important;
            color: #00FF00 !important;
            border: 1px solid #00FF00 !important;
            font-family: 'Courier New', monospace !important;
        }
        
        .stMultiSelect [data-baseweb="tag"] {
            background-color: #001500 !important;
            color: #00FF00 !important;
            border: 1px solid #00FF00 !important;
            box-shadow: 0 0 3px rgba(0, 255, 0, 0.3) !important;
        }
        
        .stMultiSelect [data-baseweb="select"] input {
            color: #00FF00 !important;
            font-family: 'Courier New', monospace !important;
        }
        
        .stMultiSelect [data-baseweb="popover"] {
            background-color: #000000 !important;
            border: 1px solid #00FF00 !important;
        }
        
        .stMultiSelect [data-baseweb="menu"] {
            background-color: #000000 !important;
        }
        
        .stMultiSelect [data-baseweb="option"] {
            color: #00FF00 !important;
            background-color: #000000 !important;
        }
        
        .stMultiSelect [data-baseweb="option"]:hover {
            background-color: #00FF00 !important;
            box-shadow: 0 0 8px rgba(0, 255, 0, 0.8) !important;
            color: #000000 !important;
            font-weight: bold !important;
        }
        
        /* Regular selectbox styling - Matrix theme */
        .stSelectbox [data-baseweb="select"] {
            background-color: #000000 !important;
            color: #00FF00 !important;
            border: 1px solid #00FF00 !important;
            font-family: 'Courier New', monospace !important;
        }
        
        .stSelectbox [data-baseweb="popover"] {
            background-color: #000000 !important;
            border: 1px solid #00FF00 !important;
        }
        
        .stSelectbox [data-baseweb="menu"] {
            background-color: #000000 !important;
        }
        
        .stSelectbox [data-baseweb="option"] {
            color: #00FF00 !important;
            background-color: #000000 !important;
        }
        
        .stSelectbox [data-baseweb="option"]:hover {
            background-color: #00FF00 !important;
            box-shadow: 0 0 8px rgba(0, 255, 0, 0.8) !important;
            color: #000000 !important;
            font-weight: bold !important;
        }
        
        /* Special styling for saved report dropdown in sidebar */
        [key="saved_report_dropdown"] [data-baseweb="option"]:hover,
        [key*="saved_report_dropdown_"] [data-baseweb="option"]:hover {
            background-color: #00FF00 !important;
            box-shadow: 0 0 10px rgba(0, 255, 0, 1) !important;
            color: #000000 !important;
            font-weight: bold !important;
            border-radius: 4px !important;
            transition: all 0.2s ease !important;
        }
    </style>
    """, unsafe_allow_html=True)

else:
    # Monograph theme additional custom CSS
    st.markdown("""
    <style>
        /* Header styling - Monograph theme (clean white with blue accents) */
        .main-header {
            background-color: #FFFFFF;
            padding: 1rem;
            border-radius: 0.5rem;
            color: #000000;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            font-family: 'Arial', sans-serif;
            border: 1px solid #E6E6E6;
        }
        
        /* Improved contrast between headers and body text */
        h1, h2, h3, h4, h5, h6 {
            font-weight: 700 !important;
            color: #00334d !important; /* Darker blue for headers */
            letter-spacing: -0.01em !important;
            margin-top: 0.8em !important;
            margin-bottom: 0.4em !important;
        }
        
        /* Header size hierarchy */
        h1 {
            font-size: 2.5rem !important;
            border-bottom: 2px solid #0077B6 !important;
            padding-bottom: 0.3em !important;
        }
        
        h2 {
            font-size: 2rem !important;
            border-bottom: 1px solid #0077B6 !important;
            padding-bottom: 0.2em !important;
        }
        
        h3 {
            font-size: 1.5rem !important;
            color: #00557c !important;
        }
        
        h4 {
            font-size: 1.25rem !important;
            color: #006699 !important;
        }
        
        /* Body text styling for better readability */
        p, div, label, span, .stSelectbox, .stTextInput, .stButton, .stMarkdown, .stDataFrame {
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
        }
        
        /* Increase base font size */
        html {
            font-size: 18px !important;
        }
        
        /* Larger text for important UI elements */
        .stButton>button, .stSelectbox>div>div, .stTextInput>div>div {
            font-size: 1.15rem !important;
        }
        
        /* Metric cards with improved styling */
        div.metric-card {
            background-color: #f8f9fa !important;
            border-radius: 0.5rem !important;
            padding: 1rem !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
            margin-bottom: 1rem !important;
            border-left: 4px solid #0077B6 !important;
        }
        
        div.metric-card h4 {
            margin-top: 0 !important;
            color: #00334d !important;
            font-weight: 600 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Main header additional styling */
        .main-header {
            margin-bottom: 1.5rem !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Card styling for metrics */
        .metric-card {
            background-color: #E0F2F1;
            border-radius: 0.5rem;
            padding: 1rem;
            border-left: 5px solid #0077B6;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Table styling */
        .dataframe {
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 1.1rem !important; /* Increased font size */
            font-family: sans-serif;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .dataframe thead th {
            background-color: #0077B6;
            color: white;
            text-align: left;
            font-size: 1.2rem !important; /* Larger header text */
            padding: 0.7rem !important; /* More padding for better spacing */
        }
        .dataframe tbody tr:nth-of-type(even) {
            background-color: #E0F2F1;
        }
        .dataframe tbody tr:hover {
            background-color: #d4ecec;
        }
        
        /* Metric values styling for better visibility */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
        
        /* Metric labels styling for better readability */
        [data-testid="stMetricLabel"] {
            font-size: 1.1rem !important;
        }
        
        /* Button styling */
        .stButton button {
            background-color: #0077B6;
            color: white;
            border-radius: 0.3rem;
            transition: all 0.3s;
        }
        .stButton button:hover {
            background-color: #005f92;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        /* Info box styling */
        .stAlert {
            border-radius: 0.5rem;
            border-left: 5px solid #0077B6;
        }
    </style>
    """, unsafe_allow_html=True)

# Session state initialization
initialize_session_state()

# After initialization, check if we need to reload any datasets
# This ensures data persists across page refreshes
reload_datasets_if_needed()

# Check user authentication before loading any UI components
# This ensures authentication is required for all functionality
print("DEBUG - Checking authentication status...")
authenticated = is_authenticated()
print(f"DEBUG - Authentication result: {authenticated}")
if 'user' in st.session_state:
    print(f"DEBUG - User in session state: {st.session_state.user}")
    print(f"DEBUG - Current page: {st.session_state.get('current_page', 'unknown')}")
if 'persistent_auth' in st.session_state:
    print(f"DEBUG - persistent_auth in session state: {st.session_state.persistent_auth}")
if authenticated and 'current_page' not in st.session_state:
    # Make sure we have a default page when authenticated
    print("DEBUG - Setting current_page to main after authentication")
    st.session_state.current_page = "main"

if not authenticated:
    # First, initialize the database in case it's needed for user authentication
    from utils.unified_database import init_database
    init_database()
    
    # Display login page only if not authenticated
    print("DEBUG - Displaying auth page")
    display_auth_page()
    
    # Stop execution here to prevent displaying the main app
    st.stop()
else:
    print("DEBUG - User is authenticated, proceeding with main app")

# Once we get here, user is authenticated
# Inject custom JavaScript to fix tab styling
direct_fix_component()

# Main title with custom styling based on active theme
active_theme = get_active_theme()
if active_theme == 'matrix':
    st.markdown('<h1 class="main-header" style="background-color: #000000; color: #00FF00; border: 1px solid #00FF00; box-shadow: 0 0 10px #00FF00; font-family: \'Courier New\', monospace;">🧪 Chemical Dashboard</h1>', unsafe_allow_html=True)
else:
    st.markdown('<h1 class="main-header" style="background-color: #FFFFFF; color: #000000; border: 1px solid #E6E6E6; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif;">🧪 Chemical Dashboard</h1>', unsafe_allow_html=True)
# Subtitle with appropriate styling based on theme
if active_theme == 'matrix':
    st.markdown("""
    <div style="padding: 0.5rem; margin-bottom: 2rem; text-align: center; color: #00FF00; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #00FF00;">
        <h3>Upload and analyze chemical spend data across water and wastewater treatment facilities</h3>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="padding: 0.5rem; margin-bottom: 2rem; text-align: center; color: #000000; font-family: Arial, sans-serif;">
        <h3>Upload and analyze chemical spend data across water and wastewater treatment facilities</h3>
    </div>
    """, unsafe_allow_html=True)

# Add buttons for various dashboard features at the top of the main interface
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    # Create a centered Report Manager button with appropriate styling based on theme
    if st.button("📊 Report Manager", key="report_manager_btn", use_container_width=True):
        # Navigate to the Report Manager page
        import streamlit as st
        st.switch_page("pages/report_manager.py")
        
with col2:
    # Unit cost analysis feature has been removed
    pass  # Empty placeholder to maintain layout

# Note: Chemical Spend Trend Analysis button removed as it's now available as a dedicated tab

# Supplier Pricing and Cost Savings functionality has been completely removed from this application

# No "Delete All Data" button - removed as per user request

# Initialize database (again, in case it's needed for the main app)
from utils.unified_database import init_database
init_database()

# Function to get the user's theme preference
# Theme management function moved to utils/theme_utils.py
from utils.theme_utils import get_user_theme

# Function to write theme to water_treatment_theme.py file
def write_theme_to_file(theme_mode='dark', color_theme='matrix'):
    """Write the theme preferences to the file
    
    Args:
        theme_mode: 'dark' or 'light' (always 'dark')
        color_theme: Theme identifier (always 'matrix')
    """
    # Override any input to ensure Matrix theme is always used
    color_theme = 'matrix'
    # For now, we'll keep theme_mode as 'dark' regardless of user choice
    # Since both our themes work best with dark mode
    
    # First update the user's theme in the database
    if is_authenticated() and 'user' in st.session_state:
        if 'theme' not in st.session_state.user or st.session_state.user['theme'] != color_theme:
            # Update the user's theme in the database
            from utils.auth import update_user_theme
            update_user_theme(st.session_state.user['id'], color_theme)
            
            # Update the session state user object with new theme
            st.session_state.user['theme'] = color_theme
            
            # Update color_theme in session state
            st.session_state.color_theme = color_theme
            
            # Apply the Matrix theme CSS
            from water_treatment_theme import get_theme_css
            st.markdown(get_theme_css(), unsafe_allow_html=True)
            st.success("Matrix theme applied successfully!")
            
            # Force rerun to fully apply the new theme
            st.rerun()

# Add user controls to sidebar at the top
with st.sidebar:
    st.markdown("---")
    st.markdown(f"**Logged in as:** {st.session_state.user['username']}")
    
    # Theme selection - only for admin users
    if st.session_state.user["role"] == "admin":
        st.markdown("### Theme Settings")
        theme_options = {
            "matrix": "Matrix Theme (Dark)",
            "industrial": "Industrial Theme (Light)"
        }
        selected_theme = st.selectbox(
            "Select Theme:",
            options=list(theme_options.keys()),
            format_func=lambda x: theme_options[x],
            index=0 if get_active_theme() == 'matrix' else 1,
            key="theme_selector"
        )
    else:
        # Non-admin users can only use Industrial theme
        selected_theme = "industrial"
    
    # Update the theme if changed and force a rerun
    if (('theme_selector' in st.session_state and st.session_state.color_theme != selected_theme) or 
        (st.session_state.color_theme != selected_theme)):
        # Apply temporary CSS immediately to avoid white flash
        if selected_theme == 'matrix':
            # Force black background and green text for Matrix theme
            st.markdown("""
            <style>
            /* Immediate Matrix theme override */
            body, .stApp, [data-testid="stAppViewContainer"], 
            [data-testid="stHeader"], [data-testid="stToolbar"], 
            [data-testid="stSidebar"], [data-testid="stSidebarUserContent"],
            .block-container, div[data-layout="wide"],
            div[data-testid="stVerticalBlock"], div.element-container,
            div.row-widget, div.stTabs, div[data-baseweb="tab-panel"],
            div.streamlit-expanderHeader, div.streamlit-expanderContent,
            .stSelectbox, .stMultiSelect, .stSlider, [data-testid="stWidgetLabel"],
            [data-testid="stExpander"], .stAlert, .stInfo, .stWarning,
            .stError, .stSuccess, .main-header, div[data-testid="stHorizontalBlock"],
            /* Dropdown and list boxes */
            div[data-baseweb="popover"], div[data-baseweb="menu"],
            div[data-baseweb="select-dropdown"], div[data-baseweb="select"] ul,
            div[data-baseweb="select"] li, div[role="listbox"],
            div[role="option"], .stApp * {
                background-color: #000000 !important;
                color: #00FF00 !important;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Update the session state
        st.session_state.color_theme = selected_theme
        
        # Update the user's theme preference in the database
        if is_authenticated() and 'user' in st.session_state:
            from utils.auth import update_user_theme
            update_user_theme(st.session_state.user['id'], selected_theme)
            st.session_state.user['theme'] = selected_theme
        
        # Force a page rerun to fully apply the new theme
        st.rerun()
        
        # This code below will only execute if rerun fails
        # Add immediate CSS override to prevent flashing of old theme
        if selected_theme == 'industrial':
            st.markdown("""
            <style>
            /* COMPREHENSIVE INDUSTRIAL THEME OVERRIDE */
            /* Consistent background for ALL elements - LIGHT THEME */
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
            .main-header {
                background-color: #F5F5F5 !important;
                color: #000000 !important; /* BLACK text */
            }
            
            /* Make KPI cards have white background in industrial theme */
            div.element-container div.row-widget.stButton, 
            div.element-container div[data-testid="stHorizontalBlock"],
            div.element-container [data-testid="stMetricValue"],
            div.element-container [data-testid="stMetricLabel"] {
                background-color: #FFFFFF !important;
                color: #000000 !important;
                border-radius: 8px !important;
                border: 1px solid rgba(249, 115, 22, 0.2) !important;
                box-shadow: 0 2px 6px rgba(249, 115, 22, 0.1) !important;
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
                color: #000000 !important; /* BLACK text everywhere */
            }
            
            /* Header styling */
            .main-header {
                background-color: #FFFFFF !important;
                color: #000000 !important; /* BLACK text */
                border-left: 4px solid #F97316 !important;
                border-top: none !important;
                border-right: none !important;
                border-bottom: none !important;
                box-shadow: 0 4px 6px rgba(15, 23, 42, 0.1) !important;
                font-family: 'Inter', 'Arial', sans-serif !important;
            }
            
            /* Button styling - primary buttons should remain orange with WHITE text */
            [data-testid="baseButton-primary"] {
                background-color: #F97316 !important;
                color: #FFFFFF !important;
            }
            
            /* Strong selector for headings */
            h1, h2, h3, h4, h5, h6, 
            div[role="heading"], 
            [data-testid="stHeading"], 
            .stTitle, 
            .stHeader, 
            [data-testid="stHeader"] * {
                color: #000000 !important;
                font-family: 'Inter', 'Arial', sans-serif !important;
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
                color: #000000 !important;
                background-color: #FFFFFF !important;
            }
            
            /* Chart backgrounds */
            .js-plotly-plot, 
            .plotly, 
            .plot-container {
                background-color: #FFFFFF !important;
            }
            
            /* Card buttons in industrial theme should be styled appropriately */
            div[data-testid="stButton"] button {
                background-color: #FFFFFF !important;
                border: 1px solid rgba(249, 115, 22, 0.3) !important;
                color: #000000 !important;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
            }
            
            div[data-testid="stButton"] button:hover {
                border: 1px solid #F97316 !important;
                box-shadow: 0 4px 8px rgba(249, 115, 22, 0.2) !important;
                transform: translateY(-2px);
            }
            
            /* Links - these should be orange instead of black */
            a, a:link, a:visited {
                color: #F97316 !important;
            }
            
            /* All inline styled elements that might have color */
            *[style*="color:"] {
                color: #000000 !important;
            }
            
            /* Extreme override for any element with specific RGB values */
            [style*="color: rgb(49, 51, 63)"], 
            [style*="color: rgb(0, 104, 201)"],
            [style*="color: rgb(14, 16, 26)"], 
            [style*="color: rgb(49, 51, 63)"],
            [style*="color: rgb(70, 103, 167)"], 
            [style*="color: rgb(38, 39, 48)"],
            [style*="color: rgb(22, 23, 24)"], 
            [style*="color: rgb(26, 26, 27)"],
            [style*="color: rgb(88, 88, 89)"], 
            [style*="color: rgb(59, 65, 68)"],
            [style*="color: rgb(107, 119, 140)"], 
            [style*="color: rgb(135, 135, 135)"] {
                color: #000000 !important;
            }
            
            /* Force chart text to be black */
            .js-plotly-plot .plotly .main-svg text {
                fill: #000000 !important;
            }
            
            /* Ensure sidebar text is black */
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
            [data-testid="stSidebar"] h1, 
            [data-testid="stSidebar"] h2, 
            [data-testid="stSidebar"] h3, 
            [data-testid="stSidebar"] h4,
            [data-testid="stSidebar"] label, 
            [data-testid="stSidebar"] div {
                color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
            /* COMPREHENSIVE MATRIX THEME OVERRIDE - Pure Black Background */
            /* Base backgrounds for ALL elements */
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
            
            /* Metrics and card components */
            div.element-container [data-testid="stMetricValue"],
            div.element-container [data-testid="stMetricLabel"],
            div.element-container div.row-widget.stButton,
            div.element-container [data-testid="stMetricDelta"] {
                background-color: #000000 !important;
                color: #00FF00 !important;
            }
            
            /* Chart backgrounds */
            .js-plotly-plot, 
            .plotly, 
            .plot-container {
                background-color: #000000 !important;
            }
            
            /* Force chart text to be Matrix green */
            .js-plotly-plot .plotly .main-svg text {
                fill: #00FF00 !important;
            }
            
            /* Matrix header styling */
            .main-header {
                background-color: #000000 !important;
                color: #00FF00 !important;
                border: 1px solid #00FF00 !important;
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.7) !important;
                font-family: 'Courier New', monospace !important;
                text-transform: uppercase !important;
                letter-spacing: 2px !important;
                text-shadow: 0 0 10px #00FF00 !important;
            }
            
            /* Button styling - neon green with black text */
            [data-testid="baseButton-primary"] {
                background-color: #00FF00 !important;
                color: #000000 !important;
                border: 1px solid #00FF00 !important;
                box-shadow: 0 0 10px rgba(0, 255, 0, 0.7) !important;
            }
            
            /* Card buttons in Matrix theme */
            div[data-testid="stButton"] button {
                background-color: #001100 !important;
                border: 1px solid #00FF00 !important;
                color: #00FF00 !important;
                box-shadow: 0 0 8px rgba(0, 255, 0, 0.7) !important;
            }
            
            div[data-testid="stButton"] button:hover {
                background-color: #003300 !important;
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.9) !important;
                transform: translateY(-2px);
            }
            
            /* Tables - ensure text is matrix green */
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
            </style>
            """, unsafe_allow_html=True)
            
        # Force reload to fully apply the theme
        st.rerun()
    
    # Feature Navigation Section
    st.markdown("### Features")
    
    # Supplier Pricing and Cost Savings functionality has been completely removed from this application
    
    # Admin Panel link (only for admins)
    if st.session_state.user["role"] == "admin":
        st.markdown("### Admin Functions")
        if st.button("Admin Panel", key="admin_panel_button"):
            # Redirect to the Admin Panel page
            st.switch_page("pages/admin_panel.py")
    
    # Logout button
    if st.button("Logout", key="logout_button"):
        logout()
        st.rerun()

# Function to clear session state (excluding some UI control variables)
def clear_cached_data():
    print("====== CLEARING SESSION STATE ======")
    print(f"Before clearing - Session state keys: {list(st.session_state.keys())}")
    
    # Check if data exists in session state
    if 'po_data' in st.session_state and st.session_state.po_data is not None:
        print(f"PO Data exists with {len(st.session_state.po_data)} rows")
        if 'Total_Cost' in st.session_state.po_data.columns:
            total_cost_sum = st.session_state.po_data['Total_Cost'].sum()
            print(f"Total Cost sum before clearing: ${total_cost_sum:,.2f}")
    else:
        print("No PO data found in session state")
    
    # Items to preserve during cache clearing
    keys_to_preserve = ['delete_pressed', 'delete_confirmed', 'po_save_pressed', 'non_po_save_pressed',
                         'po_custom_name', 'non_po_custom_name', 'current_page', 'selected_supplier', 
                         'show_supplier_details']
    
    # Store values we want to keep
    preserved_values = {}
    for key in keys_to_preserve:
        if key in st.session_state:
            preserved_values[key] = st.session_state[key]
    
    # Clear the data-related items
    data_keys = ['data', 'po_data', 'non_po_data', 'blended_data', 'original_data', 
                 'all_datasets', 'selected_report_id', 'report_type', 'chemical_spend_data']
    
    print("Clearing the following session state keys:")
    for key in data_keys:
        if key in st.session_state:
            print(f"- Clearing {key}")
            st.session_state[key] = None
        else:
            print(f"- {key} not in session state")
    
    # Also clear cached file information to force re-processing
    if 'po_filename' in st.session_state:
        print(f"- Clearing po_filename (was: {st.session_state.po_filename})")
        st.session_state.po_filename = None
    
    if 'non_po_filename' in st.session_state:
        print(f"- Clearing non_po_filename (was: {st.session_state.non_po_filename})")
        st.session_state.non_po_filename = None
        
    if 'chemical_spend_filename' in st.session_state:
        print(f"- Clearing chemical_spend_filename (was: {st.session_state.chemical_spend_filename})")
        st.session_state.chemical_spend_filename = None
    
    if 'last_po_uploaded_time' in st.session_state:
        print(f"- Clearing last_po_uploaded_time")
        st.session_state.last_po_uploaded_time = None
    
    if 'last_non_po_uploaded_time' in st.session_state:
        print(f"- Clearing last_non_po_uploaded_time")
        st.session_state.last_non_po_uploaded_time = None
        
    # Clear session manager's report IDs to force data reload on refresh
    if 'loaded_report_ids' in st.session_state:
        print(f"- Clearing loaded_report_ids (was: {st.session_state.loaded_report_ids})")
        st.session_state.loaded_report_ids = {}
    
    # Restore preserved values
    for key, value in preserved_values.items():
        st.session_state[key] = value
    
    print(f"After clearing - Session state keys: {list(st.session_state.keys())}")
    print("====== SESSION STATE CLEARED ======")
    
    st.success("Cached data cleared successfully. The data will be reloaded with the latest calculation method.")

# Set default theme if not already set
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default to dark theme regardless of color theme

# Set default color theme if not already set
if 'color_theme' not in st.session_state:
    st.session_state.color_theme = 'matrix'  # Matrix theme as default

# Apply the appropriate theme CSS and get active theme info
from water_treatment_theme import get_theme_css, get_active_theme
active_theme = get_active_theme()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Add a full override CSS for industrial theme to ensure all text is black
if active_theme == 'industrial':
    st.markdown("""
    <style>
    /* INDUSTRIAL THEME COMPREHENSIVE OVERRIDE */
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
    .main-header {
        background-color: #F5F5F5 !important;
        color: #000000 !important;
    }
    
    /* Make KPI cards have white background in industrial theme */
    div.element-container div.row-widget.stButton, 
    div.element-container div[data-testid="stHorizontalBlock"],
    div.element-container [data-testid="stMetricValue"],
    div.element-container [data-testid="stMetricLabel"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(249, 115, 22, 0.2) !important;
        box-shadow: 0 2px 6px rgba(249, 115, 22, 0.1) !important;
    }

    /* Blanket selector for ALL text elements */
    .stApp *, 
    [data-testid="stSidebar"] *, 
    [data-testid="stHeader"] *, 
    .stTabs *, 
    [data-testid="stExpander"] *, 
    [data-testid="stWidgetLabel"] *,
    .stAlert *, 
    .stInfo *, 
    [data-testid="stMarkdownContainer"] * {
        color: #000000 !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6, 
    div[role="heading"], 
    [data-testid="stHeading"], 
    .stTitle, 
    .stHeader {
        color: #000000 !important;
        font-family: 'Inter', 'Arial', sans-serif !important;
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
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Chart backgrounds */
    .js-plotly-plot, 
    .plotly, 
    .plot-container {
        background-color: #FFFFFF !important;
    }
    
    /* Card buttons in industrial theme */
    div[data-testid="stButton"] button {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(249, 115, 22, 0.3) !important;
        color: #000000 !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
    }
    
    div[data-testid="stButton"] button:hover {
        border: 1px solid #F97316 !important;
        box-shadow: 0 4px 8px rgba(249, 115, 22, 0.2) !important;
        transform: translateY(-2px);
    }

    /* Links - orange in the industrial theme */
    a, a:link, a:visited {
        color: #F97316 !important;
    }
    
    /* Primary buttons should remain orange with WHITE text */
    [data-testid="baseButton-primary"] {
        color: #FFFFFF !important;
        background-color: #F97316 !important;
    }
    
    /* Override any element with text color */
    span, p, div, label, li, ul, ol {
        color: #000000 !important;
    }
    
    /* Target elements with inline styles */
    *[style*="color:"] {
        color: #000000 !important;
    }
    
    /* Special case - override all RGB color values */
    [style*="color: rgb(49, 51, 63)"], 
    [style*="color: rgb(0, 104, 201)"],
    [style*="color: rgb(14, 16, 26)"], 
    [style*="color: rgb(49, 51, 63)"],
    [style*="color: rgb(70, 103, 167)"], 
    [style*="color: rgb(38, 39, 48)"],
    [style*="color: rgb(22, 23, 24)"], 
    [style*="color: rgb(26, 26, 27)"],
    [style*="color: rgb(88, 88, 89)"], 
    [style*="color: rgb(59, 65, 68)"],
    [style*="color: rgb(107, 119, 140)"], 
    [style*="color: rgb(135, 135, 135)"],
    [style*="color: rgb(113, 116, 123)"], 
    [style*="color: rgb(151, 155, 157)"] {
        color: #000000 !important;
    }
    
    /* Force chart text to be black */
    .js-plotly-plot .plotly .main-svg text {
        fill: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Add custom CSS for header based on theme
if active_theme == 'industrial':
    # Industrial theme additional header CSS
    st.markdown("""
    <style>
        /* Industrial Theme header styles */
        .main-header {
            background-color: #FFFFFF !important;
            padding: 1.5rem !important;
            border-radius: 8px !important;
            color: #000000 !important; /* BLACK text */
            text-align: center !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 4px 6px rgba(15, 23, 42, 0.1) !important;
            font-family: 'Inter', 'Arial', sans-serif !important;
            border-left: 4px solid #F97316 !important;
        }
        
        /* Force ALL text elements in the industrial theme to be black */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp p, .stApp span, .stApp div, .stApp label, .stApp a,
        .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stWidgetLabel"] {
            color: #000000 !important; /* BLACK text */
        }
        
        /* Override table text color */
        .stApp table, .stApp th, .stApp td, .stApp tr {
            color: #000000 !important; /* BLACK text */
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Matrix theme additional header CSS
    st.markdown("""
    <style>
        /* Matrix Theme header styles */
        .main-header {
            background-color: #000000 !important;
            padding: 1rem !important;
            border-radius: 0.5rem !important;
            color: #00FF00 !important;
            text-align: center !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.7) !important;
            font-family: 'Courier New', monospace !important;
            border: 1px solid #00FF00 !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            text-shadow: 0 0 10px #00FF00 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Update config.toml file based on the active theme
try:
    config_path = ".streamlit/config.toml"
    if os.path.exists(config_path):
        config = toml.load(config_path)
        if 'theme' not in config:
            config['theme'] = {}
        
        active_theme = get_active_theme()
        
        if active_theme == 'industrial':
            # Industrial theme settings
            config['theme']['primaryColor'] = "#F97316"  # Orange accent
            config['theme']['backgroundColor'] = "#F5F5F5"  # Light gray background 
            config['theme']['secondaryBackgroundColor'] = "#E5E5E5"  # Slightly darker gray for contrast
            config['theme']['textColor'] = "#000000"  # BLACK text for better readability
        else:
            # Default to Matrix theme settings
            config['theme']['primaryColor'] = "#00FF00"  # Matrix green
            config['theme']['backgroundColor'] = "#000000"  # Pure black background
            config['theme']['secondaryBackgroundColor'] = "#001100"  # Very dark green
            config['theme']['textColor'] = "#00FF00"  # Matrix green text
        
        # Save config
        with open(config_path, 'w') as f:
            toml.dump(config, f)
except Exception as e:
    print(f"Error updating config file: {e}")

# Sidebar for data management with streamlined interface
with st.sidebar:
    st.header("Report Management")
    
    # Create tabs for Upload and Manage
    tabs = st.tabs(["Upload Files", "Manage Reports"])
    
    # Tab 1: Upload Files
    with tabs[0]:
        st.subheader("Upload Reports")
        st.info("Upload PO and Non-PO reports for analysis")
        
        # Map the user-friendly names to the internal report type identifiers
        report_type_map = {
            "PO Line Detail": "po_line_detail",
            "Non-PO Invoice Chemical GL": "non_po_invoice",
            "Chemical Spend by Supplier": "chemical_spend_by_supplier"
        }
        
        # File Upload Section - with dropdown for report type
        report_type_selection = st.selectbox(
            "Select Report Type:",
            options=["PO Line Detail", "Non-PO Invoice Chemical GL", "Chemical Spend by Supplier"],
            key="report_type_selection"
        )
        
        # File uploader that changes based on selected type
        if report_type_selection == "PO Line Detail":
            uploaded_file = st.file_uploader(
                "Upload PO Line Detail file", 
                type=['csv', 'xlsx', 'xls'], 
                key="po_upload"
            )
            internal_type = "po_line_detail"
        elif report_type_selection == "Chemical Spend by Supplier":
            uploaded_file = st.file_uploader(
                "Upload Chemical Spend by Supplier file (NetSuite)", 
                type=['xls', 'xlsx', 'csv'], 
                key="chemical_spend_upload"
            )
            internal_type = "chemical_spend_by_supplier"
        else:  # Non-PO Invoice
            uploaded_file = st.file_uploader(
                "Upload Non-PO Invoice Chemical GL file", 
                type=['csv', 'xlsx', 'xls'], 
                key="non_po_upload"
            )
            internal_type = "non_po_invoice"
        
        # Custom name input field directly in upload section
        custom_name = st.text_input(
            "Report Display Name:",
            value=f"{report_type_selection} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
            key=f"{internal_type}_name_input",
            help="Enter a descriptive name for this report"
        )
        
        # Only show the process button if a file is uploaded
        if uploaded_file is not None:
            # Streamlined processing - no separate button for name entry
            if st.button("Process and Save Report", key=f"save_{internal_type}_btn"):
                try:
                    # Check if this is a new file upload by checking filename and content
                    session_filename_key = f"{internal_type}_filename"
                    session_content_key = f"last_{internal_type}_uploaded_time"
                    
                    is_new_upload = (
                        session_filename_key not in st.session_state or 
                        st.session_state.get(session_filename_key) != uploaded_file.name or
                        session_content_key not in st.session_state or 
                        st.session_state.get(session_content_key) != uploaded_file.getvalue()
                    )
                    
                    if is_new_upload:
                        # Process the uploaded file
                        st.info(f"Processing {uploaded_file.name}...")
                        
                        # Extract and standardize data
                        df, detected_type = extract_standard_data(uploaded_file, report_type=internal_type)
                        
                        # Validate the data
                        is_valid, message = validate_data(df)
                        
                        if is_valid:
                            # Update session state with processed data
                            if internal_type == "po_line_detail":
                                data_key = "po_data"
                            elif internal_type == "chemical_spend_by_supplier":
                                # For Chemical Spend by Supplier, use its own dedicated key
                                data_key = "chemical_spend_data"
                                
                                # For Chemical Spend by Supplier, delete all previous chemical spend reports first
                                reports = list_saved_datasets()
                                deleted_count = 0
                                chemical_spend_reports = []
                                
                                # Find reports of the relevant type
                                for report in reports:
                                    if 'report_type' in report and ('Chemical Spend by Supplier' in report['report_type']):
                                        chemical_spend_reports.append(report)
                                
                                # Delete each report
                                for report in chemical_spend_reports:
                                    if 'id' in report:
                                        success = delete_dataset(report['id'])
                                        if success:
                                            deleted_count += 1
                                
                                if deleted_count > 0:
                                    st.info(f"Removed {deleted_count} previous Chemical Spend by Supplier reports")
                            else:
                                data_key = "non_po_data"
                                
                            st.session_state[data_key] = df
                            st.session_state[session_filename_key] = uploaded_file.name
                            st.session_state[session_content_key] = uploaded_file.getvalue()
                            st.session_state.report_type = internal_type
                            
                            # Save directly without popup form
                            save_metadata = save_uploaded_data(
                                df=df,
                                filename=uploaded_file.name,
                                report_type=report_type_selection,
                                description=custom_name,  # Use the custom name from text input
                                custom_name=custom_name   # Also pass as custom_name parameter
                            )
                            
                            # Store report ID and update any references
                            if 'id' in save_metadata:
                                report_id = save_metadata['id']
                                st.session_state.selected_report_id = report_id
                                
                                # Use session manager to store report ID for persistence
                                update_loaded_report_id(internal_type, report_id)
                                
                                # Update datasets for unified dashboard
                                # Always initialize all_datasets if it doesn't exist
                                if 'all_datasets' not in st.session_state or st.session_state.all_datasets is None:
                                    st.session_state.all_datasets = []
                                
                                # Update or add to existing datasets
                                new_dataset = {
                                    'data': df,
                                    'report_type': internal_type,
                                    'filename': uploaded_file.name
                                }
                                
                                # Replace existing dataset or add new one
                                found = False
                                
                                if st.session_state.all_datasets:
                                    for i, dataset in enumerate(st.session_state.all_datasets):
                                        if dataset.get('report_type') == internal_type:
                                            st.session_state.all_datasets[i] = new_dataset
                                            found = True
                                            break
                                
                                if not found:
                                    st.session_state.all_datasets.append(new_dataset)
                                
                                # Success message without record count for Chemical Spend by Supplier
                                if internal_type == "chemical_spend_by_supplier":
                                    st.success(f"✅ Successfully processed and saved '{custom_name}'")
                                    
                                    # Show a small preview of the data
                                    st.subheader("Data Preview")
                                    preview_cols = st.columns([3, 1])
                                    with preview_cols[0]:
                                        st.dataframe(df.head(3), use_container_width=True)
                                    
                                    # Add a direct link to Chemical Spend Dashboard
                                    # and set a flag to redirect on rerun
                                    st.session_state.redirect_to_chemical_dashboard = True
                                    st.session_state.chemical_spend_data = df  # Ensure data is stored in session
                                    st.session_state.chemical_spend_filename = uploaded_file.name  # Store filename
                                    
                                    # Set the new report flag to ensure proper date filtering
                                    st.session_state.newly_uploaded_report = True
                                    
                                    with preview_cols[1]:
                                        # Only show spend metric for Chemical Spend by Supplier
                                        if 'Total_Cost' in df.columns:
                                            total_spend = df['Total_Cost'].sum()
                                            st.metric("Total Spend", f"${total_spend:,.2f}")
                                else:
                                    # Success message with more details for other report types
                                    st.success(f"✅ Successfully processed and saved '{custom_name}'")
                                    st.success(f"Loaded {len(df)} records")
                                    
                                    # Show a small preview of the data
                                    st.subheader("Data Preview")
                                    preview_cols = st.columns([3, 1])
                                    with preview_cols[0]:
                                        st.dataframe(df.head(3), use_container_width=True)
                                    with preview_cols[1]:
                                        st.metric("Records", f"{len(df):,}")
                                        
                                        # Show a basic statistic if Total_Cost is available
                                        if 'Total_Cost' in df.columns:
                                            total_spend = df['Total_Cost'].sum()
                                            st.metric("Total Spend", f"${total_spend:,.2f}")
                            else:
                                st.error("Failed to save report. No ID was returned from database.")
                        else:
                            st.error(f"Invalid data: {message}")
                    else:
                        st.warning("This file has already been processed. Please upload a different file.")
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
    
    # Tab 2: Manage Reports
    with tabs[1]:
        st.subheader("Manage Reports")
        
        # Refresh and Delete All - layout with columns
        refresh_col, clear_col = st.columns(2)
        
        # Refresh/Reset button
        with refresh_col:
            if st.button("🔄 Refresh List", key="refresh_reports_btn"):
                # Clear relevant session state to force reload
                for key in ['data', 'selected_report_id', 'all_datasets']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("Report list refreshed")
        
        # Clear all reports button
        with clear_col:
            if st.button("🗑️ Clear All Reports", key="clear_all_reports_btn"):
                # Track delete all state
                if 'delete_all_pressed' not in st.session_state:
                    st.session_state.delete_all_pressed = True
                    st.rerun()
        
        # Delete all confirmation dialog
        if 'delete_all_pressed' in st.session_state and st.session_state.delete_all_pressed:
            st.warning("⚠️ Are you sure you want to delete ALL saved reports? This action cannot be undone.")
            confirm_cols = st.columns(2)
            
            with confirm_cols[0]:
                if st.button("Yes, Delete All Reports", key="confirm_delete_all"):
                    # Get all reports
                    reports = list_saved_datasets()
                    success_count = 0
                    
                    for report in reports:
                        report_id = report.get('id')
                        if report_id:
                            success = delete_dataset(report_id)
                            if success:
                                success_count += 1
                    
                    # Reset session state
                    st.session_state.delete_all_pressed = False
                    
                    # Clear all report-related session state variables
                    for key in list(st.session_state.keys()):
                        if key.startswith('saved_report') or key in ['selected_report_id', 'data', 'saved_reports', 'saved_reports_dict', 'all_datasets']:
                            if key in st.session_state:
                                del st.session_state[key]
                    
                    # Clear all report type-specific data
                    report_type_keys = [
                        'po_data', 'po_filename',
                        'non_po_data', 'non_po_filename',
                        'chemical_spend_data', 'chemical_spend_filename'
                    ]
                    
                    for key in report_type_keys:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    # Show success and rerun
                    if success_count > 0:
                        st.success(f"Successfully deleted {success_count} reports")
                    else:
                        st.info("No reports were deleted")
                    
                    # Rerun to refresh UI
                    st.rerun()
            
            with confirm_cols[1]:
                if st.button("Cancel", key="cancel_delete_all"):
                    st.session_state.delete_all_pressed = False
                    st.rerun()
            
        # Get reports from database - always refresh from database after deletion
        reports = list_saved_datasets()
        # Store the current list of reports for comparison
        st.session_state.current_saved_reports = reports
        
        if reports:
            # Create a dictionary of report options for the dropdown
            report_options = {}
            for report in reports:
                # Prioritize the custom name from description field
                custom_name = report.get('description', '')
                
                # If no description is available, generate a fallback name
                if not custom_name:
                    report_type = report.get('report_type', 'Unknown Report')
                    # Format date for display in fallback name
                    try:
                        uploaded_at = report.get('uploaded_at', '')
                        if 'T' in uploaded_at:
                            date_obj = datetime.datetime.fromisoformat(uploaded_at)
                            date_str = date_obj.strftime("%Y-%m-%d")
                        else:
                            date_str = uploaded_at[:10]
                        custom_name = f"{report_type} - {date_str}"
                    except:
                        custom_name = report.get('name', 'Unnamed Report')
                
                # Use the custom name for the dropdown display
                report_options[custom_name] = report['id']
            
            # Create the dropdown
            selected_report_name = None
            if report_options:
                # Create a unique key for the dropdown to force refresh after deletion
                dropdown_key = f"saved_report_dropdown_{len(reports)}"
                selected_report_name = st.selectbox(
                    "Select a saved report:", 
                    options=list(report_options.keys()),
                    key=dropdown_key
                )
                
                # Create a card-like display for the selected report
                if selected_report_name:
                    report_id = report_options[selected_report_name]
                    
                    # Get report info
                    _, report_info = load_saved_dataset(report_id)
                    
                    if report_info:
                        # Format information
                        report_type = report_info.get('report_type', 'Unknown')
                        original_filename = report_info.get('original_filename', 'Unknown')
                        record_count = report_info.get('record_count', 0)
                        uploaded_at = report_info.get('uploaded_at', '')
                        
                        # Format date for display
                        try:
                            if 'T' in uploaded_at:
                                date_obj = datetime.datetime.fromisoformat(uploaded_at)
                                uploaded_at = date_obj.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                        
                        # Display report details - don't show record count for Chemical Spend by Supplier
                        if 'Chemical Spend by Supplier' in report_type:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>{selected_report_name}</h4>
                                <p><strong>Type:</strong> {report_type}</p>
                                <p><strong>Uploaded:</strong> {uploaded_at}</p>
                                <p><strong>Original file:</strong> {original_filename}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>{selected_report_name}</h4>
                                <p><strong>Type:</strong> {report_type}</p>
                                <p><strong>Records:</strong> {record_count:,}</p>
                                <p><strong>Uploaded:</strong> {uploaded_at}</p>
                                <p><strong>Original file:</strong> {original_filename}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Action buttons
                    action_cols = st.columns(2)
                    
                    with action_cols[0]:
                        if st.button("📊 Load Report", key="load_report_btn"):
                            # Load report data
                            df, report_info = load_saved_dataset(report_id)
                            
                            if df is not None:
                                # Determine report type
                                loaded_report_type = report_info.get('report_type', 'Unknown')
                                
                                # Convert to internal type
                                internal_report_type = None
                                if 'PO Line Detail' in loaded_report_type:
                                    internal_report_type = 'po_line_detail'
                                    st.session_state.po_data = df
                                    st.session_state.po_filename = report_info.get('original_filename', '')
                                    # Store report ID for persistence
                                    update_loaded_report_id('po_line_detail', report_id)
                                elif 'Non-PO Invoice' in loaded_report_type:
                                    internal_report_type = 'non_po_invoice'
                                    st.session_state.non_po_data = df
                                    st.session_state.non_po_filename = report_info.get('original_filename', '')
                                    # Store report ID for persistence
                                    update_loaded_report_id('non_po_invoice', report_id)
                                elif 'Chemical Spend by Supplier' in loaded_report_type:
                                    internal_report_type = 'chemical_spend_by_supplier'
                                    # Store in session state with its own key
                                    st.session_state.chemical_spend_data = df
                                    st.session_state.chemical_spend_filename = report_info.get('original_filename', '')
                                    # Store report ID for persistence
                                    update_loaded_report_id('chemical_spend_by_supplier', report_id)
                                    # Set flag to redirect to chemical spend dashboard
                                    # Set flag to indicate a new report was uploaded (for date filtering)
                                    st.session_state.newly_uploaded_report = True
                                    
                                    # Show success message and instruction
                                    st.success(f"Loaded report: {selected_report_name}")
                                    st.info("Chemical Spend data is now loaded. Click on the 'Chemical Spend Dashboard' tab at the top to view the analysis.")
                                
                                # Update session state with selected report data
                                # For Chemical Spend by Supplier reports, we already set the specific session state key
                                # and we don't want to set general data key to prevent data mixing
                                if internal_report_type != 'chemical_spend_by_supplier':
                                    st.session_state.data = df
                                
                                st.session_state.report_type = internal_report_type
                                st.session_state.selected_report_id = report_id
                                
                                # Update datasets list
                                # Always initialize all_datasets if it doesn't exist or is None
                                if 'all_datasets' not in st.session_state or st.session_state.all_datasets is None:
                                    st.session_state.all_datasets = []
                                
                                # Add to or update existing datasets
                                new_dataset = {
                                    'data': df,
                                    'report_type': internal_report_type,
                                    'filename': report_info.get('original_filename', '')
                                }
                                
                                found = False
                                
                                if st.session_state.all_datasets:
                                    for i, dataset in enumerate(st.session_state.all_datasets):
                                        if dataset.get('report_type') == internal_report_type:
                                            st.session_state.all_datasets[i] = new_dataset
                                            found = True
                                            break
                                
                                if not found:
                                    st.session_state.all_datasets.append(new_dataset)
                                
                                st.success(f"Loaded report: {selected_report_name}")
                            else:
                                st.error("Could not load the selected report data")
                    
                    with action_cols[1]:
                        # Initialize state variables for deletion
                        if 'delete_confirmed' not in st.session_state:
                            st.session_state.delete_confirmed = False
                        # Initialize delete_pressed if not in session state
                        if 'delete_pressed' not in st.session_state:
                            st.session_state.delete_pressed = False
                        
                        # Convert to boolean to ensure proper type
                        delete_disabled = bool(st.session_state.get('delete_pressed', False))
                        
                        # Delete button
                        if st.button("🗑️ Delete", key="delete_report_btn", disabled=delete_disabled):
                            st.session_state.delete_pressed = True
                            st.rerun()
                    
                    # Delete confirmation dialog
                    if st.session_state.delete_pressed and not st.session_state.delete_confirmed:
                        st.warning(f"Are you sure you want to delete '{selected_report_name}'?")
                        confirm_cols = st.columns(2)
                        
                        with confirm_cols[0]:
                            if st.button("Yes, Delete", key="confirm_delete"):
                                success = delete_dataset(report_id)
                                
                                if success:
                                    # Reset session state
                                    st.session_state.delete_confirmed = True
                                    st.session_state.delete_pressed = False
                                    
                                    # Clear associated data
                                    for key in ['data', 'selected_report_id', 'saved_report_dropdown', 'saved_reports', 'saved_reports_dict']:
                                        if key in st.session_state:
                                            del st.session_state[key]
                                    
                                    # Clear specific report type data
                                    # Get the report information from the database
                                    _, report_info = load_saved_dataset(report_id)
                                    report_type = report_info.get('report_type', '') if report_info else ''
                                    
                                    # Debug the report type information
                                    print(f"DEBUG - Report deletion: Report ID {report_id}, Type: {report_type}")
                                    print(f"DEBUG - Report info: {report_info}")
                                    
                                    # Make report_type lowercase for case-insensitive comparison
                                    report_type = report_type.lower() if report_type else ''
                                    
                                    # Check for the different report types with case-insensitive comparison
                                    if 'chemical_spend_by_supplier' in report_type or 'chemical spend by supplier' in report_type:
                                        print(f"DEBUG - Clearing Chemical Spend data from session state")
                                        if 'chemical_spend_data' in st.session_state:
                                            del st.session_state.chemical_spend_data
                                        if 'chemical_spend_filename' in st.session_state:
                                            del st.session_state.chemical_spend_filename
                                        # Remove from session manager
                                        remove_loaded_report_id('chemical_spend_by_supplier')
                                    elif 'po_line_detail' in report_type or 'po line detail' in report_type:
                                        print(f"DEBUG - Clearing PO Line Detail data from session state")
                                        if 'po_data' in st.session_state:
                                            del st.session_state.po_data
                                        if 'po_filename' in st.session_state:
                                            del st.session_state.po_filename
                                        # Remove from session manager
                                        remove_loaded_report_id('po_line_detail')
                                    elif 'non_po_invoice' in report_type or 'non-po invoice' in report_type:
                                        print(f"DEBUG - Clearing Non-PO Invoice data from session state")
                                        if 'non_po_data' in st.session_state:
                                            del st.session_state.non_po_data
                                        if 'non_po_filename' in st.session_state:
                                            del st.session_state.non_po_filename
                                        # Remove from session manager
                                        remove_loaded_report_id('non_po_invoice')
                                    
                                    # Clear all_datasets to force reload
                                    if 'all_datasets' in st.session_state:
                                        st.session_state.all_datasets = []
                                    
                                    # Show success and rerun
                                    st.success(f"Report '{selected_report_name}' deleted successfully")
                                    
                                    # Force reload reports list from database
                                    saved_datasets = list_saved_datasets()
                                    
                                    # Rerun the app to refresh UI
                                    st.rerun()
                                else:
                                    st.error("Failed to delete report. Please try again.")
                        
                        with confirm_cols[1]:
                            if st.button("Cancel", key="cancel_delete"):
                                st.session_state.delete_pressed = False
                                st.rerun()
            else:
                st.warning("No saved reports found in database.")
        else:
            st.info("No saved reports found. Upload a file to analyze.")

    # The section for processing non_po_file has been removed in favor of the new tabbed interface

    # Data Selection Section
    st.subheader("3. Select Data Source")

    # Determine what data is available
    has_po_data = st.session_state.po_data is not None
    has_non_po_data = st.session_state.non_po_data is not None
    has_chemical_spend_data = 'chemical_spend_data' in st.session_state and st.session_state.chemical_spend_data is not None

    if has_po_data or has_non_po_data or has_chemical_spend_data:
        data_options = []
        if has_po_data:
            data_options.append("PO Line Detail")
        if has_non_po_data:
            data_options.append("Non-PO Invoice")
        if has_chemical_spend_data:
            data_options.append("Chemical Spend by Supplier")

        selected_data = st.radio("Select data to analyze:", data_options)

        # Set the data based on selection
        if selected_data == "PO Line Detail":
            st.session_state.data = st.session_state.po_data
            st.session_state.report_type = "po_line_detail"  # Set internal report type identifier
            st.success("Analyzing PO Line Detail data")
        elif selected_data == "Non-PO Invoice":
            st.session_state.data = st.session_state.non_po_data
            st.session_state.report_type = "non_po_invoice"  # Set internal report type identifier
            st.success("Analyzing Non-PO Invoice data")
        elif selected_data == "Chemical Spend by Supplier":
            # Don't set the general data key to chemical_spend_data
            # to prevent data mixing - chemical_spend_dashboard.py will use
            # chemical_spend_data directly 
            st.session_state.report_type = "chemical_spend_by_supplier"  # Set internal report type identifier
            st.success("Analyzing Chemical Spend by Supplier data")
            
            # Add Clear button for Chemical Spend data specifically 
            if st.button("🗑️ Clear Chemical Spend Data", key="clear_chemical_spend_btn"):
                # Find all reports of type 'Chemical Spend by Supplier' from the database
                reports = list_saved_datasets()
                
                # Count deleted datasets
                deleted_count = 0
                chemical_spend_reports = []
                
                # Find reports of the relevant type
                for report in reports:
                    if 'report_type' in report and ('Chemical Spend by Supplier' in report['report_type']):
                        chemical_spend_reports.append(report)
                
                # Delete each report
                for report in chemical_spend_reports:
                    if 'id' in report:
                        success = delete_dataset(report['id'])
                        if success:
                            deleted_count += 1
                
                # Clear session state
                if 'chemical_spend_data' in st.session_state:
                    del st.session_state.chemical_spend_data
                if 'chemical_spend_filename' in st.session_state:
                    del st.session_state.chemical_spend_filename
                
                # Remove from session manager
                remove_loaded_report_id('chemical_spend_by_supplier')
                
                # Show result
                if deleted_count > 0:
                    st.success(f"Successfully deleted {deleted_count} Chemical Spend by Supplier reports")
                    # Rerun to refresh the UI
                    st.rerun()
                else:
                    st.info("No Chemical Spend by Supplier reports found to delete")
            
            st.info("Chemical Spend Dashboard will access data directly from its dedicated store without mixing with other report types")
    else:
        st.info("Please upload at least one file to begin analysis")

    # Show data summary if available
    if 'data' in st.session_state and st.session_state.data is not None:
        st.write("#### Data Summary")
        
        # Don't show record count for Chemical Spend data
        if st.session_state.report_type != "chemical_spend_by_supplier":
            st.write(f"Total Records: {len(st.session_state.data)}")
        
        # Show date range if Date column exists
        if 'Date' in st.session_state.data.columns:
            st.write(f"Date Range: {st.session_state.data['Date'].min().strftime('%Y-%m-%d')} to {st.session_state.data['Date'].max().strftime('%Y-%m-%d')}")
        
        # Check for Facility column or alternatives based on file type
        facility_columns = ['Facility', 'Supplier', '{Vendor}', 'Department', 'Department: Name', 'Purchase Order: Supplier']
        facility_col = next((col for col in facility_columns if col in st.session_state.data.columns), None)
        if facility_col:
            st.write(f"{facility_col.replace('_', ' ').title()}: {len(st.session_state.data[facility_col].unique())}")
        
        # Check for Chemical column or alternatives
        chemical_columns = ['Chemical', 'Description', 'Item Description', 'Dimension3 Description', 'Item: Category']
        chemical_col = next((col for col in chemical_columns if col in st.session_state.data.columns), None)
        if chemical_col:
            st.write(f"{chemical_col.replace('_', ' ').title()}: {len(st.session_state.data[chemical_col].unique())}")

        # Export data option
        st.write("#### Export Processed Data")
        export_format = st.selectbox("Export Format", ["CSV", "Excel"])

        if st.button("Export Data"):
            if export_format == "CSV":
                csv = st.session_state.data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="processed_chemical_spend_data.csv",
                    mime="text/csv",
                )
            else:  # Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    st.session_state.data.to_excel(writer, index=False, sheet_name='Chemical Spend Data')
                st.download_button(
                    label="Download Excel",
                    data=output.getvalue(),
                    file_name="processed_chemical_spend_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

# REMOVED DATA MIXING CODE - No longer combine data from different report types
# Each dashboard should use its specific data source
# Chemical Spend Dashboard uses chemical_spend_data session state only
# Customized Dashboard uses po_data and non_po_data
# This preserves data isolation and prevents metrics from being skewed

# Check if any of them exist (for backward compatibility)
has_po_data = 'po_data' in st.session_state and st.session_state.po_data is not None
has_non_po_data = 'non_po_data' in st.session_state and st.session_state.non_po_data is not None

# Only combine PO and Non-PO data for the unified dashboard
# Chemical Spend data is kept isolated in its own session state key
if has_po_data and has_non_po_data:
    # Only use combined PO and Non-PO data for unified dashboard
    st.session_state.data = pd.concat([st.session_state.po_data, st.session_state.non_po_data])
elif has_po_data:
    # Use only PO data
    st.session_state.data = st.session_state.po_data
elif has_non_po_data:
    # Use only Non-PO data
    st.session_state.data = st.session_state.non_po_data

# Chemical Spend data is now kept completely isolated in its own session state key (chemical_spend_data)
# Do not add chemical_spend_data to the general data key

# Main content area
if 'data' not in st.session_state or st.session_state.data is None:
    st.info("👈 Please upload a chemical spend data file from the sidebar to get started.")
    
    # Add an app description with key metrics and functionality
    st.markdown("""
    ## How This App Works
    
    The CST - Inframark app helps you track and monitor chemical procurement across facilities.
    
    ### Key Features:
    * Upload and analyze PO Detail or Non-PO Invoice reports followed by Chemical Spend by Supplier reports
    * View interactive dashboards with detailed metrics
    * Analyze chemical usage by region and supplier
    * Track chemical order distribution with automatic data visualization
    * Save and manage multiple report uploads for historical comparison
    
    ### Getting Started:
    1. **Upload order in the correct sequence:**
       * **First:** Upload a PO Line Detail report OR Non-PO Invoice Chemical GL report
       * **Then:** Upload a Chemical Spend by Supplier report
    2. The Chemical Spend by Supplier report should have these columns:
       * Vendor/Supplier
       * Line of Service Name
       * Project Region
       * Department Name
       * Bill # (Supplier Invoice #)
       * Date Due
       * Date Created
       * Description
       * QTY (Quantity)
       * Units
       * Total
    3. Give your report a name (or use the default name)
    4. Navigate to the dashboard to view your interactive analytics
    """)
    
    # Create tabs for the different report formats
    format_tabs = st.tabs(["PO Line Detail Report", "Non-PO Invoice Chemical GL Report", "Chemical Spend by Supplier Report"])

    with format_tabs[0]:
        st.write("### PO Line Detail Report Format")

        st.write("""
        The PO Line Detail report format includes these columns:

        - Purchase Order: Confirmation Date: The confirmation date of the order
        - Line Number: The line number in the purchase order
        - Purchase Requisition: Number: The requisition number (REQ-xxxxx)
        - Order Identifier: The order identification number (MF-xxxxx)
        - Purchase Order: Supplier: The supplier name
        - Item Description: Description of the chemical or item
        - Category: The chemical category (often in format 'Chemical - Name - Concentration')
        - Confirmed Unit Price: Price per unit of the chemical
        - Connected Quantity: The planned quantity
        - Confirmed Quantity: The actual quantity that was ordered
        - Purchase Requisition: Buyer: The buyer name and email
        - Purchase Requisition: Our Reference: The reference person name and email
        - Purchase Order: Processing Status: Current status (e.g., "Open")
        - Purchase Order: Received By: The receiver's information
        - Type: The type of order ("Catalog", "Free text", or "Punch out")
        """)

        # Example of company data format matching exact PO Line Detail report structure
        company_data = {
            'Purchase Order: Confirmation Date': ['2025-03-18', '2025-03-18', '2025-03-18'],
            'Line Number': [1, 1, 1],
            'Purchase Requisition: Number': ['REQ-73284', 'REQ-73375', 'REQ-73201'],
            'Order Identifier': ['MF-73428', 'MF-73376', 'MF-73290'],
            'Purchase Order: Supplier': ['Hawkins Inc', 'Univar USA Inc', 'Olin Corporation'],
            'Item Description': ['Bleach', 'NEWBURG Chemical - Sodium Hypochlorite - 10-12.5%', 'CAUSTIC'],
            'Category': ['Chemical - Sodium Hypochlorite - 10-12.5%', 'Chemical - Sodium Hypochlorite - 10-12.5%', 'Chemical - Sodium Hydroxide / Caustic Soda'],
            'Confirmed Unit Price': [2.75, 2.05, 1.32],
            'Connected Quantity': [0.0, 0.0, 0.0],
            'Confirmed Quantity': [550.0, 3000.0, 37000.0],
            'Purchase Requisition: Buyer': [None, None, 'Robert Whitney (rwhitney@inframark.com)'],
            'Purchase Requisition: Our Reference': ['Amber Webb (awebb@inframark.com)', 'Richard Bolde (rbolde@inframark.com)', 'Jenny St Jean (jstjean@inframark.com)'],
            'Purchase Order: Processing Status': ['Open', 'Open', 'Open'],
            'Purchase Order: Received By': [None, None, None],
            'Type': ['Free text', 'Catalog', 'Free text']
        }
        st.write("#### Sample PO Line Detail Format:")
        st.dataframe(pd.DataFrame(company_data))

    with format_tabs[1]:
        st.write("### Non-PO Invoice Chemical GL Report Format")

        st.write("""
        The Non-PO Invoice Chemical GL report format includes these columns:

        - Invoice: Type: The type of invoice
        - Invoice: Created Date: The creation date of the invoice
        - Supplier: Name: The supplier name
        - Invoice: Number: The invoice identification number
        - Coding Line Number: Line number in the invoice
        - Dimension1 Value: Cost code value
        - Dimension1 Description: Description of the cost code
        - Dimension2 Value: Facility information (usually contains facility name and codes)
        - Net Amount: The invoice amount
        - Dimension3 Description: Additional classification information
        - Dimension4 Description: Region and location information (e.g., "South : Georgia : Sinclair")
        - Dimension5 Description: Additional descriptive information
        - Dimension5 Value: Additional code value
        """)

        # Example of Non-PO Invoice Chemical GL format
        invoice_data = {
            'Invoice: Type': ['External', 'External', 'External'],
            'Invoice: Created Date': ['2025-03-19', '2025-03-19', '2025-03-18'],
            'Supplier: Name': ['Hawkins Inc', 'Brenntag Mid-South, Inc', 'Univar Solutions LLC'],
            'Invoice: Number': ['6036402', '3521098', '4910067'],
            'Coding Line Number': [1, 1, 1],
            'Dimension1 Value': ['6110-000-00', '6110-000-00', '6110-000-00'],
            'Dimension1 Description': ['Chemical', 'Chemical', 'Chemical'],
            'Dimension2 Value': ['Sinclair Water Authority - WTP 3861 (1076)', 'Tupelo - WWTP 4074 (1100)', 'Commerce - WTP 3727 (990)'],
            'Net Amount': [1892.50, 3625.00, 1275.60],
            'Dimension3 Description': ['Operations', 'Operations', 'Operations'],
            'Dimension4 Description': ['South : Georgia : Sinclair', 'South : Mississippi : Tupelo', 'South : Georgia : Commerce'],
            'Dimension5 Description': ['Water', 'Wastewater', 'Water'],
            'Dimension5 Value': ['WATER', 'WASTEWAT', 'WATER']
        }
        st.write("#### Sample Non-PO Invoice Chemical GL Format:")
        st.dataframe(pd.DataFrame(invoice_data))
        
    with format_tabs[2]:
        st.write("### Chemical Spend by Supplier Report Format")
        
        st.write("""
        The Chemical Spend by Supplier report format includes these columns:
        
        - {Vendor}: The vendor/supplier name
        - Line of Service: Name: The service line classification
        - Project Region: Regional classification of the project
        - Department: Name: Department using the chemical
        - Bill # (Supplier Invoice #): Invoice or bill identifier
        - Date Due: Due date for the invoice
        - Date Created: The date the invoice was created
        - Description: Description of the chemical or service
        - QTY: Quantity of chemical ordered
        - Units: Unit of measurement (gallons, pounds, etc.)
        - Total: Total cost amount for the line item
        """)
        
        # Example of Chemical Spend by Supplier format based on actual columns
        chemical_spend_data = {
            '{Vendor}': ['Hawkins Inc', 'Carus Corporation', 'Univar Solutions LLC'],
            'Line of Service: Name': ['O&M Water', 'O&M Water', 'O&M Water'],
            'Project Region': ['Southeast', 'Midwest', 'Southwest'],
            'Department: Name': ['Municipal Water', 'Water Treatment', 'Municipal Water'],
            'Bill # (Supplier Invoice #)': ['INV-98765', 'INV-87654', 'INV-76543'],
            'Date Due': ['2025-03-25', '2025-03-24', '2025-03-23'],
            'Date Created': ['2025-03-15', '2025-03-14', '2025-03-13'],
            'Description': ['Sodium Hypochlorite 12.5%', 'KMnO4 (Potassium Permanganate)', 'Chlorine - 1 ton container'],
            'QTY': [550, 60, 1],
            'Units': ['Gallons', 'Pounds', 'Each'],
            'Total': [1512.50, 555.00, 875.00]
        }
        st.write("#### Sample Chemical Spend by Supplier Format:")
        st.dataframe(pd.DataFrame(chemical_spend_data))
else:
    # Create tabs for the different dashboards - simplified navigation with essential tabs
    dashboard_tabs = st.tabs(["Customized Dashboard", "Chemical Spend Analysis"])
    
    with dashboard_tabs[0]:
        # Display the customized dashboard with enhanced supplier analysis
        from hidden_pages import customized_dashboard
        customized_dashboard.app()

    with dashboard_tabs[1]:
        # Chemical Spend by Supplier Analysis Tab - Using the dedicated module
        from hidden_pages import chemical_spend_dashboard
        # Get the data from either chemical_spend_data or data session state
        if 'chemical_spend_data' in st.session_state and st.session_state.chemical_spend_data is not None:
            st.session_state.data = st.session_state.chemical_spend_data
            st.session_state.report_type = "chemical_spend_by_supplier"
        
        # Use the specialized dashboard module which accesses st.session_state.data directly
        chemical_spend_dashboard.app()
        
    # PO Trend Analysis has been moved to a sub-tab under PO Analysis in Customized Dashboard
    # Supplier Comparison Tab has been completely removed

# Main entry point
if __name__ == "__main__":
    pass
