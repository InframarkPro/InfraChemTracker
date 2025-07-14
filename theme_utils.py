"""
Theme Utilities

Functions for managing theme settings across the application.
"""

import streamlit as st
import os
import json

# Directory for saved data
SAVED_DATA_DIR = "saved_data"
USERS_FILE = os.path.join(SAVED_DATA_DIR, "users.json")

def get_active_theme():
    """Get the active theme based on session state"""
    if 'color_theme' not in st.session_state:
        # Default to industrial theme if not set
        return 'industrial'
    
    return st.session_state.color_theme

def is_dark_theme():
    """Return whether the active theme is dark"""
    # Both themes are set to use dark mode, but this function could be used to distinguish
    # between light and dark themes if needed in the future
    return get_active_theme() == 'matrix'

def get_user_theme(user_id):
    """Get the theme preference for a specific user"""
    # Create the saved_data directory if it doesn't exist
    os.makedirs(SAVED_DATA_DIR, exist_ok=True)
    
    # If the users file doesn't exist, create it with default settings
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({"users": []}, f)
        return 'industrial'  # Default theme
    
    # Load existing users data
    with open(USERS_FILE, 'r') as f:
        users_data = json.load(f)
    
    # Find the user and return their theme
    for user in users_data.get('users', []):
        if user.get('id') == user_id:
            return user.get('theme', 'industrial')
    
    # Default to industrial theme if user not found
    return 'industrial'

def get_palette(n):
    """Return n colors from the active theme's color palette
    
    Args:
        n: Number of colors to return
    """
    if is_dark_theme():
        # Matrix theme
        return get_matrix_palette(n)
    else:
        # Industrial theme
        return get_industrial_palette(n)

def get_matrix_palette(n):
    """Return n colors from the Matrix theme palette"""
    matrix_colors = [
        '#00FF00',  # Primary green
        '#00DD00',
        '#00BB00',
        '#009900',
        '#007700',
        '#005500',
        '#003300',
        '#00FF77',
        '#00FFAA',
        '#00FFDD',
        '#77FF00',
        '#AAFF00',
        '#DDFF00'
    ]
    
    # If we need more colors than available, cycle through them
    result = []
    for i in range(n):
        result.append(matrix_colors[i % len(matrix_colors)])
    
    return result

def get_industrial_palette(n):
    """Return n colors from the Industrial theme palette"""
    industrial_colors = [
        '#F97316',  # Primary orange
        '#FB923C',
        '#FDBA74',
        '#EA580C',
        '#C2410C',
        '#9A3412',
        '#7C2D12',
        '#0EA5E9',  # Blue accent
        '#0284C7',
        '#0369A1',
        '#14B8A6',  # Teal accent
        '#0D9488',
        '#0F766E'
    ]
    
    # If we need more colors than available, cycle through them
    result = []
    for i in range(n):
        result.append(industrial_colors[i % len(industrial_colors)])
    
    return result
    
def update_chart_theme(fig):
    """Apply the appropriate theme to a plotly figure based on active theme
    
    Args:
        fig: Plotly figure to apply theme to
    """
    theme = get_active_theme()
    
    # Base plot settings for all themes
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)',
        font_family="Arial, sans-serif",
    )
    
    if theme == 'matrix':
        # Matrix theme (dark with green accents)
        fig.update_layout(
            font_color='#00FF00',
            title_font_color='#00FF00',
        )
        fig.update_xaxes(
            gridcolor='#003300',
            linecolor='#005500',
            title_font=dict(color='#00DD00'),
            tickfont=dict(color='#00DD00')
        )
        fig.update_yaxes(
            gridcolor='#003300',
            linecolor='#005500',
            title_font=dict(color='#00DD00'),
            tickfont=dict(color='#00DD00')
        )
    else:
        # Industrial theme (dark with orange accents)
        fig.update_layout(
            font_color='#E0E0E0',
            title_font_color='#F97316',
        )
        fig.update_xaxes(
            gridcolor='#2A2A2A',
            linecolor='#3A3A3A',
            title_font=dict(color='#FB923C'),
            tickfont=dict(color='#D1D1D1')
        )
        fig.update_yaxes(
            gridcolor='#2A2A2A',
            linecolor='#3A3A3A',
            title_font=dict(color='#FB923C'),
            tickfont=dict(color='#D1D1D1')
        )
    
    return fig