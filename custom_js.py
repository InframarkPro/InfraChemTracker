"""
Custom JavaScript injector for fixing styling issues in Streamlit.
"""
import streamlit as st

def inject_tab_fix_script():
    """
    Inject custom JavaScript to ensure tab containers maintain black background
    even after dynamic reloading.
    """
    js_code = """
    <script>
    // Function to force black background on tab elements
    function fixTabBackgrounds() {
        // Find all tab lists
        const tabLists = document.querySelectorAll('[role="tablist"]');
        tabLists.forEach(tabList => {
            tabList.style.backgroundColor = "#000000";
            // Also set inline style with !important
            tabList.setAttribute('style', 'background-color: #000000 !important');
            
            // Get all direct children
            Array.from(tabList.children).forEach(child => {
                child.style.backgroundColor = "#000000";
                child.setAttribute('style', 'background-color: #000000 !important');
            });
        });
        
        // Find all tab panels
        const tabPanels = document.querySelectorAll('[data-baseweb="tab-panel"]');
        tabPanels.forEach(panel => {
            panel.style.backgroundColor = "#000000";
            panel.setAttribute('style', 'background-color: #000000 !important');
        });
        
        // Find all tab containers 
        const tabContainers = document.querySelectorAll('[data-baseweb="tab-list"]');
        tabContainers.forEach(container => {
            container.style.backgroundColor = "#000000";
            container.setAttribute('style', 'background-color: #000000 !important');
            
            // Get all direct children
            Array.from(container.children).forEach(child => {
                child.style.backgroundColor = "#000000";
                child.setAttribute('style', 'background-color: #000000 !important');
            });
        });
    }
    
    // Run immediately
    fixTabBackgrounds();
    
    // Set interval to keep running - handles dynamic page updates
    setInterval(fixTabBackgrounds, 500);
    </script>
    """
    
    # Inject the JavaScript
    st.markdown(js_code, unsafe_allow_html=True)