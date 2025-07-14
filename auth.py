"""
Authentication Utilities

Functions for managing user authentication and authorization.
"""

import streamlit as st
import json
import os
import uuid
import time
import logging
import pandas as pd
from hashlib import sha256
from datetime import datetime, timedelta

# Directory for saved data
SAVED_DATA_DIR = "saved_data"
USERS_FILE = os.path.join(SAVED_DATA_DIR, "users.json")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Default admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "matrix2025"

# Import these here to avoid circular imports
try:
    from utils.unified_database import load_saved_dataset, list_saved_datasets
    from utils.session_manager import update_loaded_report_id, update_combined_data
    DATABASE_IMPORTS_AVAILABLE = True
except ImportError:
    logging.warning("Database utilities could not be imported in auth module")
    DATABASE_IMPORTS_AVAILABLE = False
    
def load_latest_reports():
    """
    Load the latest reports of each type into session state.
    This function will automatically load the most recent report of each type
    (PO Line Detail, Non-PO Invoice, Chemical Spend by Supplier).
    
    Returns:
        bool: True if any reports were loaded, False otherwise
    """
    if not DATABASE_IMPORTS_AVAILABLE:
        logging.warning("Cannot load latest reports: database utilities not available")
        return False
        
    # Get all saved reports
    try:
        all_reports = list_saved_datasets()
        if not all_reports:
            logging.info("No reports found in database")
            return False
            
        # Track if we loaded anything
        reports_loaded = False
        
        # Get the latest PO Line Detail report
        po_reports = [r for r in all_reports if r.get('report_type') == 'PO Line Detail']
        if po_reports:
            # Sort by upload date (descending)
            po_reports.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
            latest_po_report = po_reports[0]
            
            # Load the report
            logging.info(f"Loading latest PO Line Detail report: {latest_po_report.get('name')} (ID: {latest_po_report.get('id')})")
            df, report_info = load_saved_dataset(latest_po_report.get('id'))
            
            if df is not None:
                st.session_state['po_data'] = df
                st.session_state['po_filename'] = report_info.get('original_filename', '')
                update_loaded_report_id('po_line_detail', latest_po_report.get('id'))
                reports_loaded = True
                logging.info(f"Successfully loaded PO Line Detail report with {len(df)} rows")
            
        # Get the latest Non-PO Invoice report
        non_po_reports = [r for r in all_reports if r.get('report_type') == 'Non-PO Invoice Chemical GL']
        if non_po_reports:
            # Sort by upload date (descending)
            non_po_reports.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
            latest_non_po_report = non_po_reports[0]
            
            # Load the report
            logging.info(f"Loading latest Non-PO Invoice report: {latest_non_po_report.get('name')} (ID: {latest_non_po_report.get('id')})")
            df, report_info = load_saved_dataset(latest_non_po_report.get('id'))
            
            if df is not None:
                st.session_state['non_po_data'] = df
                st.session_state['non_po_filename'] = report_info.get('original_filename', '')
                update_loaded_report_id('non_po_invoice', latest_non_po_report.get('id'))
                reports_loaded = True
                logging.info(f"Successfully loaded Non-PO Invoice report with {len(df)} rows")
                
        # Get the latest Chemical Spend by Supplier report
        chemical_reports = [r for r in all_reports if r.get('report_type') == 'Chemical Spend by Supplier']
        if chemical_reports:
            # Sort by upload date (descending)
            chemical_reports.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
            latest_chemical_report = chemical_reports[0]
            
            # Load the report
            logging.info(f"Loading latest Chemical Spend report: {latest_chemical_report.get('name')} (ID: {latest_chemical_report.get('id')})")
            df, report_info = load_saved_dataset(latest_chemical_report.get('id'))
            
            if df is not None:
                st.session_state['chemical_spend_data'] = df
                st.session_state['chemical_spend_filename'] = report_info.get('original_filename', '')
                update_loaded_report_id('chemical_spend_by_supplier', latest_chemical_report.get('id'))
                reports_loaded = True
                logging.info(f"Successfully loaded Chemical Spend report with {len(df)} rows")
        
        # Update combined data if any reports were loaded
        if reports_loaded:
            logging.info("Updating combined data")
            update_combined_data()
            
        return reports_loaded
            
    except Exception as e:
        logging.error(f"Error loading latest reports: {str(e)}")
        return False

def hash_password(password):
    """Hash a password using SHA-256"""
    return sha256(password.encode()).hexdigest()

