"""
Report Management Utilities

This module provides functions for managing reports in the database,
including retrieving all reports, getting report metadata, and fetching report data.
"""

import sqlite3
import pandas as pd
import os
import json
from datetime import datetime
import logging
# No need to import from standardized_processor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database path
DB_PATH = 'saved_data/reports_database.db'

def get_connection():
    """Create a connection to the reports database with optimized settings."""
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute('PRAGMA journal_mode = WAL')
    return conn

def get_all_reports():
    """
    Get all reports from the database.
    
    Returns:
        list: List of dictionaries containing report metadata
    """
    if not os.path.exists(DB_PATH):
        logging.warning(f"Database file not found at {DB_PATH}")
        return []
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("PRAGMA table_info(reports)")
        columns = cursor.fetchall()
        logging.info(f"Database table columns: {columns}")
        
        # Get all reports with their metadata
        cursor.execute('''
            SELECT id, name, original_filename, report_type, uploaded_at, record_count, data_path, description
            FROM reports
        ''')
        
        reports = []
        for row in cursor.fetchall():
            report_id, name, original_filename, report_type, uploaded_at, record_count, data_path, description = row
            
            # Log the exact data from database
            logging.info(f"Report ID {report_id}: name='{name}', filename='{original_filename}', type='{report_type}'")
            
            # Process filename to extract more meaningful names
            display_name = name or original_filename
            if not display_name and data_path:
                # Extract filename from data path if name is empty
                display_name = os.path.basename(data_path)
            
            # Format the display name to be more user-friendly
            friendly_name = display_name
            if friendly_name and friendly_name.startswith('Chemical_Spend_by_Supplier_-_'):
                friendly_name = friendly_name.replace('Chemical_Spend_by_Supplier_-_', '')
            elif friendly_name and friendly_name.startswith('PO_Line_Detail_-_'):
                friendly_name = friendly_name.replace('PO_Line_Detail_-_', 'PO Detail - ')
            elif friendly_name and friendly_name.startswith('Non-PO_Invoice_Chemical_GL_-_'):
                friendly_name = friendly_name.replace('Non-PO_Invoice_Chemical_GL_-_', 'Non-PO Invoice - ')
            
            # Create report object with the available columns
            report = {
                'id': report_id,
                'name': friendly_name or display_name or f"Report {report_id}",
                'original_name': name,  # Keep the original name for reference
                'filename': original_filename or os.path.basename(data_path) if data_path else f"Unknown_{report_id}",
                'report_type': report_type,
                'upload_date': uploaded_at,
                'record_count': record_count,
                'data_path': data_path,
                'description': description if description else ""
            }
            
            reports.append(report)
        
        conn.close()
        logging.info(f"Retrieved {len(reports)} reports from database")
        return reports
        
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return []
    except Exception as e:
        logging.error(f"Error getting reports: {e}")
        return []

