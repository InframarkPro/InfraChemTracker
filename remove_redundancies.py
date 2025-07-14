import pandas as pd
import os
import sqlite3
import shutil
from datetime import datetime
import sys

# Add parent directory to path for importing utility modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our cleanup utilities
from utils.data_cleanup import (
    analyze_database_integrity,
    analyze_column_standardization,
    analyze_redundant_code,
    fix_database_duplicates,
    clean_orphaned_files,
    consolidate_database_files
)

def print_section(title):
    """Print a section header for better readability"""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60 + "\n")

def print_dict(data, indent=0):
    """Print a dictionary with proper indentation for nested items"""
    for key, value in data.items():
        if isinstance(value, dict):
            print(" " * indent + f"{key}:")
            print_dict(value, indent + 4)
        elif isinstance(value, list):
            print(" " * indent + f"{key}:")
            if not value:
                print(" " * (indent + 4) + "None")
            else:
                for item in value:
                    if isinstance(item, dict):
                        print_dict(item, indent + 4)
                    else:
                        print(" " * (indent + 4) + f"- {item}")
        else:
            print(" " * indent + f"{key}: {value}")

def main():
    """Main function to analyze and clean up redundancies"""
    print_section("DATA CLEANUP AND REDUNDANCY ANALYSIS")
    print("This script will analyze and clean up redundancies in the codebase and databases.")
    print("It will perform the following operations:")
    print("1. Analyze database integrity")
    print("2. Check for column standardization issues")
    print("3. Identify redundant code patterns")
    print("4. Remove duplicate database entries")
    print("5. Clean up orphaned data files")
    print("6. Consolidate database files")
    print("\nPress Enter to begin analysis or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return
    
    # STEP 1: Analyze database integrity
    print_section("Database Integrity Analysis")
    try:
        db_analysis = analyze_database_integrity()
        print_dict(db_analysis)
    except Exception as e:
        print(f"Error during database analysis: {str(e)}")
    
    # STEP 2: Analyze column standardization
    print_section("Column Standardization Analysis")
    try:
        col_analysis = analyze_column_standardization()
        print_dict(col_analysis)
    except Exception as e:
        print(f"Error during column analysis: {str(e)}")
    
    # STEP 3: Analyze redundant code
    print_section("Redundant Code Analysis")
    try:
        code_analysis = analyze_redundant_code()
        print_dict(code_analysis)
    except Exception as e:
        print(f"Error during code analysis: {str(e)}")
    
    # Ask for confirmation before making changes
    print_section("Ready to Clean Up")
    print("The above analysis has identified issues that can be fixed automatically.")
    print("Would you like to proceed with the cleanup? (yes/no): ")
    
    try:
        response = input().strip().lower()
        if response != "yes":
            print("Cleanup cancelled by user.")
            return
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return
    
    # STEP 4: Fix database duplicates
    print_section("Removing Duplicate Database Entries")
    try:
        # Backup database first
        if os.path.exists("saved_data/reports_database.db"):
            backup_path = f"saved_data/reports_database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2("saved_data/reports_database.db", backup_path)
            print(f"Database backed up to {backup_path}")
        
        # Fix duplicates
        dup_results = fix_database_duplicates()
        print_dict(dup_results)
    except Exception as e:
        print(f"Error removing duplicates: {str(e)}")
    
    # STEP 5: Clean orphaned files
    print_section("Cleaning Orphaned Files")
    try:
        orphan_results = clean_orphaned_files()
        print_dict(orphan_results)
    except Exception as e:
        print(f"Error cleaning orphaned files: {str(e)}")
    
    # STEP 6: Consolidate database files
    print_section("Consolidating Database Files")
    try:
        if os.path.exists("saved_data/reports.db"):
            # Backup old database first
            backup_path = f"saved_data/reports_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2("saved_data/reports.db", backup_path)
            print(f"Old database backed up to {backup_path}")
            
            # Consolidate databases
            consolidate_results = consolidate_database_files()
            print_dict(consolidate_results)
            
            if consolidate_results["success"]:
                # Rename old database to prevent future use
                archive_path = f"saved_data/reports_archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                os.rename("saved_data/reports.db", archive_path)
                print(f"Old database archived as {archive_path}")
        else:
            print("No secondary database found (reports.db). Skipping consolidation.")
    except Exception as e:
        print(f"Error consolidating databases: {str(e)}")
    
    print_section("Cleanup Complete")
    print("Data cleanup operations completed.")
    print("Please restart the application to ensure all changes take effect.")

if __name__ == "__main__":
    main()