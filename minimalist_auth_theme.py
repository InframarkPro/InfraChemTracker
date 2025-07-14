"""
Minimalist Authentication Theme Style

This module provides specific styling for the authentication pages (login and register)
in the Minimalist theme.
"""

def get_minimalist_auth_css():
    """
    Get the CSS for the minimalist authentication pages
    
    Returns:
        str: CSS for the minimalist authentication pages
    """
    return """
    <style>
    /* Hide Streamlit elements */
    header {display: none !important;}
    footer {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* Make the background white */
    body {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        font-family: 'Arial', sans-serif !important;
    }
    
    .stApp {
        background-color: transparent !important;
    }
    
    /* Global Form Styling */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 5px;
        padding: 20px;
        width: 100% !important;
        max-width: 650px !important;
        margin: 0 auto !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Input field styling */
    [data-baseweb="input"] {
        border: 1px solid #DDDDDD !important;
        background-color: #F5F5F5 !important;
        margin-bottom: 15px !important;
    }
    
    [data-baseweb="input"] input {
        color: #333333 !important;
        font-family: 'Arial', sans-serif !important;
        font-size: 16px !important;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #0066CC !important;
        color: #FFFFFF !important;
        border: none !important;
        font-family: 'Arial', sans-serif !important;
        font-size: 16px !important;
        padding: 8px 16px !important;
        border-radius: 4px !important;
    }
    
    .stButton button:hover {
        background-color: #0055AA !important;
    }
    
    /* Radio button styling for theme selection */
    .stRadio > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 30px !important;
    }
    
    .stRadio > div > div {
        flex: 0 0 auto !important;
    }
    
    /* Theme preview containers */
    div[data-testid="column"] > div {
        height: auto !important;
    }
    
    /* Make labels more visible */
    .stTextInput label, .stRadio label {
        color: #333333 !important;
        font-weight: 500 !important;
        font-family: 'Arial', sans-serif !important;
        font-size: 16px !important;
        margin-bottom: 5px !important;
    }
    
    /* Custom heading styles */
    h1, h2, h3, h4, h5 {
        color: #222222 !important;
        font-family: 'Arial', sans-serif !important;
    }
    
    /* Fix theme column height */
    div[data-testid="column"] [data-testid="stVerticalBlock"] {
        height: auto !important;
    }
    </style>
    """

def get_login_header():
    """
    Get the header HTML for the login page
    
    Returns:
        str: HTML for the login header
    """
    return """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-family: 'Arial', sans-serif; color: #333333; font-size: 36px;">Chemical Dashboard</h1>
        <h3 style="font-family: 'Arial', sans-serif; color: #333333; font-size: 20px;">LOGIN</h3>
    </div>
    """

def get_register_header():
    """
    Get the header HTML for the register page
    
    Returns:
        str: HTML for the register header
    """
    return """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-family: 'Arial', sans-serif; color: #333333; font-size: 36px;">Chemical Dashboard</h1>
        <h3 style="font-family: 'Arial', sans-serif; color: #333333; font-size: 20px;">REGISTER NEW USER</h3>
    </div>
    """

def get_theme_heading():
    """
    Get the theme selection heading
    
    Returns:
        str: HTML for the theme selection heading
    """
    return """
    <div style="margin-top: 20px; margin-bottom: 10px; font-family: 'Arial', sans-serif; color: #333333;">
        <h4>Choose Your Dashboard Theme</h4>
    </div>
    """

def get_minimalist_preview():
    """
    Get the HTML for the minimalist theme preview
    
    Returns:
        str: HTML for the minimalist theme preview
    """
    return """
    <div style="background-color: #FFFFFF; border: 1px solid #DDDDDD; padding: 10px; border-radius: 5px; text-align: center; height: 120px;">
        <h5 style="color: #333333; font-family: 'Arial', sans-serif;">Minimalist Theme</h5>
        <div style="background-color: #F8F9FA; border: 1px solid #E0E0E0; margin: 5px; padding: 8px; border-radius: 3px;">
            <span style="color: #333333; font-family: 'Arial', sans-serif;">Black Text with Blue Accents</span>
        </div>
    </div>
    """

def get_minimalist_description():
    """
    Get the HTML for the minimalist theme description
    
    Returns:
        str: HTML for the minimalist theme description
    """
    return """
    <div style="margin-top: 10px; padding: 10px; background-color: rgba(248, 249, 250, 0.7); border-radius: 5px; border: 1px solid #E0E0E0;">
        <p style="color: #333333; font-family: 'Arial', sans-serif; margin: 0; background-color: #F8F9FA; border-radius: 3px; padding: 5px;">
        The Minimalist theme offers a sleek, modern design with blue accents on a white background.
        Provides excellent contrast and a professional aesthetic with blue-shaded KPIs and metrics.
        </p>
    </div>
    """