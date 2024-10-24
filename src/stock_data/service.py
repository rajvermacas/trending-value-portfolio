import os
import pandas as pd
from stock_data import params
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Set
import builtins


def get_stock_data(filepath: str=None) -> pd.DataFrame:
    # CSV column names
    # "Name",
    # "Sub-Sector",
    # "Market Cap",
    # "6M Return",
    # "1Y Historical EPS Growth",
    # "Earnings Per Share"
    # "PE Ratio",
    # "PB Ratio",
    # "PS Ratio",
    # "EV/EBITDA Ratio",
    # "Price / CFO",
    # "Dividend Yield"
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
        "Price / CFO"
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
