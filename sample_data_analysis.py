import pandas as pd
import sys
import os

def analyze_sample_data():
    print("Reading sample data from Chemical PO Line Detail file...")
    
    try:
        # Read the excel file
        file_path = 'attached_assets/Chemical - PO Line Detail_18032025_1848.xlsx'
        df = pd.read_excel(file_path)
        
        # Check if Item Description (column F) exists
        if 'Item Description' not in df.columns:
            print("Error: 'Item Description' column not found. Column list:", df.columns)
            return
        
        # Get the State column if it exists
        state_col = 'Purchase Requisition: Delivery Address: State' if 'Purchase Requisition: Delivery Address: State' in df.columns else None
        
        # Display some sample rows with Item Description and State
        print("\n===== SAMPLE ENTRIES =====")
        
        # Take a random sample of 20 entries
        sample_df = df.sample(min(20, len(df)))
        
        # Display with index for easy reference
        for idx, row in sample_df.iterrows():
            item_desc = row['Item Description'] if not pd.isna(row['Item Description']) else "N/A"
            state = row[state_col] if state_col and not pd.isna(row[state_col]) else "N/A"
            supplier = row['Purchase Order: Supplier'] if 'Purchase Order: Supplier' in df.columns and not pd.isna(row['Purchase Order: Supplier']) else "N/A"
            
            print(f"\nEntry #{idx}")
            print(f"Item Description: {item_desc}")
            print(f"State: {state}")
            print(f"Supplier: {supplier}")
            
        # Show the top 5 most frequent values in Item Description
        print("\n===== MOST COMMON ITEM DESCRIPTIONS =====")
        top_descriptions = df['Item Description'].value_counts().head(5)
        print(top_descriptions)
        
        # Count how many item descriptions contain region keywords
        if 'Item Description' in df.columns:
            region_indicators = [
                "South", "North", "Central", "East", "West", 
                "Northeast", "Northwest", "Southeast", "Southwest"
            ]
            
            print("\n===== REGION KEYWORDS IN ITEM DESCRIPTIONS =====")
            for region in region_indicators:
                count = df['Item Description'].astype(str).str.contains(region, case=False).sum()
                print(f"'{region}' appears in {count} item descriptions")
        
        # Show distribution of states
        if state_col:
            print("\n===== STATE DISTRIBUTION =====")
            state_counts = df[state_col].value_counts()
            print(state_counts)
        
    except Exception as e:
        print(f"Error analyzing data: {e}")

if __name__ == "__main__":
    analyze_sample_data()