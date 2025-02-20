import pandas as pd
import os
import pandas as pd
from stock_data import params
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Set
import builtins


# Set up input directory path
os.environ['INPUT_DIR'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'input')

def get_stock_data(filepath: str=None) -> pd.DataFrame:
    # "Name",
    # "Sub-Sector",
    # "Market Cap",
    # "PE Ratio",
    # "6M Return",
    # "PB Ratio",
    # "PS Ratio",
    # "EV/EBITDA Ratio",
    # "Price / CFO",
    # "Dividend Yield",
    # "1Y Historical EPS Growth",
    # "Earnings Per Share",
    # "1Y Return",
    # "1M Return",
    # "Net Income (Q)",
    # "1Y Historical Revenue Growth",
    # "1Y Hist Op. Cash Flow Growth",
    # "1Y Historical EBITDA Growth",
    # "PEG Ratio"

    if filepath is None:
        filepath = os.path.join(os.getenv("INPUT_DIR"), params.NIFTY_STOCKS_CSV_FILENAME)
    
    print(f"Reading data from {filepath}")
    df = pd.read_csv(filepath)

    # Convert necessary columns to numeric
    numeric_columns = [
        "Market Cap",
        "6M Return",
        "Dividend Yield",
        "1Y Historical EPS Growth",
        "Earnings Per Share",
        "PE Ratio",
        "PB Ratio",
        "PS Ratio",
        "EV/EBITDA Ratio",
        "Price / CFO",
        "1Y Historical EPS Growth",
        "Earnings Per Share",
        "1Y Return",
        "1M Return",
        "Net Income (Q)",
        "1Y Historical Revenue Growth",
        "1Y Hist Op. Cash Flow Growth",
        "1Y Historical EBITDA Growth",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    
    # Calculate PEG Ratio efficiently
    df['PEG Ratio'] = df['PE Ratio'] / df['1Y Historical EPS Growth']
    df['PEG Ratio'] = df['PEG Ratio'].round(2)
    
    # Handle invalid cases (divide by zero, negative growth)
    mask = (df['1Y Historical EPS Growth'] <= 0) | (df['PEG Ratio'].isin([float('inf'), -float('inf')]))
    df.loc[mask, 'PEG Ratio'] = pd.NA

    return df


def find_fallen_value_stocks():
    # Get the stock data
    file_name = "ticker_tape_250220.csv"
    df = get_stock_data(filepath=os.path.join(os.getenv("INPUT_DIR"), file_name))
    
    # Apply filters:
    # 1. Price fallen more than 35% (6M Return < -35)
    # 2. PEG < 1
    # 3. Positive growth across multiple metrics and positive net income
    filtered_stocks = df[
        (df['6M Return'] < -35) & 
        (df['PEG Ratio'] < 1) & 
        (df['PEG Ratio'] > 0) &  # Exclude negative PEG
        # Check for positive growth across multiple metrics
        (df['1Y Historical EPS Growth'] > 0) &
        (df['1Y Historical Revenue Growth'] > 0) &
        (df['1Y Hist Op. Cash Flow Growth'] > 0) &
        (df['1Y Historical EBITDA Growth'] > 0) &
        # Ensure positive net income
        (df['Net Income (Q)'] > 0)
    ]
    
    # Sort by PEG Ratio (ascending) to get the most undervalued stocks first
    filtered_stocks = filtered_stocks.sort_values('PEG Ratio')
    
    # Select relevant columns for display
    columns_to_display = [
        'Name', 
        'Sub-Sector',
        '6M Return',
        'PEG Ratio',
        'Net Income (Q)',
        '1Y Historical EPS Growth',
        '1Y Historical Revenue Growth',
        '1Y Hist Op. Cash Flow Growth',
        '1Y Historical EBITDA Growth',
        'PE Ratio',
        'Market Cap'
    ]
    
    # Display top 100 results
    result = filtered_stocks[columns_to_display].head(100)
    
    # Save results to CSV
    output_file = 'fallen_value_stocks.csv'
    result.to_csv(output_file, index=False)
    print(f"\nFound {len(filtered_stocks)} stocks matching criteria:")
    print("- Price fallen more than 35%")
    print("- PEG Ratio < 1")
    print("- Positive quarterly net income")
    print("- Positive growth in:")
    print("  * EPS")
    print("  * Revenue")
    print("  * Operating Cash Flow")
    print("  * EBITDA")
    print(f"\nResults saved to {output_file}")
    
    return result

if __name__ == "__main__":
    results = find_fallen_value_stocks()
    print("\nTop 10 stocks:")
    print(results.head(10).to_string(index=False))
