"""
White Authentication Theme Module

This module provides a clean white theme for the authentication pages.
"""

def get_white_auth_css():
    """Return CSS for white authentication theme"""
    return """
    <style>
    /* Hide Streamlit elements */
    header {display: none !important;}
    footer {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* Force override ALL theme elements with white background */
    body, .stApp, [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], [data-testid="stToolbar"], 
    [data-testid="stSidebar"], [data-testid="stSidebarUserContent"],
    .block-container, div[data-layout="wide"], 
    div[role="main"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: sans-serif !important;
    }
    
    .stTextInput > div > div > input {
        background-color: #F5F5F5 !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
    }
    
    .stTextInput label, .stSelectbox label, h1, h2, h3, h4, h5, h6, p, span, div {
        color: #000000 !important;
        font-family: sans-serif !important;
    }
    
    .stMarkdown, .stMarkdown * {
        color: #000000 !important;
        font-family: sans-serif !important;
    }
    
    /* Button styling */
    form button, div.stButton button, button[type="submit"], 
    button[data-testid="baseButton-primary"], button[data-testid="baseButton-secondary"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
        font-family: sans-serif !important;
    }
    
    form button:hover, div.stButton button:hover {
        background-color: #F0F0F0 !important;
    }
    
    /* Container styling for the login form */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    /* Fix any dark mode elements */
    .reportview-container, .main, .reportview-container .main {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Remove ANY matrix theme effects */
    canvas {
        display: none !important;
    }
    
    /* Force all form elements to white theme */
    .stForm {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 8px !important;
    }
    
    .stForm label {
        color: #000000 !important;
    }
    
    </style>
    """

def get_login_header():
    """Return HTML for the login header in white theme"""
    return """
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #000000; font-family: sans-serif; font-size: 28px;">Water Treatment Dashboard</h1>
        <p style="color: #555555; font-family: sans-serif; font-size: 16px;">Please log in to access the dashboard</p>
    </div>
    """

def get_register_header():
    """Return HTML for the registration header in white theme"""
    return """
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #000000; font-family: sans-serif; font-size: 28px;">Water Treatment Dashboard</h1>
        <p style="color: #555555; font-family: sans-serif; font-size: 16px;">Register for an account</p>
    </div>
    """

def get_theme_heading():
    """Return HTML for the theme selection heading in white theme"""
    return """
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #000000; font-family: sans-serif; font-size: 24px;">Select Your Theme</h2>
        <p style="color: #555555; font-family: sans-serif; font-size: 14px;">Choose a visual style for the dashboard</p>
    </div>
    """

def get_white_preview():
    """Return HTML for the white theme preview"""
    return """
    <div style="
        border: 1px solid #CCCCCC; 
        border-radius: 8px; 
        padding: 10px; 
        margin-bottom: 15px;
        background-color: #FFFFFF;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <h3 style="color: #000000; font-family: sans-serif; margin-bottom: 10px;">Standard Theme</h3>
        <div style="
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        ">
            <div style="
                background-color: #F8F8F8;
                width: 30%;
                height: 40px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: sans-serif;
                color: #000000;
                font-size: 12px;
            ">KPI Card</div>
            <div style="
                background-color: #F8F8F8;
                width: 30%;
                height: 40px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: sans-serif;
                color: #000000;
                font-size: 12px;
            ">KPI Card</div>
            <div style="
                background-color: #F8F8F8;
                width: 30%;
                height: 40px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: sans-serif;
                color: #000000;
                font-size: 12px;
            ">KPI Card</div>
        </div>
        <div style="
            background-color: #F8F8F8;
            height: 60px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
            color: #000000;
            margin-bottom: 5px;
        ">Chart Area</div>
    </div>
    """

def get_white_description():
    """Return HTML for the white theme description"""
    return """
    <div style="font-family: sans-serif; color: #555555; font-size: 14px; text-align: center; margin-bottom: 15px;">
        <p>Clean, professional design with standard colors. <br>Best for everyday use and readability.</p>
    </div>
    """