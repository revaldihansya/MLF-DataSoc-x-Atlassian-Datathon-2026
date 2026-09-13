import pandas as pd
import numpy as np

def prepare_data():
    print("Loading datasets...")
    tickets = pd.read_csv('customer_support_tickets.csv')
    customers = pd.read_csv('customers.csv')
    usage = pd.read_csv('product_usage.csv')

    print("Cleaning and standardizing column headers...")
    # Strip spaces, convert to lowercase, and replace internal spaces with underscores
    tickets.columns = tickets.columns.str.strip().str.lower().str.replace(' ', '_')
    customers.columns = customers.columns.str.strip().str.lower().str.replace(' ', '_')
    usage.columns = usage.columns.str.strip().str.lower().str.replace(' ', '_')

    # Now the columns will actually be 'customer_email', 'first_response_time', etc.
    merge_keys = ['customer_email', 'customer_name', 'customer_age', 'customer_gender']

    # Debugging step: print the actual columns so you can verify the names
    print(f"Cleaned Tickets columns: {tickets.columns.tolist()}")
    print(f"Cleaned Customers columns: {customers.columns.tolist()}")

    # If the column is named something like 'email' instead of 'customer_email' in the CSV, 
    # you will need to update the list below to match the printed output above.
    merge_keys = ['customer_email', 'customer_name', 'customer_age', 'customer_gender']

    print("Step 1: Merging Customers & Tickets...")
    master_df = pd.merge(tickets, customers, on=merge_keys, how='left')

    print("Step 2: Parsing Dates & Feature Engineering...")
    # Using dayfirst=True and format='mixed' to handle international date formats
    master_df['first_response_time'] = pd.to_datetime(master_df['first_response_time'], dayfirst=True, format='mixed')
    master_df['time_to_resolution'] = pd.to_datetime(master_df['time_to_resolution'], dayfirst=True, format='mixed')
    
    # Let's also apply this to the other date columns just to be safe!
    master_df['date_of_purchase'] = pd.to_datetime(master_df['date_of_purchase'], dayfirst=True, format='mixed')
    master_df['account_created_date'] = pd.to_datetime(master_df['account_created_date'], dayfirst=True, format='mixed')
    
    master_df['resolution_time_hours'] = (master_df['time_to_resolution'] - master_df['first_response_time']).dt.total_seconds() / 3600

    print("Step 3: Aggregating Product Usage...")
    usage_agg = usage.groupby('customer_id').agg(
        total_active_days=('active_days', 'sum'),
        total_sessions=('sessions', 'sum'),
        total_product_actions=('product_actions', 'sum'),
        avg_collaborators=('collaborators', 'mean'),
        avg_integrations=('integrations_used', 'mean')
    ).reset_index()

    print("Step 4: Final Merge...")
    final_df = pd.merge(master_df, usage_agg, on='customer_id', how='left')

    print("Exporting clean dataset...")
    final_df.to_csv('clean_atlassian_master.csv', index=False)
    print("Done! Saved as 'clean_atlassian_master.csv'.")

if __name__ == "__main__":
    prepare_data()