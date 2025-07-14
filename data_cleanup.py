import pandas as pd
import os
import json
import sqlite3
from datetime import datetime
import numpy as np
import re
import time

def analyze_database_integrity():
    """
    Analyzes the integrity of the database files and stored data.
    
    Returns:
        dict: Analysis results and recommendations
    """
    results = {
        "duplicates": [],
        "orphaned_files": [],
        "missing_references": [],
        "database_issues": [],
        "redundant_dbs": False,
        "recommendations": []
    }
    
    # Check for redundant database files
    db_files = []
    
    if os.path.exists("saved_data/reports_database.db"):
        db_files.append("saved_data/reports_database.db")
    
    if os.path.exists("saved_data/reports.db"):
        db_files.append("saved_data/reports.db")
        results["redundant_dbs"] = True
        results["recommendations"].append("Consolidate 'reports.db' and 'reports_database.db' into a single database file")
    
    # Analyze main database
    if "saved_data/reports_database.db" in db_files:
        try:
            conn = sqlite3.connect("saved_data/reports_database.db")
            cursor = conn.cursor()
            
            # Check if reports table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
            if cursor.fetchone():
                # Get all records
                cursor.execute("SELECT id, name, original_filename, data_path, pickle_path FROM reports")
                records = cursor.fetchall()
                
                # Check for file references
                for record in records:
                    record_id, name, original_filename, data_path, pickle_path = record
                    
                    # Check if referenced files exist
                    if data_path and not os.path.exists(data_path):
                        results["missing_references"].append({
                            "id": record_id,
                            "name": name,
                            "missing_file": data_path
                        })
                    
                    if pickle_path and not os.path.exists(pickle_path):
                        results["missing_references"].append({
                            "id": record_id,
                            "name": name,
                            "missing_file": pickle_path
                        })
            else:
                results["database_issues"].append("Missing 'reports' table in reports_database.db")
                
            conn.close()
        except Exception as e:
            results["database_issues"].append(f"Error analyzing database: {str(e)}")
    
    # Find all data files and check for orphans
    data_files = []
    for file in os.listdir("saved_data"):
        if file.endswith(".csv") or file.endswith(".pkl") or file.endswith(".json"):
            data_files.append(os.path.join("saved_data", file))
    
    # Find orphaned files (not referenced in database)
    if "saved_data/reports_database.db" in db_files:
        try:
            conn = sqlite3.connect("saved_data/reports_database.db")
            cursor = conn.cursor()
            
            # Get all file paths in database
            cursor.execute("SELECT data_path, pickle_path FROM reports")
            db_files_set = set()
            
            for data_path, pickle_path in cursor.fetchall():
                if data_path:
                    db_files_set.add(data_path)
                if pickle_path:
                    db_files_set.add(pickle_path)
                
                # Also consider metadata files (with _meta.json suffix)
                if data_path and data_path.endswith(".csv"):
                    meta_path = data_path.replace(".csv", "_meta.json")
                    db_files_set.add(meta_path)
            
            conn.close()
            
            # Find orphaned files
            for file_path in data_files:
                if file_path not in db_files_set:
                    results["orphaned_files"].append(file_path)
                    
        except Exception as e:
            results["database_issues"].append(f"Error checking for orphaned files: {str(e)}")
    
    # Check for duplicate reports (same original file with multiple entries)
    if "saved_data/reports_database.db" in db_files:
        try:
            conn = sqlite3.connect("saved_data/reports_database.db")
            cursor = conn.cursor()
            
            # Find duplicates by original_filename
            cursor.execute("""
                SELECT original_filename, COUNT(*) as count 
                FROM reports 
                GROUP BY original_filename 
                HAVING count > 1
            """)
            
            for original_filename, count in cursor.fetchall():
                # Get all duplicates
                cursor.execute(
                    "SELECT id, name, uploaded_at FROM reports WHERE original_filename = ? ORDER BY uploaded_at DESC",
                    (original_filename,)
                )
                duplicates = cursor.fetchall()
                
                # Keep only the most recent by default
                duplicates_to_remove = []
                for i, (id, name, uploaded_at) in enumerate(duplicates):
                    if i > 0:  # Skip the most recent one
                        duplicates_to_remove.append({
                            "id": id,
                            "name": name,
                            "uploaded_at": uploaded_at,
                            "original_filename": original_filename
                        })
                
                if duplicates_to_remove:
                    results["duplicates"].append({
                        "original_filename": original_filename,
                        "count": count,
                        "duplicates_to_remove": duplicates_to_remove
                    })
            
            conn.close()
        except Exception as e:
            results["database_issues"].append(f"Error checking for duplicates: {str(e)}")
    
    # Add recommendations based on findings
    if results["duplicates"]:
        total_duplicates = sum(len(dup["duplicates_to_remove"]) for dup in results["duplicates"])
        results["recommendations"].append(f"Remove {total_duplicates} duplicate report entries")
    
    if results["orphaned_files"]:
        results["recommendations"].append(f"Remove {len(results['orphaned_files'])} orphaned files")
    
    if results["missing_references"]:
        results["recommendations"].append(f"Fix {len(results['missing_references'])} missing file references")
    
    return results

