"""
Minimalist Login Theme Module

This module provides a clean black and white theme for the login page.
"""

def get_minimalist_login_css():
    """Return CSS for minimalist black and white login theme"""
    try:
        return """
    <style>
    /* Critical styles for login page - ensuring consistent appearance */
    /* RESET - Ensure we have a clean slate */
    html, body {
        background-color: #000000 !important;
        margin: 0 !important;
        padding: 0 !important;
        font-family: sans-serif !important;
    }
    
    /* Hide all Streamlit UI elements */
    header {display: none !important;}
    footer {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* ===== CRITICAL: Force ALL possible container elements to BLACK ===== */
    html, body, .stApp, 
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stToolbar"], 
    [data-testid="stSidebar"], 
    [data-testid="stSidebarUserContent"],
    .block-container,
    div[data-layout="wide"],
    section[data-testid="stSidebar"],
    div[data-testid="stVerticalBlock"],
    div.element-container,
    div.row-widget.stApp,
    div[role="main"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    
    /* Override Streamlit main container width */
    .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Override column sizing to prevent stretching */
    div.stColumn {
        width: auto !important;
        flex: none !important;
        min-width: auto !important;
    }
    
    /* Center main content */
    div[data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }
    
    /* LOGIN FORM CONTAINER STYLING - GUARANTEED BOX */
    .login-container, .register-container {
        width: 200px !important;
        max-width: 200px !important;
        margin: 0 auto !important;
        padding: 10px !important;
        border: 1px solid #FFFFFF !important;
        background-color: #000000 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1) !important;
        box-sizing: border-box !important;
    }
    
    /* Tighter control over Streamlit form */
    section.main > div:first-child {
        display: flex !important;
        justify-content: center !important;
    }

    section.main div[data-testid="stForm"] {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }

    form {
        width: 400px !important;
        max-width: 400px !important;
        padding: 20px !important;
        background-color: #000 !important;
        border: 1px solid #fff !important;
        border-radius: 8px !important;
    }
    
    /* Styled inputs */
    .stTextInput > div > div > input,
    .css-1k17nkz.e1q9ylmb2,
    div[data-baseweb="input"] > div:first-child {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        padding: 0.3rem !important;
        height: 32px !important;
        font-size: 13px !important;
        box-sizing: border-box !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* ALL text elements to white */
    h1, h2, h3, h4, h5, h6, p, 
    span:not(.st-emotion-cache-gu4ico), 
    div:not(.stAlert *),
    label, 
    a, 
    input,
    .stMarkdown, 
    .stMarkdown * {
        color: #FFFFFF !important;
        font-family: sans-serif !important;
    }
    
    /* Button styling */
    form button, 
    div.stButton button, 
    button[type="submit"], 
    button[data-testid="baseButton-primary"], 
    button[data-testid="baseButton-secondary"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        border-radius: 0 !important;
        font-family: sans-serif !important;
        height: 32px !important;
        min-height: 32px !important;
        font-size: 13px !important;
        padding: 0 10px !important;
        cursor: pointer !important;
    }
    
    /* Button hover effect */
    form button:hover, div.stButton button:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        transition: all 0.3s ease !important;
    }
    
    /* Remove ANY matrix theme effects */
    canvas {
        display: none !important;
    }
    
    /* Alert text should remain readable */
    .stAlert, .stAlert p {
        color: #000000 !important; 
    }
    
    /* Style field labels above inputs */
    .field-label {
        margin-bottom: 5px !important;
        font-size: 14px !important;
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    
    /* Style the password visibility toggle */
    button[aria-label="Hide password"] svg, 
    button[aria-label="Show password"] svg {
        fill: #FFFFFF !important;
    }
    </style>
    """
    except Exception as e:
        print(f"Error in get_minimalist_login_css: {str(e)}")
        return """
    <style>
    /* Fallback styling */
    body, html, .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    </style>
    """

def get_login_header():
    """Return HTML for the login header in minimalist black and white theme"""
    try:
        return """
    <div style="text-align: center; padding: 15px 0; border-bottom: 1px solid #FFFFFF; max-width: 400px; margin: 0 auto;">
        <h1 style="color: #FFFFFF; font-family: sans-serif; font-size: 20px; margin-bottom: 5px;">Procurement Chemical Dashboard</h1>
        <p style="color: #FFFFFF; font-family: sans-serif; font-size: 14px; margin: 0;">Please log in to access the dashboard</p>
    </div>
    """
    except Exception as e:
        print(f"Error in get_login_header: {str(e)}")
        return """
    <div style="text-align: center; padding: 15px 0;">
        <h1 style="color: #FFFFFF; font-size: 22px; margin-bottom: 5px;">Procurement Chemical Dashboard</h1>
        <p style="color: #FFFFFF; font-size: 14px; margin: 0;">Please log in to access the dashboard</p>
    </div>
    """

