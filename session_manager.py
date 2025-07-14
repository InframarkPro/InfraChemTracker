"""
Session State Manager

This module provides functions to manage Streamlit session state persistence
across page refreshes and navigation.
"""
import streamlit as st
import logging
from utils.unified_database import load_saved_dataset, list_saved_datasets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """
    Initialize all required session state variables if they don't exist
    """
    # Basic data variables
    data_vars = [
        'data', 'po_data', 'non_po_data', 'blended_data', 'chemical_spend_data',
        'original_data', 'original_columns', 'all_datasets'
    ]
    
    for var in data_vars:
        if var not in st.session_state:
            st.session_state[var] = None
    
    # File tracking variables
    file_vars = [
        'po_filename', 'non_po_filename', 'chemical_spend_filename',
        'last_po_uploaded_time', 'last_non_po_uploaded_time', 'last_chemical_spend_uploaded_time'
    ]
    
    for var in file_vars:
        if var not in st.session_state:
            st.session_state[var] = None
    
    # Tracking and selection variables
    if 'report_type' not in st.session_state:
        st.session_state.report_type = None
    if 'selected_report_id' not in st.session_state:
        st.session_state.selected_report_id = None
    if 'loaded_report_ids' not in st.session_state:
        st.session_state.loaded_report_ids = {}
        
    # Navigation variables
    # Only set the default page if it doesn't exist or if explicit navigation is needed
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "main"
        
    # Authentication persistence
    if 'persistent_auth' not in st.session_state:
        # By default, persistent auth is enabled for easier user experience
        st.session_state.persistent_auth = True
        
    # Supplier selection variables for drill-down functionality
    if 'selected_supplier' not in st.session_state:
        st.session_state.selected_supplier = None
    if 'show_supplier_details' not in st.session_state:
        st.session_state.show_supplier_details = False
        
    # Delete confirmation variables
    if 'delete_pressed' not in st.session_state:
        st.session_state.delete_pressed = False
    if 'delete_confirmed' not in st.session_state:
        st.session_state.delete_confirmed = False

