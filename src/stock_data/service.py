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

    if filepath is None:
        filepath = os.path.join(os.getenv("INPUT_DIR"), params.NIFTY_STOCKS_CSV_FILENAME)
    
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

    return df