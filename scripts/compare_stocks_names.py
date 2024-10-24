import pandas as pd

# Read the CSV files
current_file = r"C:\Users\mrina\Documents\Projects\trending-value-portfolio\output\trending_value_portfolio_ticker_tape_1846_241024.csv"
reference_file = r"C:\Users\mrina\Documents\Projects\trending-value-portfolio\output\trending_value_portfolio_ticker_tape_1871_201024.csv"

current_df = pd.read_csv(current_file)
reference_df = pd.read_csv(reference_file)

# Assuming the stock names are in a column called 'Name' or 'Symbol'
# Adjust the column name if it's different in your CSV files
column_name = 'Name'  # or 'Symbol'

# Get the set of stock names from each DataFrame
current_stocks = set(current_df[column_name])
reference_stocks = set(reference_df[column_name])

# Find new stocks (in current but not in reference)
new_stocks = current_stocks - reference_stocks

# Find stocks that were removed (in reference but not in current)
delisted_stocks = reference_stocks - current_stocks

# Print the results
print("New stocks (present in current file but not in reference):")
for stock in new_stocks:
    print(f"- {stock}")

print("\nDelisted stocks (present in reference but not in current):")
for stock in delisted_stocks:
    print(f"- {stock}")

# Print summary
print(f"\nTotal new stocks: {len(new_stocks)}")
print(f"Total delisted stocks: {len(delisted_stocks)}")