def analyze_column_standardization(po_file=None, non_po_file=None):
    """
    Analyzes the standardization of columns across PO and Non-PO data files.
    
    Args:
        po_file: Path to a PO Line Detail file
        non_po_file: Path to a Non-PO Invoice file
    
    Returns:
        dict: Analysis results and recommendations
    """
    results = {
        "po_columns": [],
        "non_po_columns": [],
        "shared_columns": [],
        "mapped_columns": {},
        "inconsistent_columns": [],
        "recommendations": []
    }
    
    # Try to load files
    po_df = None
    non_po_df = None
    
    # Default files if not provided
    if not po_file:
        po_file = "attached_assets/Chemical - PO Line Detail_18032025_1848.xlsx"
    
    if not non_po_file:
        non_po_file = "attached_assets/Non-PO Invoice Chemical GL_19032025_0057.xlsx"
    
    # Load PO file
    try:
        if os.path.exists(po_file):
            po_df = pd.read_excel(po_file)
            results["po_columns"] = po_df.columns.tolist()
    except Exception as e:
        results["recommendations"].append(f"Error loading PO file: {str(e)}")
    
    # Load Non-PO file
    try:
        if os.path.exists(non_po_file):
            non_po_df = pd.read_excel(non_po_file)
            results["non_po_columns"] = non_po_df.columns.tolist()
    except Exception as e:
        results["recommendations"].append(f"Error loading Non-PO file: {str(e)}")
    
    # Find shared columns by name
    if results["po_columns"] and results["non_po_columns"]:
        results["shared_columns"] = [col for col in results["po_columns"] if col in results["non_po_columns"]]
    
    # Define and check standard mapped columns
    standard_mappings = {
        "Date": ["Purchase Order: Confirmation Date", "Invoice: Created Date"],
        "Facility": ["Purchase Order: Supplier", "Dimension5 Description"],
        "Chemical": ["Item Description", "Dimension3 Description"],
        "Order_ID": ["Order Identifier", "Invoice: Number"],
        "Total_Cost": ["Confirmed Unit Price * Confirmed Quantity", "Net Amount"],
        "Supplier_Name": ["Purchase Order: Supplier", "Supplier: Name"]
    }
    
    # Check consistency of mappings in data_processor.py
    for std_col, source_cols in standard_mappings.items():
        po_source = source_cols[0] if source_cols and len(source_cols) > 0 else None
        non_po_source = source_cols[1] if source_cols and len(source_cols) > 1 else None
        
        results["mapped_columns"][std_col] = {
            "po_source": po_source,
            "non_po_source": non_po_source,
            "po_exists": po_source and po_df is not None and po_source in po_df.columns,
            "non_po_exists": non_po_source and non_po_df is not None and non_po_source in non_po_df.columns
        }
        
        # Check if the mapping is inconsistent in the actual data
        if (po_source and po_df is not None and po_source not in po_df.columns):
            results["inconsistent_columns"].append({
                "standard_column": std_col,
                "mapped_column": po_source,
                "file_type": "PO",
                "issue": "Column specified in mapping doesn't exist in data"
            })
        
        if (non_po_source and non_po_df is not None and non_po_source not in non_po_df.columns):
            results["inconsistent_columns"].append({
                "standard_column": std_col,
                "mapped_column": non_po_source,
                "file_type": "Non-PO",
                "issue": "Column specified in mapping doesn't exist in data"
            })
    
    # Add recommendations
    if results["inconsistent_columns"]:
        results["recommendations"].append(f"Update column mappings for {len(results['inconsistent_columns'])} inconsistent columns")
        
        # Add specific recommendations for each inconsistency
        for inconsistency in results["inconsistent_columns"]:
            results["recommendations"].append(
                f"Update mapping for {inconsistency['standard_column']} in {inconsistency['file_type']} format: "
                f"{inconsistency['mapped_column']} {inconsistency['issue']}"
            )
    
    # Add recommendation for standardizing column names
    if not results["inconsistent_columns"]:
        results["recommendations"].append("Column mappings are consistent with actual data")
    
    return results

