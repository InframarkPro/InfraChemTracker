"""
Script to delete all datasets and clear session state cache.
Run this script to clean all data before testing.
"""

import os
import json
import sqlite3
import shutil

def main():
    # Set title
    print("Clearing all data from the application...")
    
    # Define paths
    saved_data_dir = "saved_data"
    
    # Check if the saved_data directory exists
    if os.path.exists(saved_data_dir):
        # List all files in saved_data directory
        files = os.listdir(saved_data_dir)
        deleted_count = len(files)
        
        # Remove all files in the directory
        for file in files:
            file_path = os.path.join(saved_data_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"Deleted: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        
        print(f"Successfully deleted {deleted_count} files from saved_data directory.")
    else:
        print("No saved_data directory found.")
    
    # Check for SQLite database
    db_path = "saved_data/reports.db"
    if os.path.exists(db_path):
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Delete all records from reports table
            cursor.execute("DELETE FROM reports")
            deleted_rows = cursor.rowcount
            conn.commit()
            
            # Close connection
            conn.close()
            
            print(f"Successfully deleted {deleted_rows} reports from SQLite database.")
        except Exception as e:
            print(f"Error clearing SQLite database: {e}")
    else:
        print("No SQLite database found.")
        
    print("All data has been cleared.")

if __name__ == "__main__":
    main()