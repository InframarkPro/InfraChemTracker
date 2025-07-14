"""
Industrial Authentication Theme Style

This module provides specific styling for the authentication pages (login and register)
in the Industrial theme.
"""

def get_industrial_auth_css():
    """
    Get the CSS for the industrial authentication pages
    
    Returns:
        str: CSS for the industrial authentication pages
    """
    return """
    <style>
    /* Hide Streamlit elements */
    header {display: none !important;}
    footer {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* Make the background light gray */
    body {
        background-color: #F5F5F5 !important;
        color: #333333 !important;
        font-family: 'Arial', sans-serif !important;
    }
    
    .stApp {
        background-color: transparent !important;
    }
    
    /* Global Form Styling */
    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 5px !important;
        padding: 20px !important;
        width: 100% !important;
        max-width: 650px !important;
        margin: 0 auto !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Input field styling */
    [data-baseweb="input"] {
        border: 1px solid #D1D5DB !important;
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
        background-color: #F97316 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        padding: 10px 20px !important;
        margin-top: 10px !important;
        width: 100% !important;
        font-family: 'Arial', sans-serif !important;
    }
    
    .stButton button:hover {
        background-color: #EA580C !important;
        box-shadow: 0 2px 5px rgba(249, 115, 22, 0.4) !important;
    }
    
    /* Secondary button */
    .stButton button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #F97316 !important;
        border: 1px solid #F97316 !important;
    }
    
    .stButton button[kind="secondary"]:hover {
        background-color: #FEF3C7 !important;
    }
    
    /* Form Title */
    h1, h2, h3 {
        color: #333333 !important;
        font-family: 'Arial', sans-serif !important;
        text-align: center !important;
        margin-bottom: 20px !important;
        font-weight: 600 !important;
    }
    
    /* Links */
    a {
        color: #F97316 !important;
        text-decoration: none !important;
    }
    
    a:hover {
        text-decoration: underline !important;
    }
    
    /* Alerts and error messages */
    .stAlert {
        background-color: #FFFFFF !important;
        border-radius: 5px !important;
    }
    
    /* Error alert */
    .stAlert[kind="error"] {
        background-color: #FEF2F2 !important;
        border-left: 4px solid #EF4444 !important;
    }
    
    /* Success alert */
    .stAlert[kind="success"] {
        background-color: #F0FDF4 !important;
        border-left: 4px solid #10B981 !important;
    }
    
    /* Info box */
    [data-testid="stExpander"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 5px !important;
    }
    
    [data-testid="stExpander"] > details > summary {
        background-color: #F5F5F5 !important;
        color: #333333 !important;
        font-weight: 600 !important;
        padding: 10px 15px !important;
        border-bottom: 1px solid #E5E7EB !important;
    }
    
    /* Logo styling */
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .auth-logo {
        max-width: 150px;
        height: auto;
    }
    
    /* Form layout */
    .auth-form-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    
    /* Checkbox styling */
    [data-testid="stCheckbox"] {
        color: #333333 !important;
    }
    
    [data-testid="stCheckbox"] label p {
        color: #333333 !important;
    }
    
    /* Form divider */
    .form-divider {
        display: flex;
        align-items: center;
        text-align: center;
        color: #9CA3AF;
        margin: 20px 0;
    }
    
    .form-divider::before,
    .form-divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #E5E7EB;
    }
    
    .form-divider::before {
        margin-right: 10px;
    }
    
    .form-divider::after {
        margin-left: 10px;
    }
    
    /* Add industrial accents */
    .industrial-accent {
        border-left: 4px solid #F97316;
        padding-left: 10px;
    }
    
    /* Login form specifics */
    .login-form {
        border-top: 4px solid #F97316 !important;
    }
    
    /* Registration form specifics */
    .registration-form {
        border-top: 4px solid #3B82F6 !important;
    }
    </style>
    """

def get_industrial_preview():
    """
    Get the HTML for the industrial theme preview
    
    Returns:
        str: HTML for the industrial theme preview
    """
    return """
    <div style="background-color: #F5F5F5; border: 1px solid #E5E7EB; padding: 10px; border-radius: 5px; text-align: center; height: 120px;">
        <h5 style="color: #333333; font-family: Arial, sans-serif; border-left: 3px solid #F97316; padding-left: 8px; display: inline-block;">Industrial Theme</h5>
        <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; margin: 5px; padding: 8px; border-radius: 3px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);">
            <span style="color: #333333; font-family: Arial, sans-serif;">Light Gray with Orange Accents</span>
        </div>
    </div>
    """

def get_industrial_description():
    """
    Get the HTML for the industrial theme description
    
    Returns:
        str: HTML for the industrial theme description
    """
    return """
    <div style="margin-top: 10px; padding: 10px; background-color: #FFFFFF; border-radius: 5px; border: 1px solid #E5E7EB;">
        <p style="color: #4B5563; font-family: Arial, sans-serif; margin: 0;">
        The Industrial theme features a clean, bright interface with orange accents and a utility-focused design.
        Perfect for daily use in technical and engineering environments.
        </p>
    </div>
    """