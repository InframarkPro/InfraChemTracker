"""
Unified Database Module

This module consolidates all database-related functionality from both database.py and data_storage.py
into a single, consistent interface for interacting with the SQLite database.
"""

import pandas as pd
import os
import json
from datetime import datetime
import sqlite3
import pickle
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('database')

# Directory for storing uploaded data
DATA_DIR = "saved_data"
DB_PATH = os.path.join(DATA_DIR, "reports_database.db")

def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory: {DATA_DIR}")

def init_database():
    """
    Initialize the SQLite database with required tables.
    If the database doesn't exist, it will be created.

    Returns:
        str: Path to the database file
    """
    # Create the database file in the saved_data directory
    ensure_data_dir()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create reports table to store metadata about uploaded reports
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            report_type TEXT NOT NULL,
            uploaded_at TIMESTAMP NOT NULL,
            record_count INTEGER NOT NULL,
            data_path TEXT NOT NULL,
            pickle_path TEXT NOT NULL,
            description TEXT
        )
        ''')

        # Create supplier_unit_prices table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS supplier_unit_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            SupplierName TEXT NOT NULL,
            ItemNumber TEXT,
            SupplierItemNumber TEXT,
            ItemDescription TEXT,
            UnitPrice DECIMAL(10,4) NOT NULL,
            Unit TEXT,
            SupplierItemDescription TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(SupplierName, ItemNumber, SupplierItemNumber)
        )
        ''')


        conn.commit()
        conn.close()
        logger.info(f"Database initialized successfully at {DB_PATH}")

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

    return DB_PATH

def save_uploaded_data(df, filename, report_type=None, description=None, custom_name=None):
    """
    Save uploaded data to disk and database with timestamp using transaction protection

    Args:
        df: DataFrame to save
        filename: Original filename
        report_type: Type of report (e.g., 'PO Line Detail', 'Non-PO Invoice')
        description: Optional description for the report
        custom_name: Optional user-provided name for the report (will be sanitized)

    Returns:
        save_info: Dict with save metadata
    """
    # Verify that data frame is valid
    if df is None or len(df) == 0:
        raise ValueError("Cannot save empty dataframe")

    ensure_data_dir()
    db_path = init_database()
    saved_files = []
    conn = None

    # Generate a timestamp for the filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Clean up the filename for file system compatibility
    clean_filename = filename.replace(" ", "_").replace(":", "-")
    name_without_ext = os.path.splitext(clean_filename)[0]

    # Use custom name if provided
    display_name = custom_name if custom_name else name_without_ext
    # Sanitize display name
    display_name = display_name.strip().replace(" ", "_").replace(":", "-")

    # Create the save filenames
    csv_filename = f"{name_without_ext}_{timestamp}.csv"
    pickle_filename = f"{name_without_ext}_{timestamp}.pkl"
    meta_filename = f"{name_without_ext}_{timestamp}_meta.json"

    # Create the full paths
    csv_path = os.path.join(DATA_DIR, csv_filename)
    pickle_path = os.path.join(DATA_DIR, pickle_filename)
    meta_path = os.path.join(DATA_DIR, meta_filename)

    try:
        # Save to CSV
        df.to_csv(csv_path, index=False)
        saved_files.append(csv_path)
        logger.info(f"Data saved to CSV: {csv_path}")

        # Save to Pickle for faster loading
        with open(pickle_path, 'wb') as f:
            pickle.dump(df, f)
        saved_files.append(pickle_path)
        logger.info(f"Data saved to Pickle: {pickle_path}")

        # Create metadata
        metadata = {
            "original_filename": filename,
            "display_name": display_name,
            "report_type": report_type or "Unknown",
            "uploaded_at": datetime.now().isoformat(),
            "record_count": len(df),
            "columns": df.columns.tolist(),
            "description": description or "",
            "column_dtypes": {col: str(df[col].dtype) for col in df.columns}
        }

        # Save metadata to JSON
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        saved_files.append(meta_path)
        logger.info(f"Metadata saved to JSON: {meta_path}")

        # Save metadata to database with transaction protection
        conn = sqlite3.connect(db_path)

        try:
            # Start transaction
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO reports (
                name, original_filename, report_type, uploaded_at, record_count, 
                data_path, pickle_path, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                display_name,  # Use display_name instead of name_without_ext
                filename,
                report_type or "Unknown",
                metadata["uploaded_at"],
                len(df),
                csv_path,
                pickle_path,
                description or ""
            ))

            # Get the inserted record ID
            report_id = cursor.lastrowid

            # Commit transaction
            conn.commit()
            logger.info(f"Metadata saved to database with ID: {report_id}")

            # Return info about the save operation
            return {
                "id": report_id,
                "name": display_name,
                "saved_filename": csv_filename,
                "original_filename": filename,
                "report_type": report_type or "Unknown",
                "record_count": len(df),
                "uploaded_at": metadata["uploaded_at"],
                "data_path": csv_path,
                "pickle_path": pickle_path,
                "description": description or ""
            }

        except Exception as db_error:
            # Rollback transaction on database error
            if conn:
                conn.rollback()
            logger.error(f"Database error while saving data: {str(db_error)}")
            raise
        finally:
            # Close connection
            if conn:
                conn.close()

    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        # Clean up any created files
        for path in saved_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"Cleaned up file after error: {path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up file {path}: {str(cleanup_error)}")
        raise