def get_report_metadata(report_id):
    """
    Get metadata for a specific report.
    
    Args:
        report_id: ID of the report
        
    Returns:
        dict: Report metadata
    """
    if not os.path.exists(DB_PATH):
        logging.warning(f"Database file not found at {DB_PATH}")
        return None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get report metadata
        cursor.execute('''
            SELECT id, name, original_filename, report_type, uploaded_at, record_count, data_path, description
            FROM reports 
            WHERE id = ?
        ''', (report_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            logging.warning(f"Report with ID {report_id} not found")
            return None
        
        report_id, name, original_filename, report_type, uploaded_at, record_count, data_path, description = row
        
        # Log the exact data from database for debugging
        logging.info(f"Report metadata for ID {report_id}: name='{name}', filename='{original_filename}', type='{report_type}'")
        
        # Process filename to extract more meaningful names
        display_name = name or original_filename
        if not display_name and data_path:
            # Extract filename from data path if name is empty
            display_name = os.path.basename(data_path)
            
        # Format the display name to be more user-friendly
        friendly_name = display_name
        if friendly_name and friendly_name.startswith('Chemical_Spend_by_Supplier_-_'):
            friendly_name = friendly_name.replace('Chemical_Spend_by_Supplier_-_', '')
        elif friendly_name and friendly_name.startswith('PO_Line_Detail_-_'):
            friendly_name = friendly_name.replace('PO_Line_Detail_-_', 'PO Detail - ')
        elif friendly_name and friendly_name.startswith('Non-PO_Invoice_Chemical_GL_-_'):
            friendly_name = friendly_name.replace('Non-PO_Invoice_Chemical_GL_-_', 'Non-PO Invoice - ')
        
        # Create report object
        report = {
            'id': report_id,
            'name': friendly_name or display_name or f"Report {report_id}",
            'original_name': name,  # Keep the original name for reference
            'filename': original_filename or os.path.basename(data_path) if data_path else f"Unknown_{report_id}",
            'report_type': report_type,
            'upload_date': uploaded_at,
            'record_count': record_count,
            'data_path': data_path,
            'description': description if description else ""
        }
        
        return report
        
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None
    except Exception as e:
        logging.error(f"Error getting report metadata: {e}")
        return None

def get_dataset_by_id(report_id):
    """
    Get a dataset by its ID.
    
    Args:
        report_id: ID of the report
        
    Returns:
        DataFrame or None: The dataset as a pandas DataFrame, or None if not found
    """
    logging.debug(f"GET DATASET DEBUG: Fetching dataset with ID {report_id}")
    if not os.path.exists(DB_PATH):
        logging.warning(f"Database file not found at {DB_PATH}")
        return None
    
    try:
        logging.info(f"Database initialized successfully at {DB_PATH}")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Debug information
        cursor.execute("SELECT COUNT(*) FROM reports WHERE id = ?", (report_id,))
        count = cursor.fetchone()[0]
        logging.debug(f"Found {count} reports with ID {report_id}")
        
        # Get the report record
        cursor.execute('''
            SELECT data_path, report_type
            FROM reports 
            WHERE id = ?
        ''', (report_id,))
        
        row = cursor.fetchone()
        
        if not row:
            logging.warning(f"Report with ID {report_id} not found")
            conn.close()
            return None
        
        data_path, report_type = row
        
        if not os.path.exists(data_path):
            logging.warning(f"CSV file not found at {data_path}")
            conn.close()
            return None
        
        # Load the CSV file
        df = pd.read_csv(data_path)
        logging.info(f"Loaded raw dataset from CSV: {data_path}")
        
        # Close connection
        conn.close()
        
        return df
        
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None
    except Exception as e:
        logging.error(f"Error getting dataset: {e}")
        return None

def get_reports():
    """
    Get all reports from the database.
    
    Returns:
        list: List of dictionaries containing report metadata
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get all reports with their metadata
        cursor.execute('''
            SELECT id, name, original_filename, report_type, uploaded_at, record_count
            FROM reports
            ORDER BY uploaded_at DESC
        ''')
        
        reports = []
        for row in cursor.fetchall():
            report_id, name, original_filename, report_type, uploaded_at, record_count = row
            reports.append({
                'id': report_id,
                'name': name,
                'original_filename': original_filename,
                'report_type': report_type,
                'uploaded_at': uploaded_at,
                'record_count': record_count
            })
        
        conn.close()
        logging.info(f"Retrieved {len(reports)} reports from database")
        return reports
        
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None
    except Exception as e:
        logging.error(f"Error getting reports: {e}")
        return None

def load_report(report_id):
    """
    Load a report by its ID.
    
    Args:
        report_id: ID of the report
        
    Returns:
        Tuple of (DataFrame, report_metadata) or (None, None) if not found
    """
    # Get report metadata
    metadata = get_report_metadata(report_id)
    if not metadata:
        return None, None
    
    # Get dataset
    dataset = get_dataset_by_id(report_id)
    if dataset is None:
        return None, metadata
    
    return dataset, metadata

def get_report_data(report_id):
    """
    Get report data as a DataFrame.
    
    Args:
        report_id: ID of the report
        
    Returns:
        DataFrame or None: The dataset as a pandas DataFrame, or None if not found
    """
    dataset, _ = load_report(report_id)
    return dataset