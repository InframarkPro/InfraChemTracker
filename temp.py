        # Calculate the % difference between distributions
        distribution_difference = non_po_percentage - 5 if non_po_percentage > 5 else 0
        po_percentage = 100 - non_po_percentage
        
        if distribution_difference > 0:
            # Calculate number of orders to convert
            target_gap = non_po_count - int(total_orders * 0.05)  # Calculate how many orders need to be converted
            
            # Show % difference from target
            st.write(f"**Gap: {distribution_difference:.1f}% above target**")
            st.write(f"Need to convert {target_gap} orders from Non-PO to PO to reach target")
        else:
            st.write("**Target Met!** Non-PO orders are below 5% threshold")
