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


def find_fallen_stocks(df: pd.DataFrame, return_column: str, mcap_filter: float = None) -> pd.DataFrame:
    """
    Filter stocks based on return threshold and optional market cap
    """
    filter_conditions = [
        (df[return_column] < -35),  # Price fallen more than 35%
        # (df['Earnings Per Share'] > 0),  # Current EPS is positive
        # (df['1Y Historical EPS Growth'] > 0),  # EPS is growing
        (df['1Y Historical Revenue Growth'] > 0),
        # (df['1Y Hist Op. Cash Flow Growth'] > 0),
        # (df['1Y Historical EBITDA Growth'] > 0),
        # (df['Net Income (Q)'] > 0)
    ]
    
    if mcap_filter is not None:
        filter_conditions.append(df['Market Cap'] >= mcap_filter)
    
    filtered_stocks = df[pd.concat(filter_conditions, axis=1).all(axis=1)]
    
    # Sort by return (ascending) to get the biggest drops first
    filtered_stocks = filtered_stocks.sort_values(return_column)
    
    return filtered_stocks

def analyze_fallen_stocks():
    # Get the stock data
    file_name = "ticker_tape_250220.csv"
    df = get_stock_data(filepath=os.path.join(os.getenv("INPUT_DIR"), file_name))
    
    # Columns to display in output
    columns_to_display = [
        'Name', 
        'Sub-Sector',
        'Market Cap',
        '1M Return',
        '6M Return',
        '1Y Return',
        'Earnings Per Share',
        '1Y Historical EPS Growth',
        'Net Income (Q)',
        '1Y Historical Revenue Growth',
        '1Y Hist Op. Cash Flow Growth',
        '1Y Historical EBITDA Growth',
        'PE Ratio',
        'PEG Ratio'
    ]
    
    # Define analysis scenarios
    scenarios = [
        {
            'name': '1M_fallen_stocks',
            'return_column': '1M Return',
            'description': 'Stocks fallen by 35% or more in 1 month'
        },
        {
            'name': '6M_fallen_stocks',
            'return_column': '6M Return',
            'description': 'Stocks fallen by 35% or more in 6 months'
        },
        {
            'name': '1Y_fallen_stocks',
            'return_column': '1Y Return',
            'description': 'Stocks fallen by 35% or more in 1 year'
        },
        {
            'name': '1Y_fallen_large_cap_stocks',
            'return_column': '1Y Return',
            'mcap_filter': 10000,  # 10,000 crores for large cap
            'description': 'Large cap stocks (>10,000 cr) fallen by 35% or more in 1 year'
        }
    ]
    
    print("\n" + "="*70)
    print("Analyzing Fallen Stocks with Strong Fundamentals")
    print("="*70)
    
    # Process each scenario
    for scenario in scenarios:
        # Get filtered stocks
        filtered_stocks = find_fallen_stocks(
            df, 
            scenario['return_column'],
            scenario.get('mcap_filter')
        )
        
        # Save to CSV
        output_file = f"{scenario['name']}.csv"
        result = filtered_stocks[columns_to_display].head(100)
        result.to_csv(output_file, index=False)
        
        # Print summary
        print(f"\n{scenario['description']}:")
        print(f"- Found {len(filtered_stocks)} stocks")
        print(f"- Top 100 results saved to: {output_file}")
        
        # Print market cap distribution if available
        if len(filtered_stocks) > 0:
            mcap_stats = filtered_stocks['Market Cap'].describe()
            print(f"- Market Cap Statistics (in crores):")
            print(f"  * Min: {mcap_stats['min']:.0f}")
            print(f"  * Median: {mcap_stats['50%']:.0f}")
            print(f"  * Max: {mcap_stats['max']:.0f}")
    
    print("\nFilter Criteria Applied to All Results:")
    print("1. Earnings Quality:")
    print("   - Positive current EPS")
    print("   - Positive Net Income (Latest Quarter)")
    print("\n2. Growth Metrics (All Positive):")
    print("   - EPS Growth (Year-over-Year)")
    print("   - Revenue Growth (Year-over-Year)")
    print("   - Operating Cash Flow Growth (Year-over-Year)")
    print("   - EBITDA Growth (Year-over-Year)")
    print("\n" + "-"*70)

if __name__ == "__main__":
    analyze_fallen_stocks()
