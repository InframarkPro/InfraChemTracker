import pandas as pd
import os
import json
from datetime import datetime
import sqlite3
import pickle

# Directory for storing uploaded data
DATA_DIR = "saved_data"

def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def init_database():
    """Initialize the SQLite database with required tables"""
    # Create the database file in the saved_data directory
    ensure_data_dir()
    db_path = os.path.join(DATA_DIR, "reports_database.db")
    
    conn = sqlite3.connect(db_path)
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
    
    conn.commit()
    conn.close()
    
    return db_path

def save_uploaded_data(df, filename, report_type=None, description=None):
    """
    Save uploaded data to disk and database with timestamp
    
    Args:
        df: DataFrame to save
        filename: Original filename
        report_type: Type of report (e.g., 'PO Line Detail', 'Non-PO Invoice')
        description: Optional description for the report
        
    Returns:
        save_info: Dict with save metadata
    """
    print(f"\n=== SAVE UPLOADED DATA START: {report_type} ===")
    print(f"Data to save - Shape: {df.shape}, Columns: {list(df.columns)}")
    print(f"First row sample: {df.iloc[0].to_dict() if len(df) > 0 else 'No data'}")
    print(f"Data types: {df.dtypes}")
    
    try:
        ensure_data_dir()
        print("Data directory ensured")
        db_path = init_database()
        print(f"Database initialized at: {db_path}")
        
        # Create a timestamp for the saved file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(filename))[0]
        sanitized_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in base_name)
        print(f"Sanitized name: {sanitized_name}")
        
        # Create save path for CSV
        save_filename = f"{sanitized_name}_{timestamp}.csv"
        save_path = os.path.join(DATA_DIR, save_filename)
        
        # Create save path for pickle (faster loading)
        pickle_filename = f"{sanitized_name}_{timestamp}.pkl"
        pickle_path = os.path.join(DATA_DIR, pickle_filename)
        print(f"Save paths - CSV: {save_path}, Pickle: {pickle_path}")
        
        # Create a readable name for the dropdown
        display_name = f"{base_name} ({timestamp[:8]})"
        if report_type:
            display_name = f"{display_name} - {report_type}"
        print(f"Display name: {display_name}")
        
        # Convert datetime columns to string for CSV export
        df_to_save = df.copy()
        for col in df_to_save.columns:
            if pd.api.types.is_datetime64_any_dtype(df_to_save[col]):
                print(f"Converting datetime column {col} to string format for CSV saving")
                df_to_save[col] = df_to_save[col].dt.strftime('%Y-%m-%d')
                
        # Save the data in both formats with error handling
        print("Saving CSV file...")
        try:
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Save CSV file
            df_to_save.to_csv(save_path, index=False)
            print(f"Successfully saved CSV to {save_path}")
            
            # Verify the file exists
            if os.path.exists(save_path):
                print(f"CSV file verified at {save_path}")
            else:
                print(f"WARNING: CSV file not found after saving: {save_path}")
        except Exception as csv_err:
            print(f"ERROR saving CSV file: {str(csv_err)}")
            raise
        
        # Save the original dataframe as pickle for faster loading and to preserve datatypes
        print("Saving pickle file...")
        try:
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(pickle_path), exist_ok=True)
            
            # Save pickle file
            with open(pickle_path, 'wb') as f:
                pickle.dump(df, f)
            print(f"Successfully saved pickle to {pickle_path}")
            
            # Verify the file exists
            if os.path.exists(pickle_path):
                print(f"Pickle file verified at {pickle_path}")
            else:
                print(f"WARNING: Pickle file not found after saving: {pickle_path}")
        except Exception as pickle_err:
            print(f"ERROR saving pickle file: {str(pickle_err)}")
            raise
        
        # Create metadata
        print("Creating metadata...")
        metadata = {
            "name": display_name,
            "original_filename": filename,
            "saved_filename": save_filename,
            "pickle_filename": pickle_filename,
            "timestamp": timestamp,
            "date_saved": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "record_count": len(df),
            "columns": list(df.columns),
            "report_type": report_type or "Unknown"
        }
        
        # Save metadata to JSON
        metadata_path = os.path.join(DATA_DIR, f"{sanitized_name}_{timestamp}_meta.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        print(f"Metadata saved to {metadata_path}")
        
        # Add to database
        print("Adding to database...")
        report_id = None
        conn = None
        try:
            # Ensure database file exists and is writable
            try:
                with open(db_path, 'a'):
                    pass
                print(f"Successfully opened database at {db_path} for writing")
            except Exception as db_open_err:
                print(f"ERROR opening database file {db_path}: {str(db_open_err)}")
                raise
                
            print(f"Connecting to SQLite database at {db_path} with timeout 30.0 seconds")
            conn = sqlite3.connect(db_path, timeout=30.0)  # Increase timeout for busy database
            cursor = conn.cursor()
            
            # First verify the table exists
            print("Checking if reports table exists...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
            if not cursor.fetchone():
                print("Reports table doesn't exist! Recreating it...")
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
                conn.commit()
                print("Reports table created successfully")
                
            insert_query = '''
            INSERT INTO reports (name, original_filename, report_type, uploaded_at, record_count, data_path, pickle_path, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            current_time = datetime.now().isoformat()
            insert_values = (
                display_name,
                filename,
                report_type or "Unknown",
                current_time,
                len(df),
                save_path,
                pickle_path,
                description or ""
            )
            
            print(f"SQL values: {insert_values}")
            
            cursor.execute(insert_query, insert_values)
            conn.commit()  # Make sure to commit before getting lastrowid
            
            # Get the ID of the newly inserted report
            report_id = cursor.lastrowid
            if report_id:
                metadata['id'] = report_id
                print(f"Inserted with ID: {report_id}")
            else:
                print("WARNING: No report ID returned after insert")
                # Check if the insert actually happened
                cursor.execute('''SELECT id FROM reports WHERE name=? AND uploaded_at=?''', (display_name, current_time))
                result = cursor.fetchone()
                if result:
                    report_id = result[0]
                    metadata['id'] = report_id
                    print(f"Found report ID through query: {report_id}")
                else:
                    print("ERROR: Could not find inserted report in database")
        except sqlite3.Error as e:
            print(f"SQLite error during database operation: {e}")
            import traceback
            traceback.print_exc()
            
            # Verify database integrity
            print("Checking database integrity...")
            try:
                test_conn = sqlite3.connect(db_path)
                test_cursor = test_conn.cursor()
                test_cursor.execute("PRAGMA integrity_check")
                result = test_cursor.fetchone()
                print(f"Database integrity check result: {result}")
                test_conn.close()
            except Exception as integrity_err:
                print(f"Error during integrity check: {integrity_err}")
                
        except Exception as e:
            print(f"Unexpected error during database insert: {e}")
            import traceback
            traceback.print_exc()
            
            # Check if file paths are valid
            print(f"Verifying file paths - CSV: {os.path.exists(save_path)}, Pickle: {os.path.exists(pickle_path)}")
            
        finally:
            # Close connection if it was opened
            if conn:
                try:
                    conn.close()
                    print("Database connection closed")
                except Exception as e:
                    print(f"Error closing database connection: {e}")
        
        print(f"=== SAVE UPLOADED DATA COMPLETE: {report_type} ===\n")
        return metadata
    except Exception as e:
        print(f"ERROR in save_uploaded_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def list_saved_datasets():
    """
    List all saved datasets from the database
    
    Returns:
        datasets: List of dataset info dicts
    """
    ensure_data_dir()
    db_path = init_database()
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, name, original_filename, report_type, uploaded_at, record_count, data_path, pickle_path, description
    FROM reports
    ORDER BY uploaded_at DESC
    ''')
    
    datasets = []
    for row in cursor.fetchall():
        dataset = dict(row)  # Convert Row to dict
        datasets.append(dataset)
    
    conn.close()
    
    return datasets

def get_dataset_by_id(report_id):
    """
    Get dataset info by ID
    
    Args:
        report_id: ID of the report
        
    Returns:
        dataset_info: Dict with dataset info or None if not found
    """
    db_path = init_database()
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, name, original_filename, report_type, uploaded_at, record_count, data_path, pickle_path, description
    FROM reports
    WHERE id = ?
    ''', (report_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    else:
        return None

def load_saved_dataset(dataset_id_or_path):
    """
    Load a saved dataset by ID or file path
    
    Args:
        dataset_id_or_path: The dataset ID or file path to load
        
    Returns:
        df: Loaded DataFrame or None if not found
        dataset_info: Dictionary with metadata about the dataset
    """
    ensure_data_dir()
    
    # Check if it's an ID (integer) or a path (string)
    dataset_info = None
    if isinstance(dataset_id_or_path, int) or (isinstance(dataset_id_or_path, str) and dataset_id_or_path.isdigit()):
        # It's an ID, get the file path from the database
        dataset_info = get_dataset_by_id(int(dataset_id_or_path))
        if not dataset_info:
            print(f"Dataset with ID {dataset_id_or_path} not found")
            return None, None
        
        # Prefer pickle file for faster loading
        file_path = dataset_info['pickle_path']
        if not os.path.exists(file_path):
            # Fall back to CSV if pickle doesn't exist
            file_path = dataset_info['data_path']
    else:
        # It's a path
        file_path = dataset_id_or_path
        if not os.path.isabs(file_path):
            file_path = os.path.join(DATA_DIR, file_path)
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None, None
    
    try:
        # Load the data
        if file_path.endswith('.pkl'):
            with open(file_path, 'rb') as f:
                df = pickle.load(f)
        else:
            df = pd.read_csv(file_path)
        
        print(f"Successfully loaded dataset with {len(df)} rows")
        return df, dataset_info
    except Exception as e:
        print(f"Error loading dataset {file_path}: {e}")
        return None, None

def delete_dataset(dataset_id):
    """
    Delete a dataset from the database and its files
    
    Args:
        dataset_id: ID of the dataset to delete
        
    Returns:
        success: Boolean indicating success
    """
    dataset_info = get_dataset_by_id(dataset_id)
    if not dataset_info:
        return False
    
    try:
        # Delete the files
        if os.path.exists(dataset_info['data_path']):
            os.remove(dataset_info['data_path'])
        
        if os.path.exists(dataset_info['pickle_path']):
            os.remove(dataset_info['pickle_path'])
        
        # Delete from database
        db_path = init_database()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM reports WHERE id = ?', (dataset_id,))
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error deleting dataset {dataset_id}: {e}")
        return False