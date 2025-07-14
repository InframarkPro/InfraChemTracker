import streamlit as st
import pandas as pd

def main():
    st.title("Debug PO Count Issue")
    
    if 'po_data' in st.session_state and st.session_state.po_data is not None:
        df = st.session_state.po_data
        
        st.write("### DataFrame Basic Info")
        st.write(f"Shape: {df.shape}")
        st.write(f"Columns: {df.columns.tolist()}")
        
        st.write("### Type Column Analysis")
        if 'Type' in df.columns:
            st.write("Type column values:")
            type_counts = df['Type'].value_counts().to_dict()
            st.write(type_counts)
            
            st.write(f"Number of rows where Type is 'P': {len(df[df['Type'] == 'P'])}")
            
            # Show sample rows with each type value
            for type_val in type_counts.keys():
                st.write(f"\nSample row with Type = '{type_val}':")
                st.dataframe(df[df['Type'] == type_val].head(1))
        else:
            st.write("Type column NOT FOUND in the dataframe")
        
        st.write("### Order_ID Analysis")
        if 'Order_ID' in df.columns:
            unique_order_ids = df['Order_ID'].unique()
            st.write(f"Number of unique Order_ID values: {len(unique_order_ids)}")
            st.write(f"Sample unique Order_IDs: {unique_order_ids[:5]}")
        else:
            st.write("Order_ID column NOT FOUND in the dataframe")
        
        # Try alternative ways to count POs
        st.write("### Alternative PO Counting Methods")
        if 'Type' in df.columns:
            st.write(f"Count using Type == 'P': {len(df[df['Type'] == 'P'])}")
            st.write(f"Count using Type.str.upper() == 'P': {len(df[df['Type'].str.upper() == 'P'])}")
            st.write(f"Count using Type.str.contains('P'): {len(df[df['Type'].str.contains('P', na=False)])}")
        
        if 'Order_ID' in df.columns:
            st.write(f"Count using Order_ID unique: {len(df['Order_ID'].unique())}")
        
        # Show raw sample data
        st.write("### Raw Data Sample (First 10 rows)")
        st.dataframe(df.head(10))
    else:
        st.warning("No data loaded. Please upload data from the main page first.")

if __name__ == "__main__":
    main()