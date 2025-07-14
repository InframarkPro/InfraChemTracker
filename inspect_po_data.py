import pandas as pd
import sqlite3
import os
import json

def inspect_database():
    """Examine the reports database structure"""
    conn = sqlite3.connect('saved_data/reports_database.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Look at reports table structure
    print("\nReports table structure:")
    cursor.execute("PRAGMA table_info(reports)")
    for col in cursor.fetchall():
        print(f"- {col[1]} ({col[2]})")
    
    # List report types
    print("\nReport types in database:")
    cursor.execute("SELECT DISTINCT report_type FROM reports")
    for report_type in cursor.fetchall():
        print(f"- {report_type[0]}")
    
    # List PO Line Detail reports
    print("\nPO Line Detail reports:")
    cursor.execute("SELECT id, name, original_filename, uploaded_at FROM reports WHERE report_type = 'PO Line Detail' ORDER BY uploaded_at")
    for report in cursor.fetchall():
        print(f"- Report ID {report[0]}: {report[1]} ({report[2]}) uploaded at {report[3]}")
    
    conn.close()

def examine_po_structure():
    """Look at the structure of a PO Line Detail file"""
    # Find the most recent PO Line Detail file
    po_files = [f for f in os.listdir('saved_data') if f.endswith('.csv') and 'PO_Line_Detail' in f]
    if not po_files:
        print("No PO Line Detail files found")
        return
    
    # Sort by date (assuming filename contains the date)
    po_files.sort(reverse=True)
    latest_file = po_files[0]
    print(f"\nExamining most recent PO file: {latest_file}")
    
    # Read the file
    df = pd.read_csv(f"saved_data/{latest_file}")
    
    # Show basic info
    print(f"\nFile shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nColumns in file:")
    for col in df.columns:
        print(f"- {col}")
    
    # Check for date/time columns
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    print(f"\nPotential date/time columns: {date_cols}")
    
    # Check for PO type column
    po_type_cols = [col for col in df.columns if 'type' in col.lower() or 'catalog' in col.lower() or 'free text' in col.lower()]
    print(f"\nPotential PO type columns: {po_type_cols}")
    
    # If we found a PO type column, show the distribution
    if po_type_cols:
        print(f"\nDistribution of values in '{po_type_cols[0]}':")
        value_counts = df[po_type_cols[0]].value_counts()
        for value, count in value_counts.items():
            print(f"- {value}: {count} ({count/len(df)*100:.1f}%)")
    
    # Check if metadata file exists
    meta_file = latest_file.replace('.csv', '_meta.json')
    if os.path.exists(f"saved_data/{meta_file}"):
        with open(f"saved_data/{meta_file}", 'r') as f:
            meta = json.load(f)
        print("\nMetadata:")
        print(json.dumps(meta, indent=2))

if __name__ == "__main__":
    print("Examining database structure...\n")
    inspect_database()
    
    print("\n" + "-"*50 + "\n")
    
    print("Examining PO file structure...\n")
    examine_po_structure()