def reload_datasets_if_needed():
    """
    Reload datasets from the database if they're in loaded_report_ids
    but not present in session state
    """
    # Debug logging
    print("DEBUG - reload_datasets_if_needed called")
    print(f"DEBUG - Session state keys: {list(st.session_state.keys())}")
    
    if 'loaded_report_ids' in st.session_state:
        print(f"DEBUG - loaded_report_ids in session: {st.session_state.loaded_report_ids}")
    
    # Check if we have any report IDs that need reloading from session state
    if 'loaded_report_ids' not in st.session_state or not st.session_state.loaded_report_ids:
        print("DEBUG - No loaded_report_ids found in session state, checking persistence file")
        
        # Check if there's a persistence file
        try:
            import os
            import json
            import glob
            
            # Find the most recent persistence file
            persistence_files = glob.glob('saved_data/persistence*.json')
            if persistence_files:
                print(f"DEBUG - Found {len(persistence_files)} persistence files")
                
                # Try to load from user-specific file if user is authenticated
                user_file = None
                if 'user' in st.session_state and st.session_state.user and 'username' in st.session_state.user:
                    username = st.session_state.user['username']
                    user_file = f'saved_data/persistence_{username}.json'
                    
                # Use user-specific file if it exists, otherwise use the first one found
                if user_file and user_file in persistence_files:
                    persistence_file = user_file
                else:
                    persistence_file = persistence_files[0]
                
                print(f"DEBUG - Using persistence file: {persistence_file}")
                
                # Load the persistence data
                with open(persistence_file, 'r') as f:
                    persistence_data = json.load(f)
                
                # Check if it has loaded_report_ids
                if 'loaded_report_ids' in persistence_data and persistence_data['loaded_report_ids']:
                    print(f"DEBUG - Found loaded_report_ids in persistence file: {persistence_data['loaded_report_ids']}")
                    
                    # Initialize session state if needed
                    if 'loaded_report_ids' not in st.session_state:
                        st.session_state.loaded_report_ids = {}
                    
                    # Copy persistence data to session state
                    for report_type, report_id in persistence_data['loaded_report_ids'].items():
                        st.session_state.loaded_report_ids[report_type] = report_id
                    
                    print(f"DEBUG - Restored loaded_report_ids to session state: {st.session_state.loaded_report_ids}")
                else:
                    print("DEBUG - No loaded_report_ids found in persistence file")
            else:
                print("DEBUG - No persistence files found")
        except Exception as e:
            print(f"DEBUG - Error loading persistence file: {str(e)}")
    
    # Now check if we have any report IDs to reload
    if 'loaded_report_ids' not in st.session_state or not st.session_state.loaded_report_ids:
        print("DEBUG - Still no loaded_report_ids after checking persistence, nothing to reload")
        return
    
    reload_succeeded = False
    
    # PO Line Detail data
    if (('po_data' not in st.session_state or st.session_state.po_data is None) and 
        'po_line_detail' in st.session_state.loaded_report_ids):
        report_id = st.session_state.loaded_report_ids['po_line_detail']
        logger.info(f"Reloading PO Line Detail dataset with ID: {report_id}")
        
        try:
            df, report_info = load_saved_dataset(report_id)
            if df is not None:
                st.session_state.po_data = df
                st.session_state.po_filename = report_info.get('original_filename', '')
                reload_succeeded = True
                logger.info(f"Successfully reloaded PO Line Detail dataset with ID: {report_id}")
        except Exception as e:
            logger.error(f"Failed to reload PO Line Detail dataset with ID {report_id}: {str(e)}")
    
    # Non-PO Invoice data
    if (('non_po_data' not in st.session_state or st.session_state.non_po_data is None) and 
        'non_po_invoice' in st.session_state.loaded_report_ids):
        report_id = st.session_state.loaded_report_ids['non_po_invoice']
        logger.info(f"Reloading Non-PO Invoice dataset with ID: {report_id}")
        
        try:
            df, report_info = load_saved_dataset(report_id)
            if df is not None:
                st.session_state.non_po_data = df
                st.session_state.non_po_filename = report_info.get('original_filename', '')
                reload_succeeded = True
                logger.info(f"Successfully reloaded Non-PO Invoice dataset with ID: {report_id}")
        except Exception as e:
            logger.error(f"Failed to reload Non-PO Invoice dataset with ID {report_id}: {str(e)}")
    
    # Chemical Spend by Supplier data
    if (('chemical_spend_data' not in st.session_state or st.session_state.chemical_spend_data is None) and 
        'chemical_spend_by_supplier' in st.session_state.loaded_report_ids):
        report_id = st.session_state.loaded_report_ids['chemical_spend_by_supplier']
        logger.info(f"Reloading Chemical Spend by Supplier dataset with ID: {report_id}")
        
        try:
            df, report_info = load_saved_dataset(report_id)
            if df is not None:
                st.session_state.chemical_spend_data = df
                st.session_state.chemical_spend_filename = report_info.get('original_filename', '')
                reload_succeeded = True
                logger.info(f"Successfully reloaded Chemical Spend by Supplier dataset with ID: {report_id}")
        except Exception as e:
            logger.error(f"Failed to reload Chemical Spend by Supplier dataset with ID {report_id}: {str(e)}")
    
    # Update combined data if needed
    if reload_succeeded:
        update_combined_data()

def update_loaded_report_id(report_type, report_id):
    """
    Update the loaded_report_ids dictionary with a new report ID
    
    Args:
        report_type: The type of report ('po_line_detail', 'non_po_invoice', 
                    'chemical_spend_by_supplier', 'supplier_unit_cost')
        report_id: The ID of the loaded report
    """
    if 'loaded_report_ids' not in st.session_state:
        st.session_state.loaded_report_ids = {}
    
    # Save to session state
    st.session_state.loaded_report_ids[report_type] = report_id
    logger.info(f"Updated loaded report ID for {report_type}: {report_id}")
    
    # Also save to file for persistence across sessions
    try:
        import os
        import json
        
        # Make sure directory exists
        os.makedirs('saved_data', exist_ok=True)
        
        # Create a user-specific persistence file using username if authenticated
        persistence_file = 'saved_data/persistence.json'
        if 'user' in st.session_state and st.session_state.user and 'username' in st.session_state.user:
            username = st.session_state.user['username']
            persistence_file = f'saved_data/persistence_{username}.json'
        
        # Load existing data or create new
        persistence_data = {}
        if os.path.exists(persistence_file):
            try:
                with open(persistence_file, 'r') as f:
                    persistence_data = json.load(f)
            except:
                persistence_data = {}
        
        # Update loaded_report_ids
        if 'loaded_report_ids' not in persistence_data:
            persistence_data['loaded_report_ids'] = {}
        persistence_data['loaded_report_ids'][report_type] = report_id
        
        # Save back to file
        with open(persistence_file, 'w') as f:
            json.dump(persistence_data, f, indent=2)
        
        print(f"DEBUG - Saved report ID {report_id} for {report_type} to persistence file")
    except Exception as e:
        logger.error(f"Failed to save persistence data: {str(e)}")
    