def initialize_admin():
    """Initialize admin user if not already exists"""
    # Create the saved_data directory if it doesn't exist
    os.makedirs(SAVED_DATA_DIR, exist_ok=True)
    
    # Check if users file exists, create it if not
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({"users": []}, f)
    
    # Load existing users data
    with open(USERS_FILE, 'r') as f:
        users_data = json.load(f)
    
    # Check if admin user exists
    admin_exists = False
    for user in users_data.get('users', []):
        if user.get('username') == ADMIN_USERNAME:
            admin_exists = True
            break
    
    # Create admin user if not exists
    if not admin_exists:
        # Create a hash of the admin password
        hashed_password = hash_password(ADMIN_PASSWORD)
        
        # Create admin user object
        admin_user = {
            "id": str(uuid.uuid4()),
            "username": ADMIN_USERNAME,
            "password": hashed_password,
            "role": "admin",
            "approved": True,
            "created_at": datetime.now().isoformat(),
            "theme": "matrix"  # Force matrix theme for admin
        }
        
        # Add admin user to users data
        users_data.setdefault('users', []).append(admin_user)
        
        # Save updated users data
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=2)

def is_authenticated():
    """Check if user is authenticated"""
    return 'authenticated' in st.session_state and st.session_state.authenticated

def is_admin():
    """Check if the current authenticated user is an admin"""
    if not is_authenticated():
        return False
    
    user = st.session_state.get('user', {})
    return user.get('role') == 'admin'

def check_user_authenticated():
    """Check if user is authenticated, redirect to login if not"""
    if not is_authenticated() or 'user' not in st.session_state:
        return False
    return True

def check_auth():
    """Alias for check_user_authenticated for backward compatibility"""
    return check_user_authenticated()

def get_user_info():
    """Get the current user information"""
    if 'user' in st.session_state:
        return st.session_state.user
    return {'username': 'Guest', 'role': 'guest'}

def load_users():
    """
    Load users from the users.json file
    
    Returns:
        dict: User data dictionary
    """
    # Create the saved_data directory if it doesn't exist
    os.makedirs(SAVED_DATA_DIR, exist_ok=True)
    
    # Check if users file exists, create it if not
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({"users": []}, f)
    
    # Load existing users data
    with open(USERS_FILE, 'r') as f:
        users_data = json.load(f)
    
    return users_data

def save_users(users_data):
    """
    Save users data to the users.json file
    
    Args:
        users_data (dict): User data dictionary to save
    """
    # Create the saved_data directory if it doesn't exist
    os.makedirs(SAVED_DATA_DIR, exist_ok=True)
    
    # Save updated users data
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=2)

def update_user_theme(user_id, theme):
    """Update a user's theme preference"""
    # Load existing users data
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users_data = json.load(f)
        
        # Update the user's theme
        for user in users_data.get('users', []):
            if user.get('id') == user_id:
                user['theme'] = theme
                break
        
        # Save updated users data
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=2)

def register_user(username, password, confirm_password):
    """Register a new user"""
    # Basic validation
    if not username or not password:
        return (False, "Username and password are required")
    
    if password != confirm_password:
        return (False, "Passwords do not match")
    
    # Create the saved_data directory if it doesn't exist
    os.makedirs(SAVED_DATA_DIR, exist_ok=True)
    
    # Load existing users data
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users_data = json.load(f)
    else:
        users_data = {"users": []}
    
    # Check if username already exists
    for user in users_data.get('users', []):
        if user.get('username') == username:
            return (False, "Username already exists")
    
    # Create a hash of the password
    hashed_password = hash_password(password)
    
    # Create user object
    new_user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password": hashed_password,
        "role": "user",
        "approved": False,  # New users need admin approval
        "created_at": datetime.now().isoformat(),
        "theme": "industrial"  # Default theme for new users
    }
    
    # Add new user to users data
    users_data.setdefault('users', []).append(new_user)
    
    # Save updated users data
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=2)
    
    return (True, "Registration successful. Please wait for admin approval.")

