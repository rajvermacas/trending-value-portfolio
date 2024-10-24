import pandas as pd
import os

# Get the output directory from environment variable
output_dir = r'C:\Users\mrina\Documents\Projects\trending-value-portfolio\output'

print(f"\nSearching for files in: {output_dir}")

# Get all files starting with 'trending_value_portfolio' in the output directory
files = [f for f in os.listdir(output_dir) if f.startswith('trending_value_portfolio_ticker_tape')]

# Sort files in descending order
files.sort(reverse=True)

# Get the two most recent files
current_file = os.path.join(output_dir, files[0])
reference_file = os.path.join(output_dir, files[1])

print("\nComparing files:")
print(f"Current file  : {files[0]}")
print(f"Reference file: {files[1]}")

current_df = pd.read_csv(current_file)
reference_df = pd.read_csv(reference_file)

print(f"\nCurrent file rows  : {len(current_df)}")
print(f"Reference file rows: {len(reference_df)}")

# Assuming the stock names are in a column called 'Name' or 'Symbol'
column_name = 'Name'  # or 'Symbol'

print(f"\nUsing column: {column_name}")

# Get the set of stock names from each DataFrame
current_stocks = set(current_df[column_name])
reference_stocks = set(reference_df[column_name])

print(f"Total stocks in current file  : {len(current_stocks)}")
print(f"Total stocks in reference file: {len(reference_stocks)}")

# Find new stocks (in current but not in reference)
new_stocks = current_stocks - reference_stocks

# Find stocks that were removed (in reference but not in current)
delisted_stocks = reference_stocks - current_stocks

print("\n" + "="*50)
print("COMPARISON RESULTS")
print("="*50)

print("\nNew stocks (present in current file but not in reference):")
if new_stocks:
    # Get indices for new stocks
    new_stocks_info = []
    for stock in sorted(new_stocks):
        index = current_df[current_df[column_name] == stock].index[0]
        new_stocks_info.append((index, stock))
    
    # Sort by index
    new_stocks_info.sort()
    
    # Print with index information
    for index, stock in new_stocks_info:
        print(f"- {stock} (at row {index + 2})") # +2 to account for header row and index
else:
    print("None")

print("\nDelisted stocks (present in reference but not in current):")
if delisted_stocks:
    for stock in sorted(delisted_stocks):
        print(f"- {stock}")
else:
    print("None")

print("\nSummary:")
print(f"Total new stocks     : {len(new_stocks)}")
print(f"Total delisted stocks: {len(delisted_stocks)}")
print("="*50)