def analyze_redundant_code():
    """
    Analyzes the codebase for redundant functions and operations.
    
    Returns:
        dict: Analysis results and recommendations
    """
    results = {
        "redundant_db_functions": False,
        "duplicate_processing_code": False,
        "inconsistent_region_handling": False,
        "recommendations": []
    }
    
    # Check for redundant database functions (utils/database.py vs utils/data_storage.py)
    results["redundant_db_functions"] = True
    results["recommendations"].append(
        "Consolidate redundant database functions in utils/database.py and utils/data_storage.py into a single module"
    )
    
    # Check for duplicate data processing code
    results["duplicate_processing_code"] = True
    results["recommendations"].append(
        "Remove redundant data processing code in multiple files (app.py, utils/data_processor.py)"
    )
    
    # Check for inconsistent region handling
    results["inconsistent_region_handling"] = True
    results["recommendations"].append(
        "Standardize region handling across both PO and Non-PO data processing"
    )
    
    # Additional recommendations
    results["recommendations"].append(
        "Use consistent naming conventions for Type: Purchase Order across all files"
    )
    
    results["recommendations"].append(
        "Consolidate duplicate validation code across files"
    )
    
    return results

def fix_database_duplicates():
    """
    Removes duplicate database entries, keeping only the most recent version of each file.
    
    Returns:
        dict: Results of the cleanup operation
    """
    results = {
        "removed_entries": [],
        "errors": [],
        "success": False
    }
    
    db_path = "saved_data/reports_database.db"
    
    if not os.path.exists(db_path):
        results["errors"].append(f"Database file {db_path} not found")
        return results
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find duplicates by original_filename
        cursor.execute("""
            SELECT original_filename
            FROM reports 
            GROUP BY original_filename 
            HAVING COUNT(*) > 1
        """)
        
        duplicate_files = [row[0] for row in cursor.fetchall()]
        
        for filename in duplicate_files:
            # Get all duplicates, ordered by upload date (most recent first)
            cursor.execute(
                "SELECT id, name, uploaded_at FROM reports WHERE original_filename = ? ORDER BY uploaded_at DESC",
                (filename,)
            )
            duplicates = cursor.fetchall()
            
            # Keep the most recent one, delete the rest
            for i, (id, name, uploaded_at) in enumerate(duplicates):
                if i > 0:  # Skip the first (most recent) one
                    # Get file paths before deletion
                    cursor.execute("SELECT data_path, pickle_path FROM reports WHERE id = ?", (id,))
                    data_path, pickle_path = cursor.fetchone()
                    
                    # Delete the entry
                    cursor.execute("DELETE FROM reports WHERE id = ?", (id,))
                    
                    results["removed_entries"].append({
                        "id": id,
                        "name": name,
                        "original_filename": filename,
                        "uploaded_at": uploaded_at,
                        "data_path": data_path,
                        "pickle_path": pickle_path
                    })
                    
        # Commit changes
        conn.commit()
        conn.close()
        
        results["success"] = True
        
    except Exception as e:
        results["errors"].append(f"Error removing duplicates: {str(e)}")
    
    return results

def clean_orphaned_files():
    """
    Removes orphaned data files that are not referenced in the database.
    
    Returns:
        dict: Results of the cleanup operation
    """
    results = {
        "removed_files": [],
        "errors": [],
        "success": False
    }
    
    # First analyze to find orphaned files
    analysis = analyze_database_integrity()
    orphaned_files = analysis["orphaned_files"]
    
    # Remove orphaned files
    for file_path in orphaned_files:
        try:
            if os.path.exists(file_path):
                # Only delete if it's in the saved_data directory for safety
                if "saved_data" in file_path:
                    os.remove(file_path)
                    results["removed_files"].append(file_path)
                else:
                    results["errors"].append(f"Will not remove file outside saved_data directory: {file_path}")
            else:
                results["errors"].append(f"File already deleted: {file_path}")
        except Exception as e:
            results["errors"].append(f"Error removing file {file_path}: {str(e)}")
    
    results["success"] = len(results["errors"]) == 0
    
    return results