def remove_loaded_report_id(report_type):
    """
    Remove a report ID from the loaded_report_ids dictionary
    
    Args:
        report_type: The type of report to remove ('po_line_detail', 'non_po_invoice', 
                    'chemical_spend_by_supplier', 'supplier_unit_cost')
    
    Returns:
        bool: True if the report was removed, False if it wasn't in the dictionary
    """
    removed = False
    
    # Remove from session state
    if 'loaded_report_ids' in st.session_state and report_type in st.session_state.loaded_report_ids:
        del st.session_state.loaded_report_ids[report_type]
        logger.info(f"Removed loaded report ID for {report_type}")
        removed = True
    
    # Also remove from persistence file
    try:
        import os
        import json
        
        # Find the correct persistence file
        persistence_file = 'saved_data/persistence.json'
        if 'user' in st.session_state and st.session_state.user and 'username' in st.session_state.user:
            username = st.session_state.user['username']
            persistence_file = f'saved_data/persistence_{username}.json'
        
        # Update the file if it exists
        if os.path.exists(persistence_file):
            try:
                with open(persistence_file, 'r') as f:
                    persistence_data = json.load(f)
                
                # Remove the report ID if it exists
                if 'loaded_report_ids' in persistence_data and report_type in persistence_data['loaded_report_ids']:
                    del persistence_data['loaded_report_ids'][report_type]
                    
                    # Save the updated data
                    with open(persistence_file, 'w') as f:
                        json.dump(persistence_data, f, indent=2)
                    
                    print(f"DEBUG - Removed report ID for {report_type} from persistence file")
                    removed = True
            except Exception as e:
                print(f"DEBUG - Error updating persistence file: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to update persistence file: {str(e)}")
    
    return removed

def get_loaded_report_id(report_type):
    """
    Get the report ID for a specific report type from loaded_report_ids
    
    Args:
        report_type: The type of report to retrieve ('po_line_detail', 'non_po_invoice', 
                    'chemical_spend_by_supplier', 'supplier_unit_cost')
        
    Returns:
        int: Report ID if found, None otherwise
    """
    # Initialize if not exists
    if 'loaded_report_ids' not in st.session_state:
        st.session_state.loaded_report_ids = {}
        
    # Return the report ID if it exists
    if report_type in st.session_state.loaded_report_ids:
        return st.session_state.loaded_report_ids[report_type]
    else:
        return None

def update_combined_data():
    """
    Update the combined data in session state based on available PO and Non-PO data
    """
    # Check if any of them exist
    has_po_data = 'po_data' in st.session_state and st.session_state.po_data is not None
    has_non_po_data = 'non_po_data' in st.session_state and st.session_state.non_po_data is not None
    
    # Only combine PO and Non-PO data for the unified dashboard
    if has_po_data and has_non_po_data:
        # Use both PO and Non-PO data
        import pandas as pd
        st.session_state.data = pd.concat([st.session_state.po_data, st.session_state.non_po_data])
        logger.info("Updated combined data with both PO and Non-PO data")
    elif has_po_data:
        # Use only PO data
        st.session_state.data = st.session_state.po_data
        logger.info("Updated combined data with only PO data")
    elif has_non_po_data:
        # Use only Non-PO data
        st.session_state.data = st.session_state.non_po_data
        logger.info("Updated combined data with only Non-PO data")