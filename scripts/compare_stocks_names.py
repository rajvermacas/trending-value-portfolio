"""
Compare stock names between two CSV files.

This script compares the stock names in a current CSV file against a reference CSV file,
identifying new stocks and delisted stocks.

Usage:
    python compare_stocks_names.py [--current CURRENT_FILE] [--reference REFERENCE_FILE]

Arguments:
    --current CURRENT_FILE    : Path to the current CSV file (optional)
    --reference REFERENCE_FILE: Path to the reference CSV file (optional)

If no arguments are provided, the script will automatically select the two most recent
'trending_value_portfolio_ticker_tape' files from the output directory.

Output:
    - Displays comparison results, including new stocks and delisted stocks
    - Prints summary statistics of the comparison
"""


import pandas as pd
import os
import argparse

def get_default_files():
    # Get the output directory from environment variable
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    
    print(f"\nSearching for files in: {output_dir}")
    
    # Get all files starting with 'trending_value_portfolio' in the output directory
    files = [f for f in os.listdir(output_dir) if f.startswith('trending_value_portfolio_ticker_tape')]
    
    # Sort files in descending order
    files.sort(reverse=True)
    
    # Get the two most recent files
    current_file = os.path.join(output_dir, files[0])
    reference_file = os.path.join(output_dir, files[1])
    
    return current_file, reference_file, files[0], files[1]

def main():
    parser = argparse.ArgumentParser(description='Compare stock names between two CSV files.')
    parser.add_argument('--current', help='Path to the current CSV file')
    parser.add_argument('--reference', help='Path to the reference CSV file')
    
    args = parser.parse_args()
    
    if args.current and args.reference:
        current_file = args.current
        reference_file = args.reference
        current_name = os.path.basename(current_file)
        reference_name = os.path.basename(reference_file)
    else:
        current_file, reference_file, current_name, reference_name = get_default_files()
    
    print("\nComparing files:")
    print(f"Current file  : {current_name}")
    print(f"Reference file: {reference_name}")
    
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

if __name__ == "__main__":
    main()