def list_saved_datasets():
    """
    List all saved datasets from the database

    Returns:
        datasets: List of dataset info dicts
    """
    ensure_data_dir()
    db_path = init_database()

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()

        cursor.execute('''
        SELECT id, name, original_filename, report_type, uploaded_at, record_count, data_path, pickle_path, description
        FROM reports
        ORDER BY uploaded_at DESC
        ''')

        datasets = []
        columns = [col[0] for col in cursor.description]  # Get column names
        for row in cursor.fetchall():
            # Create a dictionary from row values with column names as keys
            dataset = {columns[i]: row[i] for i in range(len(columns))}
            datasets.append(dataset)

        conn.close()
        logger.info(f"Retrieved {len(datasets)} datasets from database")

        return datasets
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        return []

def get_dataset_by_id(report_id):
    """
    Get dataset info by ID

    Args:
        report_id: ID of the report

    Returns:
        dataset_info: Dict with dataset info or None if not found
    """
    print(f"GET DATASET DEBUG: Fetching dataset with ID {report_id}")
    db_path = init_database()
    print(f"GET DATASET DEBUG: Using database at: {db_path}")

    try:
        # Make sure report_id is an integer
        if isinstance(report_id, str) and report_id.isdigit():
            report_id = int(report_id)

        print(f"GET DATASET DEBUG: Using report_id (type: {type(report_id)}): {report_id}")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # First check if the report exists at all
        cursor.execute('SELECT COUNT(*) FROM reports WHERE id = ?', (report_id,))
        count = cursor.fetchone()[0]
        print(f"GET DATASET DEBUG: Found {count} reports with ID {report_id}")

        if count == 0:
            print(f"GET DATASET DEBUG: No report found with ID {report_id}")
            conn.close()
            return None

        # If it exists, fetch the details
        print(f"GET DATASET DEBUG: Executing SELECT query for ID {report_id}")
        cursor.execute('''
        SELECT id, name, original_filename, report_type, uploaded_at, record_count, data_path, pickle_path, description
        FROM reports
        WHERE id = ?
        ''', (report_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            # Create a dictionary from row values with column names as keys
            columns = [col[0] for col in cursor.description]
            dataset = {columns[i]: row[i] for i in range(len(columns))}
            print(f"GET DATASET DEBUG: Successfully retrieved dataset with ID: {report_id}")
            logger.info(f"Retrieved dataset with ID: {report_id}")
            return dataset
        else:
            print(f"GET DATASET DEBUG: Dataset with ID {report_id} not found after executing query")
            logger.warning(f"Dataset with ID {report_id} not found")
            return None
    except Exception as e:
        print(f"GET DATASET DEBUG: Error getting dataset by ID: {str(e)}")
        logger.error(f"Error getting dataset by ID: {str(e)}")
        import traceback
        print(f"GET DATASET DEBUG: Traceback: {traceback.format_exc()}")
        return None

def load_saved_dataset(dataset_id_or_path):
    """
    Load a saved dataset by ID or file path

    Args:
        dataset_id_or_path: The dataset ID or file path to load

    Returns:
        tuple: (df, dataset_info) - The loaded DataFrame and dataset info or (None, None) if not found
    """
    # Check if input is a numeric ID or a string path
    is_id = isinstance(dataset_id_or_path, int) or (isinstance(dataset_id_or_path, str) and dataset_id_or_path.isdigit())

    try:
        if is_id:
            # Get info by ID
            dataset_info = get_dataset_by_id(int(dataset_id_or_path))
            if not dataset_info:
                logger.warning(f"Dataset with ID {dataset_id_or_path} not found")
                return None, None

            pickle_path = dataset_info.get('pickle_path')
            data_path = dataset_info.get('data_path')

            # Get the report type to determine processing
            report_type = dataset_info.get('report_type', '')
            internal_report_type = None

            # Map to internal report type
            if 'PO Line Detail' in report_type:
                internal_report_type = 'po_line_detail'
            elif 'Non-PO Invoice' in report_type:
                internal_report_type = 'non_po_invoice'
            elif 'Chemical Spend by Supplier' in report_type:
                internal_report_type = 'chemical_spend_by_supplier'

            # Load from CSV and reprocess to ensure latest calculations
            if data_path and os.path.exists(data_path):
                try:
                    # Load the raw data
                    raw_df = pd.read_csv(data_path)
                    logger.info(f"Loaded raw dataset from CSV: {data_path}")

                    # Import and use standardized processor
                    from utils.standardized_processor import standardize_columns
                    logger.info(f"Reprocessing with standardized_processor using type: {internal_report_type}")

                    # Reprocess with the latest code
                    df = standardize_columns(raw_df, internal_report_type)

                    # Debug info for Total_Cost
                    if 'Total_Cost' in df.columns:
                        total_cost_sum = df['Total_Cost'].sum()
                        logger.info(f"Total Cost after reprocessing: ${total_cost_sum:,.2f}")

                    return df, dataset_info
                except Exception as e:
                    logger.error(f"Error reprocessing data: {str(e)}")
                    logger.info("Falling back to original loading method")

            # Fall back to pickle if CSV processing fails or CSV doesn't exist
            if pickle_path and os.path.exists(pickle_path):
                with open(pickle_path, 'rb') as f:
                    df = pickle.load(f)
                logger.info(f"Loaded dataset from pickle: {pickle_path}")
                return df, dataset_info

            # Final fallback to CSV if pickle not available
            elif data_path and os.path.exists(data_path):
                df = pd.read_csv(data_path)
                logger.info(f"Loaded dataset from CSV without reprocessing: {data_path}")
                return df, dataset_info

            else:
                logger.error(f"Dataset files not found for ID {dataset_id_or_path}")
                return None, dataset_info

        else:
            # Try to load directly from path
            path = dataset_id_or_path

            if not os.path.exists(path):
                logger.warning(f"File not found: {path}")
                return None, None

            # Determine file type and load - ensure path is a string first
            if not isinstance(path, str):
                logger.error(f"Path is not a string: {path}")
                return None, None

            # Now we can safely use string methods like endswith
            if path.endswith('.pkl'):
                with open(path, 'rb') as f:
                    df = pickle.load(f)
                logger.info(f"Loaded dataset from pickle: {path}")
            elif path.endswith('.csv'):
                df = pd.read_csv(path)
                logger.info(f"Loaded dataset from CSV: {path}")
            elif path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(path)
                logger.info(f"Loaded dataset from Excel: {path}")
            else:
                logger.error(f"Unsupported file format: {path}")
                return None, None

            # Create a basic info dict
            basename = os.path.basename(path) if isinstance(path, str) else "unknown"
            dataset_info = {
                'id': None,
                'name': basename,
                'original_filename': basename,
                'data_path': path,
                'record_count': len(df) if df is not None else 0
            }

            return df, dataset_info

    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        return None, None

    logger.warning("Dataset not found or could not be loaded")
    return None, None

def delete_dataset(dataset_id):
    """
    Delete a dataset from the database and its files using transaction protection

    Args:
        dataset_id: ID of the dataset to delete

    Returns:
        success: Boolean indicating success
    """
    print(f"DEBUG DELETE: Starting deletion of dataset with ID {dataset_id}")
    logger.info(f"Starting deletion of dataset with ID {dataset_id}")

    # Make sure dataset_id is an integer
    if isinstance(dataset_id, str) and dataset_id.isdigit():
        dataset_id = int(dataset_id)
    
    print(f"DEBUG DELETE: Using dataset_id (type: {type(dataset_id)}): {dataset_id}")

    # Initialize database
    db_path = init_database()
    print(f"DEBUG DELETE: Using database at: {db_path}")
    conn = None

    try:
        # Establish connection
        conn = sqlite3.connect(db_path)

        # Start transaction
        conn.execute("BEGIN TRANSACTION")

        # Get dataset info within transaction
        cursor = conn.cursor()
        cursor.execute('''
        SELECT id, name, original_filename, report_type, uploaded_at, 
               record_count, data_path, pickle_path, description
        FROM reports 
        WHERE id = ?
        ''', (dataset_id,))

        row = cursor.fetchone()

        if not row:
            logger.warning(f"Dataset with ID {dataset_id} not found for deletion")
            conn.rollback()
            return False

        # Create dataset info dictionary
        columns = ['id', 'name', 'original_filename', 'report_type', 'uploaded_at', 
                  'record_count', 'data_path', 'pickle_path', 'description']
        dataset_info = dict(zip(columns, row))

        # Print detailed debug info
        print(f"DEBUG DELETE: Found dataset info:")
        for key, value in dataset_info.items():
            print(f"DEBUG DELETE:   {key}: {value}")
            
        logger.info(f"Found dataset info: {dataset_info}")

        # Delete from database within transaction
        cursor.execute('DELETE FROM reports WHERE id = ?', (dataset_id,))
        rows_affected = cursor.rowcount
        logger.info(f"SQL DELETE affected {rows_affected} rows")

        if rows_affected == 0:
            logger.warning(f"No rows deleted for dataset ID {dataset_id}")
            conn.rollback()
            return False

        # Collect file paths to delete
        paths_to_delete = []

        # Data file
        data_path = dataset_info.get('data_path')
        print(f"DEBUG DELETE: Data path: {data_path}")
        if data_path and isinstance(data_path, str):
            if os.path.exists(data_path):
                paths_to_delete.append(data_path)
                print(f"DEBUG DELETE: Added data file to delete list: {data_path}")
            else:
                print(f"DEBUG DELETE: Data file does not exist: {data_path}")

        # Metadata file
        if data_path and isinstance(data_path, str) and data_path.endswith('.csv'):
            meta_path = data_path.replace('.csv', '_meta.json')
            print(f"DEBUG DELETE: Checking metadata file: {meta_path}")
            if os.path.exists(meta_path):
                paths_to_delete.append(meta_path)
                print(f"DEBUG DELETE: Added metadata file to delete list: {meta_path}")
            else:
                print(f"DEBUG DELETE: Metadata file does not exist: {meta_path}")

        # Pickle file
        pickle_path = dataset_info.get('pickle_path')
        print(f"DEBUG DELETE: Pickle path: {pickle_path}")
        if pickle_path and isinstance(pickle_path, str):
            if os.path.exists(pickle_path):
                paths_to_delete.append(pickle_path)
                print(f"DEBUG DELETE: Added pickle file to delete list: {pickle_path}")
            else:
                print(f"DEBUG DELETE: Pickle file does not exist: {pickle_path}")
                
        print(f"DEBUG DELETE: Files to delete: {len(paths_to_delete)}")
        for i, path in enumerate(paths_to_delete):
            print(f"DEBUG DELETE: File {i+1}: {path}")

        # Commit the database deletion
        conn.commit()

        # Now delete the files (after successful database commit)
        deleted_files = []
        for path in paths_to_delete:
            try:
                os.remove(path)
                deleted_files.append(path)
                logger.info(f"Deleted file: {path}")
            except Exception as file_error:
                logger.warning(f"Could not delete file {path}: {str(file_error)}")

        logger.info(f"Successfully deleted dataset with ID {dataset_id} and {len(deleted_files)} files")
        return True

    except Exception as e:
        print(f"DEBUG DELETE: Error occurred: {str(e)}")
        logger.error(f"Error deleting dataset: {str(e)}")
        if conn:
            conn.rollback()
        import traceback
        tb = traceback.format_exc()
        print(f"DEBUG DELETE: Full traceback:\n{tb}")
        logger.error(f"Deletion traceback: {tb}")
        return False
    finally:
        # Always close the connection
        if conn:
            conn.close()

# Backwards compatibility functions for database.py
def get_all_reports():
    """
    Retrieve all reports from database - compatibility function

    Returns:
        List of report tuples in the format expected by the original function
    """
    # Get all datasets from unified database
    datasets = list_saved_datasets()

    # Convert to the format expected by the original function
    reports = []
    for dataset in datasets:
        # Create a tuple format compatible with the original function
        # id, filename, original_filename, report_type, upload_date, metadata
        data_path = dataset.get('data_path', '')
        filename = ''

        # Only try to extract filename if data_path is a string
        if isinstance(data_path, str) and data_path:
            filename = data_path.split('/')[-1]

        report = (
            dataset.get('id'),
            filename,  # Extract filename from path with type checking
            dataset.get('original_filename', ''),
            dataset.get('report_type', 'Unknown'),
            dataset.get('uploaded_at', ''),
            json.dumps({"record_count": dataset.get('record_count', 0)})
        )
        reports.append(report)

    return reports

def get_report_by_id(report_id):
    """
    Retrieve a specific report by ID - compatibility function

    Returns:
        Report tuple in the format expected by the original function
    """
    dataset = get_dataset_by_id(report_id)

    if dataset:
        # Convert to the format expected by the original function
        data_path = dataset.get('data_path', '')
        filename = ''

        # Only try to extract filename if data_path is a string
        if isinstance(data_path, str) and data_path:
            filename = data_path.split('/')[-1]

        return (
            dataset.get('id'),
            filename,  # Extract filename from path with type checking
            dataset.get('original_filename', ''),
            dataset.get('report_type', 'Unknown'),
            dataset.get('uploaded_at', ''),
            json.dumps({"record_count": dataset.get('record_count', 0)})
        )

    return None

def load_report_data(report_id):
    """
    Load report data by ID - compatibility function

    Returns:
        DataFrame with the report data
    """
    df, _ = load_saved_dataset(report_id)
    return df

def save_report_metadata(filename, original_filename, report_type, metadata):
    """
    Save report metadata to database - compatibility function

    Note: This function doesn't actually save data, only metadata.
    To save data, use save_uploaded_data instead.
    """
    logger.warning(f"save_report_metadata called, but doesn't save actual data. "
          f"Use save_uploaded_data instead.")

    # Return the metadata as if we'd saved it
    return {
        "filename": filename,
        "original_filename": original_filename,
        "report_type": report_type,
        "upload_date": datetime.now().isoformat(),
        "metadata": metadata
    }