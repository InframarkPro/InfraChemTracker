
import sqlite3
import json
from datetime import datetime
import os
import pandas as pd
import pickle

# Use data_storage functions for database operations
from utils.data_storage import (
    init_database, list_saved_datasets, load_saved_dataset, 
    get_dataset_by_id, save_uploaded_data, delete_dataset
)

def init_db():
    """Initialize the database with necessary tables - using data_storage implementation"""
    return init_database()

def save_report_metadata(filename, original_filename, report_type, metadata):
    """
    Save report metadata to database - this is a compatibility function
    that calls the data_storage implementation
    
    Note: This function doesn't actually save data, only metadata.
    To save data, use save_uploaded_data from data_storage instead.
    """
    # This is a placeholder for compatibility with existing code
    print(f"Warning: save_report_metadata called, but doesn't save actual data. "
          f"Use save_uploaded_data from data_storage instead.")
    
    # Return the metadata as if we'd saved it
    return {
        "filename": filename,
        "original_filename": original_filename,
        "report_type": report_type,
        "upload_date": datetime.now().isoformat(),
        "metadata": metadata
    }

def get_all_reports():
    """
    Retrieve all reports from database - using data_storage implementation
    
    Returns:
        List of report tuples in the format expected by the original function
    """
    # Get all datasets from data_storage
    datasets = list_saved_datasets()
    
    # Convert to the format expected by the original function
    reports = []
    for dataset in datasets:
        # Create a tuple format compatible with the original function
        # id, filename, original_filename, report_type, upload_date, metadata
        report = (
            dataset.get('id'),
            dataset.get('data_path', '').split('/')[-1],  # Extract filename from path
            dataset.get('original_filename', ''),
            dataset.get('report_type', 'Unknown'),
            dataset.get('uploaded_at', ''),
            json.dumps({"record_count": dataset.get('record_count', 0)})
        )
        reports.append(report)
    
    return reports

def get_report_by_id(report_id):
    """
    Retrieve a specific report by ID - using data_storage implementation
    
    Returns:
        Report tuple in the format expected by the original function
    """
    # Get the dataset info from data_storage
    dataset_info = get_dataset_by_id(report_id)
    
    if not dataset_info:
        return None
    
    # Convert to the format expected by the original function
    # id, filename, original_filename, report_type, upload_date, metadata
    report = (
        dataset_info.get('id'),
        dataset_info.get('data_path', '').split('/')[-1],  # Extract filename from path
        dataset_info.get('original_filename', ''),
        dataset_info.get('report_type', 'Unknown'),
        dataset_info.get('uploaded_at', ''),
        json.dumps({"record_count": dataset_info.get('record_count', 0)})
    )
    
    return report

def load_report_data(report_id):
    """
    Load report data by ID - using data_storage implementation
    
    Returns:
        DataFrame with the report data
    """
    # Load the dataset using data_storage
    df, _ = load_saved_dataset(report_id)
    return df
