import streamlit as st
import pandas as pd
import os
import json

print("Debugging Region column values")

# Try to access session state from saved files
session_dir = os.path.join("saved_data", "sessions")
if not os.path.exists(session_dir):
    print("No session directory found")
    exit()

# Look for the most recent session file
session_files = [f for f in os.listdir(session_dir) if f.endswith(".json")]
if not session_files:
    print("No session files found")
    exit()

# Look at loaded datasets in each session file
for session_file in session_files:
    try:
        with open(os.path.join(session_dir, session_file), "r") as f:
            data = json.load(f)
            
            # Check if datasets are loaded
            loaded_data_key = data.get("loaded_datasets")
            print(f"Session file: {session_file}")
            
            if loaded_data_key:
                # Try to load the datasets
                for dataset_id in loaded_data_key:
                    dataset_path = os.path.join("saved_data", f"{dataset_id}.pkl")
                    
                    if os.path.exists(dataset_path):
                        try:
                            df = pd.read_pickle(dataset_path)
                            print(f"Dataset ID: {dataset_id}, Shape: {df.shape}")
                            
                            if "Region" in df.columns:
                                print("Sample Region values:")
                                print(df["Region"].head(10).tolist())
                                
                                # Check for emails in Region values
                                has_emails = any("@" in str(r) for r in df["Region"].dropna())
                                print(f"Region column contains emails: {has_emails}")
                                
                                # Show some sample values that have emails
                                if has_emails:
                                    email_samples = [r for r in df["Region"].dropna() if "@" in str(r)][:5]
                                    print("Sample values with emails:")
                                    for sample in email_samples:
                                        print(f"  {sample}")
                        except Exception as e:
                            print(f"Error loading dataset {dataset_id}: {e}")
                    else:
                        print(f"Dataset file not found: {dataset_path}")
            else:
                print("No loaded datasets in this session")
                
    except Exception as e:
        print(f"Error processing session file {session_file}: {e}")