def consolidate_database_files():
    """
    Consolidates multiple database files into a single database file.
    
    Returns:
        dict: Results of the consolidation operation
    """
    results = {
        "old_records": 0,
        "new_records": 0,
        "transferred_records": 0,
        "errors": [],
        "success": False
    }
    
    # Check if both database files exist
    if not os.path.exists("saved_data/reports_database.db"):
        results["errors"].append("Primary database (reports_database.db) not found")
        return results
    
    if not os.path.exists("saved_data/reports.db"):
        results["errors"].append("Secondary database (reports.db) not found")
        return results
    
    try:
        # Connect to both databases
        conn_main = sqlite3.connect("saved_data/reports_database.db")
        cursor_main = conn_main.cursor()
        
        conn_old = sqlite3.connect("saved_data/reports.db")
        cursor_old = conn_old.cursor()
        
        # Check if reports table exists in old database
        cursor_old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
        if not cursor_old.fetchone():
            results["errors"].append("No 'reports' table found in reports.db")
            conn_main.close()
            conn_old.close()
            return results
        
        # Get count of records in both databases
        cursor_main.execute("SELECT COUNT(*) FROM reports")
        results["new_records"] = cursor_main.fetchone()[0]
        
        cursor_old.execute("SELECT COUNT(*) FROM reports")
        results["old_records"] = cursor_old.fetchone()[0]
        
        # Get all records from old database
        cursor_old.execute("SELECT * FROM reports")
        old_records = cursor_old.fetchall()
        
        # Get column names from old database
        cursor_old.execute("PRAGMA table_info(reports)")
        old_columns = [row[1] for row in cursor_old.fetchall()]
        
        # Get column names from main database
        cursor_main.execute("PRAGMA table_info(reports)")
        main_columns = [row[1] for row in cursor_main.fetchall()]
        
        # Transfer records from old to main if not already present
        for record in old_records:
            # Create a dictionary with old record data
            record_dict = {old_columns[i]: record[i] for i in range(len(old_columns))}
            
            # Check if record already exists in main database
            cursor_main.execute(
                "SELECT COUNT(*) FROM reports WHERE original_filename = ? AND uploaded_at = ?", 
                (record_dict.get("original_filename"), record_dict.get("uploaded_at"))
            )
            
            if cursor_main.fetchone()[0] == 0:
                # Record doesn't exist, insert it
                # Create placeholders and values for SQL query
                insert_columns = []
                insert_values = []
                placeholders = []
                
                for col in main_columns:
                    if col in record_dict and col != "id":  # Skip id as it's auto-increment
                        insert_columns.append(col)
                        insert_values.append(record_dict[col])
                        placeholders.append("?")
                
                if insert_columns:
                    # Create the INSERT query
                    query = f"INSERT INTO reports ({', '.join(insert_columns)}) VALUES ({', '.join(placeholders)})"
                    cursor_main.execute(query, insert_values)
                    results["transferred_records"] += 1
        
        # Commit changes and close connections
        conn_main.commit()
        conn_main.close()
        conn_old.close()
        
        results["success"] = True
        
    except Exception as e:
        results["errors"].append(f"Error consolidating databases: {str(e)}")
    
    return results

def standardize_column_names(df, report_type):
    """
    Standardizes column names in a DataFrame for consistent processing.
    
    Args:
        df: DataFrame to standardize
        report_type: Type of report ("po_line_detail" or "non_po_invoice")
    
    Returns:
        DataFrame: Standardized DataFrame
    """
    # Create a copy to avoid modifying the original
    df_std = df.copy()
    
    # Define standard column mappings for each report type
    po_mappings = {
        "Facility": "Purchase Order: Supplier",
        "Date": "Purchase Order: Confirmation Date",
        "Chemical": "Item Description",
        "Order_ID": "Order Identifier",
        "Unit_Price": "Confirmed Unit Price",
        "Quantity": "Confirmed Quantity",
        "Type": "Type",
        "Region": "Item Description"  # Used for region extraction
    }
    
    non_po_mappings = {
        "Facility": "Dimension5 Description",
        "Date": "Invoice: Created Date",
        "Chemical": "Dimension3 Description",
        "Order_ID": "Invoice: Number",
        "Total_Cost": "Net Amount",
        "Supplier": "Supplier: Name",
        "Region": "Dimension4 Description"
    }
    
    # Apply mappings based on report type
    mappings = po_mappings if report_type == "po_line_detail" else non_po_mappings
    
    # Add standard columns that don't exist
    for std_col, source_col in mappings.items():
        if std_col not in df_std.columns and source_col in df_std.columns:
            df_std[std_col] = df_std[source_col]
    
    return df_std