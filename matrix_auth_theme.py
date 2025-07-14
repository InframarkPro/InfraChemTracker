"""
Matrix Authentication Theme Style

This module provides specific styling for the authentication pages (login and register)
in the Matrix theme.
"""

def get_matrix_auth_css():
    """
    Get the CSS for the matrix authentication pages
    
    Returns:
        str: CSS for the matrix authentication pages
    """
    return """
    <style>
    /* Hide Streamlit elements */
    header {display: none !important;}
    footer {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* Make the background black */
    body {
        background-color: #000000 !important;
        color: #00FF00 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .stApp {
        background-color: transparent !important;
    }
    
    /* Global Form Styling */
    [data-testid="stForm"] {
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid #00FF00 !important;
        border-radius: 5px !important;
        padding: 20px !important;
        width: 100% !important;
        max-width: 650px !important;
        margin: 0 auto !important;
    }
    
    /* Input field styling */
    [data-baseweb="input"] {
        border: 1px solid #00AA00 !important;
        background-color: rgba(0, 0, 0, 0.8) !important;
        margin-bottom: 15px !important;
    }
    
    [data-baseweb="input"] input {
        color: #00FF00 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
    }
    
    /* Button styling - more aggressive targeting for login and register buttons */
    .stButton button,
    button[kind="primary"], button[kind="secondary"],
    button[data-testid="baseButton-primary"], button[data-testid="baseButton-secondary"],
    div[data-testid="baseButton-primary"] button, div[data-testid="baseButton-secondary"] button,
    input[type="submit"], button[type="submit"],
    form button, form .stButton button,
    button[data-baseweb="button"], .stButton > button {
        background-color: #000000 !important;
        color: #00FF00 !important;
        border: 1px solid #00AA00 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        padding: 8px 16px !important;
    }
    
    .stButton button:hover,
    button[kind="primary"]:hover, button[kind="secondary"]:hover,
    button[data-testid="baseButton-primary"]:hover, button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="baseButton-primary"] button:hover, div[data-testid="baseButton-secondary"] button:hover,
    input[type="submit"]:hover, button[type="submit"]:hover,
    form button:hover, form .stButton button:hover,
    button[data-baseweb="button"]:hover, .stButton > button:hover {
        background-color: #001100 !important;
        border: 1px solid #00FF00 !important;
        box-shadow: 0 0 5px #00FF00 !important;
        cursor: pointer !important;
        color: #00FF00 !important;
        text-shadow: 0 0 5px #00FF00 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Dropdown option hover styling */
    [data-baseweb="select"] ul li:hover,
    [data-baseweb="menu"] ul li:hover,
    [role="listbox"] [role="option"]:hover,
    [data-testid="stSelectbox"] option:hover,
    select option:hover {
        background-color: #001100 !important;
        color: #00FF00 !important;
        cursor: pointer !important;
    }
    
    /* Form submit buttons */
    div[data-testid="stForm"] button {
        background-color: #000000 !important;
        color: #00FF00 !important;
        border: 1px solid #00AA00 !important;
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
        color: #00FF00 !important;
        font-weight: bold !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        margin-bottom: 5px !important;
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
        <h1 style="font-family: 'Courier New', monospace; color: #00FF00; font-size: 36px;">Chemical Dashboard</h1>
        <h3 style="font-family: 'Courier New', monospace; color: #00FF00; font-size: 20px;">LOGIN</h3>
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
        <h1 style="font-family: 'Courier New', monospace; color: #00FF00; font-size: 36px;">Chemical Dashboard</h1>
        <h3 style="font-family: 'Courier New', monospace; color: #00FF00; font-size: 20px;">REGISTER NEW USER</h3>
    </div>
    """

def get_theme_heading():
    """
    Get the theme selection heading
    
    Returns:
        str: HTML for the theme selection heading
    """
    return """
    <div style="margin-top: 20px; margin-bottom: 10px; font-family: 'Courier New', monospace; color: #00FF00;">
        <h4>Choose Your Dashboard Theme</h4>
    </div>
    """

def get_matrix_preview():
    """
    Get the HTML for the matrix theme preview
    
    Returns:
        str: HTML for the matrix theme preview
    """
    return """
    <div style="background-color: #000000; border: 1px solid #00FF00; padding: 10px; border-radius: 5px; text-align: center; height: 120px;">
        <h5 style="color: #00FF00; font-family: 'Courier New', monospace;">Matrix Theme</h5>
        <div style="background-color: #001100; border: 1px solid #00AA00; margin: 5px; padding: 8px; border-radius: 3px;">
            <span style="color: #00FF00; font-family: 'Courier New', monospace;">Neon Green on Black</span>
        </div>
    </div>
    """

def get_matrix_description():
    """
    Get the HTML for the matrix theme description
    
    Returns:
        str: HTML for the matrix theme description
    """
    return """
    <div style="margin-top: 10px; padding: 10px; background-color: rgba(0, 17, 0, 0.5); border-radius: 5px;">
        <p style="color: #00FF00; font-family: 'Courier New', monospace; margin: 0;">
        The Matrix theme uses a striking neon green on black design reminiscent of classic terminal displays.
        Ideal for low-light environments and dramatic data presentation.
        </p>
    </div>
    """

def get_matrix_rain_effect():
    """
    Get the HTML and JavaScript for the Matrix rain effect
    
    Returns:
        str: HTML and JavaScript for the Matrix rain effect
    """
    return """
    <div class="matrix-rain" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: -1; opacity: 0.3; 
                 pointer-events: none; overflow: hidden;"></div>
    
    <script>
    // Matrix code rain effect
    const canvas = document.createElement('canvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.zIndex = '-1';
    canvas.style.pointerEvents = 'none';
    document.querySelector('.matrix-rain').appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    
    // Characters for the Matrix rain
    const chars = '01アイウエオカキクケコサシスセソタチツテト';
    
    const columns = Math.floor(canvas.width / 20);
    const drops = [];
    
    for (let i = 0; i < columns; i++) {
        drops[i] = Math.floor(Math.random() * -20);
    }
    
    function drawMatrixRain() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#0F0';
        ctx.font = '15px monospace';
        
        for (let i = 0; i < drops.length; i++) {
            const text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(text, i * 20, drops[i] * 20);
            
            if (drops[i] * 20 > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            
            drops[i]++;
        }
    }
    
    const matrixInterval = setInterval(drawMatrixRain, 55);
    </script>
    """