def login(username, password):
    """Log in a user"""
    # Basic validation
    if not username or not password:
        return (False, "Username and password are required")
    
    # Load users data
    if not os.path.exists(USERS_FILE):
        initialize_admin()
    
    with open(USERS_FILE, 'r') as f:
        users_data = json.load(f)
    
    # Check credentials
    for user in users_data.get('users', []):
        if user.get('username') == username:
            # Check if password matches
            hashed_password = hash_password(password)
            if user.get('password') == hashed_password or user.get('password_hash') == hashed_password:
                # Check if user is approved - older accounts may not have this field
                has_approval_field = 'approved' in user
                if has_approval_field and not user.get('approved', False):
                    return (False, "Your account is pending approval by an administrator")
                
                # Set user as authenticated in session state
                st.session_state.authenticated = True
                st.session_state.user = user
                
                # Track login time
                st.session_state.login_time = time.time()
                
                # Set theme based on user preference
                theme = user.get('theme', 'industrial')
                if user.get('role') == 'admin':
                    # Force matrix theme for admin users
                    theme = 'matrix'
                
                st.session_state.color_theme = theme
                
                # Automatically load the latest reports for the user
                if DATABASE_IMPORTS_AVAILABLE:
                    try:
                        logging.info(f"Automatically loading latest reports for user {username}")
                        reports_loaded = load_latest_reports()
                        if reports_loaded:
                            logging.info(f"Successfully loaded reports for user {username}")
                            return (True, "Login successful. Latest reports loaded automatically.")
                    except Exception as e:
                        logging.error(f"Error loading reports on login: {str(e)}")
                
                return (True, "Login successful")
            else:
                return (False, "Invalid password")
    
    return (False, "Username not found")

def authenticate(username, password):
    """Alias for login for backward compatibility"""
    return login(username, password)

def logout():
    """Log out a user"""
    # Save current user info before logout for data persistence
    current_username = None
    if 'user' in st.session_state and st.session_state.user:
        current_username = st.session_state.user.get('username')
        logging.info(f"Preserving data persistence for user: {current_username}")
    
    # Store report IDs and data before logout
    loaded_report_ids = {}
    if 'loaded_report_ids' in st.session_state:
        loaded_report_ids = st.session_state.loaded_report_ids.copy()
        logging.info(f"Preserving loaded report IDs: {loaded_report_ids}")
    
    # Store the actual report data before logout
    report_data = {
        'po_data': st.session_state.get('po_data'),
        'po_filename': st.session_state.get('po_filename'),
        'non_po_data': st.session_state.get('non_po_data'),
        'non_po_filename': st.session_state.get('non_po_filename'),
        'chemical_spend_data': st.session_state.get('chemical_spend_data'),
        'chemical_spend_filename': st.session_state.get('chemical_spend_filename'),
        'data': st.session_state.get('data'),
    }
    logging.info(f"Preserving report data for: {[k for k,v in report_data.items() if v is not None]}")
    
    # Clear authentication
    st.session_state.authenticated = False
    
    # Clear user data
    if 'user' in st.session_state:
        del st.session_state.user
    
    # Clear login time
    if 'login_time' in st.session_state:
        del st.session_state.login_time
    
    # Reset theme to default
    st.session_state.color_theme = 'industrial'
    
    # Restore report IDs and data after logout to maintain persistence
    if loaded_report_ids:
        st.session_state.loaded_report_ids = loaded_report_ids
        logging.info(f"Restored loaded report IDs for persistence after logout")
    
    # Restore the actual report data
    for key, value in report_data.items():
        if value is not None:
            st.session_state[key] = value
    logging.info(f"Restored report data after logout for persistence")

def get_all_users():
    """Get all users data"""
    if not os.path.exists(USERS_FILE):
        initialize_admin()
        
    with open(USERS_FILE, 'r') as f:
        users_data = json.load(f)
    
    return users_data.get('users', [])

def approve_user(user_id):
    """Approve a user registration"""
    if not os.path.exists(USERS_FILE):
        return False
    
    with open(USERS_FILE, 'r') as f:
        users_data = json.load(f)
    
    # Find and approve the user
    success = False
    for user in users_data.get('users', []):
        if user.get('id') == user_id:
            user['approved'] = True
            success = True
            break
    
    if success:
        # Save updated users data
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=2)
    
    return success

def delete_user(user_id):
    """Delete a user"""
    if not os.path.exists(USERS_FILE):
        return False
    
    with open(USERS_FILE, 'r') as f:
        users_data = json.load(f)
    
    # Find index of user to remove
    user_index = None
    for i, user in enumerate(users_data.get('users', [])):
        if user.get('id') == user_id:
            user_index = i
            break
    
    if user_index is not None:
        # Remove the user
        users_data['users'].pop(user_index)
        
        # Save updated users data
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=2)
        
        return True
    
    return False