def get_register_header():
    """Return HTML for the registration header in minimalist black and white theme"""
    try:
        return """
    <div style="text-align: center; padding: 15px 0; border-bottom: 1px solid #FFFFFF; max-width: 400px; margin: 0 auto;">
        <h1 style="color: #FFFFFF; font-family: sans-serif; font-size: 20px; margin-bottom: 5px;">Procurement Chemical Dashboard</h1>
        <p style="color: #FFFFFF; font-family: sans-serif; font-size: 14px; margin: 0;">Register for an account</p>
    </div>
    """
    except Exception as e:
        print(f"Error in get_register_header: {str(e)}")
        return """
    <div style="text-align: center; padding: 15px 0;">
        <h1 style="color: #FFFFFF; font-size: 22px; margin-bottom: 5px;">Procurement Chemical Dashboard</h1>
        <p style="color: #FFFFFF; font-size: 14px; margin: 0;">Register for an account</p>
    </div>
    """

def get_theme_heading():
    """Return HTML for the theme selection heading in minimalist black and white theme"""
    try:
        return """
    <div style="text-align: center; padding: 10px 0; border-bottom: 1px solid #FFFFFF;">
        <h2 style="color: #FFFFFF; font-family: sans-serif; font-size: 24px;">Select Your Theme</h2>
        <p style="color: #FFFFFF; font-family: sans-serif; font-size: 14px;">Choose a visual style for the dashboard</p>
    </div>
    """
    except Exception as e:
        print(f"Error in get_theme_heading: {str(e)}")
        return """
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #FFFFFF; font-size: 24px;">Select Your Theme</h2>
        <p style="color: #FFFFFF; font-size: 14px;">Choose a visual style for the dashboard</p>
    </div>
    """

def get_register_note():
    """Return HTML for the registration note in minimalist black and white theme"""
    try:
        return """
    <div style="margin-top: 15px; padding: 8px; border: 1px solid #FFFFFF; border-radius: 0;">
        <p style="color: #FFFFFF; margin: 0; font-size: 12px;">Admin approval required for registration.</p>
    </div>
    """
    except Exception as e:
        print(f"Error in get_register_note: {str(e)}")
        return """
    <div style="margin-top: 15px; padding: 8px;">
        <p style="color: #FFFFFF; margin: 0; font-size: 12px;">Admin approval required for registration.</p>
    </div>
    """

def get_industrial_preview():
    """Return HTML for the industrial theme preview in minimalist black and white style"""
    try:
        return """
    <div style="
        border: 1px solid #FFFFFF; 
        border-radius: 0; 
        padding: 6px; 
        margin-bottom: 10px;
        background-color: #000000;
        text-align: center;
    ">
        <h4 style="color: #FFFFFF; font-family: sans-serif; margin-bottom: 3px; font-size: 12px;">Industrial Theme</h4>
        <div style="
            background-color: #333333;
            height: 60px;
            border-radius: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
            font-size: 11px;
            color: #FFFFFF;
            margin-bottom: 3px;
            border: 1px solid #FFFFFF;
        ">Standard Users</div>
    </div>
    """
    except Exception as e:
        print(f"Error in get_industrial_preview: {str(e)}")
        return """
    <div style="border: 1px solid #FFFFFF; padding: 6px; margin-bottom: 10px; text-align: center;">
        <h4 style="color: #FFFFFF; margin-bottom: 3px; font-size: 12px;">Industrial Theme</h4>
        <div style="background-color: #333333; height: 60px; border: 1px solid #FFFFFF; display: flex; align-items: center; justify-content: center; color: #FFFFFF; font-size: 11px;">Standard Users</div>
    </div>
    """

def get_matrix_preview():
    """Return HTML for the matrix theme preview in minimalist black and white style"""
    try:
        return """
    <div style="
        border: 1px solid #FFFFFF; 
        border-radius: 0; 
        padding: 6px; 
        margin-bottom: 10px;
        background-color: #000000;
        text-align: center;
    ">
        <h4 style="color: #FFFFFF; font-family: 'Courier New', monospace; margin-bottom: 3px; font-size: 12px;">Matrix Theme</h4>
        <div style="
            background-color: #000000;
            height: 60px;
            border-radius: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: #FFFFFF;
            margin-bottom: 3px;
            border: 1px solid #FFFFFF;
        ">Admin Users</div>
    </div>
    """
    except Exception as e:
        print(f"Error in get_matrix_preview: {str(e)}")
        return """
    <div style="border: 1px solid #FFFFFF; padding: 6px; margin-bottom: 10px; text-align: center;">
        <h4 style="color: #FFFFFF; margin-bottom: 3px; font-size: 12px;">Matrix Theme</h4>
        <div style="background-color: #000000; height: 60px; border: 1px solid #FFFFFF; display: flex; align-items: center; justify-content: center; color: #FFFFFF; font-size: 11px;">Admin Users</div>
    </div>
    """