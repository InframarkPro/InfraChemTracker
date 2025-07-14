"""
Direct Tab Fix Component

This component injects CSS and JavaScript directly into the page to maintain the Matrix theme styling
on tab bars even after report uploads or other dynamic page changes.
"""
import streamlit as st

def direct_fix_component():
    """Inject a direct CSS and JavaScript fix that targets the specific elements
    that are turning white after report uploads.
    """
    # Inline CSS with !important rules targeting the most specific selectors possible
    css = """
    <style>
    /* Direct targeting of tab container parent elements */
    [data-testid="stHorizontalBlock"], 
    div[data-testid="stHorizontalBlock"] > div, 
    div[data-testid="stHorizontalBlock"] > div > div {
        background-color: #000000 !important;
    }
    
    /* Direct targeting of tabs elements themselves with important flag */
    [data-baseweb="tab-list"],
    [data-baseweb="tab-list"] > *,
    [data-baseweb="tab-panel"],
    [data-baseweb="tab"] {
        background-color: #000000 !important;
    }
    
    /* Specific targeting for the tab bar containers */
    div[role="tablist"],
    div[role="tablist"] > *,
    div[role="tablist"] > div,
    div[role="tab"],
    div[role="tab"] > * {
        background-color: #000000 !important;
    }
    
    /* Extra specificity for hover states */
    div[role="tab"]:hover {
        background-color: #002200 !important;
    }
    
    /* Active tab styling */
    div[role="tab"][aria-selected="true"] {
        background-color: #003300 !important;
        color: #00FF00 !important;
        box-shadow: 0 0 5px rgba(0, 255, 0, 0.5) !important;
    }
    </style>
    """
    
    # JavaScript that looks for specific elements and forces them to remain black
    # Runs every 500ms and after key user events like clicking
    js = """
    <script>
    function forceTabStyling() {
        // Find all elements that could be tab containers
        document.querySelectorAll('[data-testid="stHorizontalBlock"]').forEach(el => {
            el.style.setProperty('background-color', '#000000', 'important');
            
            // Apply to all children
            Array.from(el.querySelectorAll('*')).forEach(child => {
                if (child.tagName !== 'BUTTON' || child.getAttribute('role') === 'tab') {
                    child.style.setProperty('background-color', '#000000', 'important');
                }
            });
        });
        
        // Find all tab lists
        document.querySelectorAll('[data-baseweb="tab-list"]').forEach(el => {
            el.style.setProperty('background-color', '#000000', 'important');
            
            // Apply to all children
            Array.from(el.querySelectorAll('*')).forEach(child => {
                child.style.setProperty('background-color', '#000000', 'important');
            });
        });
        
        // Find all role="tablist" elements
        document.querySelectorAll('[role="tablist"]').forEach(el => {
            el.style.setProperty('background-color', '#000000', 'important');
            
            // Apply to direct children
            Array.from(el.children).forEach(child => {
                child.style.setProperty('background-color', '#000000', 'important');
            });
        });
        
        // Style active tabs specifically
        document.querySelectorAll('[role="tab"][aria-selected="true"]').forEach(el => {
            el.style.setProperty('background-color', '#003300', 'important');
            el.style.setProperty('color', '#00FF00', 'important');
            el.style.setProperty('box-shadow', '0 0 5px rgba(0, 255, 0, 0.5)', 'important');
        });
    }
    
    // Run immediately
    forceTabStyling();
    
    // Run after any click event on the page
    document.addEventListener('click', function() {
        setTimeout(forceTabStyling, 100);
        setTimeout(forceTabStyling, 500);
    });
    
    // Run after an element is observed changing
    const observer = new MutationObserver(mutations => {
        forceTabStyling();
    });
    
    // Observe the entire body for changes
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
    });
    
    // Also run periodically in case the above methods miss something
    setInterval(forceTabStyling, 1000);
    </script>
    """
    
    # Inject both the CSS and JS
    st.markdown(css + js, unsafe_allow_html=True)