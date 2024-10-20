import pandas as pd
from stock_data.service import get_stocks_with_financials, get_stocks_with_financials_from_excel, get_price_change
from typing import List
from utils.service import init_log
import builtins


def assign_ranks_to_financial_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # List of metrics to rank
    metrics_to_rank = [
        "Price-to-Earnings Ratio",
        "Price-to-Book Ratio",
        "Price-to-Sales Ratio",
        "EV-to-EBITDA Ratio",
        "Price-to-Cash Flow Ratio",
        "Dividend Yield"
    ]
    
    # Rank each metric
    for metric in metrics_to_rank:
        # Handle None, NA, or missing values
        df[metric] = pd.to_numeric(df[metric], errors='coerce')
        
        # Determine the number of stocks in each rank
        num_stocks = len(df)
        stocks_per_rank = max(1, num_stocks // 10)
        
        if metric == "Dividend Yield":
            # For Dividend Yield, higher is better
            df[f"{metric} Rank"] = pd.qcut(df[metric].rank(method='dense', ascending=False), 
                                           q=10, labels=False, duplicates='drop') + 1
        else:
            # For other metrics, lower is better
            df[f"{metric} Rank"] = pd.qcut(df[metric].rank(method='dense'), 
                                           q=10, labels=False, duplicates='drop') + 1
        
        # Assign rank 10 to stocks with missing values
        df.loc[(df[metric].isna()) | (df[metric] < 0), f"{metric} Rank"] = 10        
    
    # Calculate the sum of ranks
    rank_columns = [f"{metric} Rank" for metric in metrics_to_rank]
    df["Sum of Ranks"] = df[rank_columns].sum(axis=1)
    
    return df

def process_stocks(ticker_names: List[str], counter: int) -> pd.DataFrame:
    try:
        init_log(counter)
        
        builtins.logging.info(f"Processing ticker counter={counter}")
        builtins.logging.info(f"Get stocks financials for ticker counter={counter}")
        df = get_stocks_with_financials(ticker_names)

        builtins.logging.info(f"Assinging ranks to financial metrics for ticker counter={counter}")
        df = assign_ranks_to_financial_metrics(df)

        # Filter out the stocks whose market cap is greater than 500 cr
        df = df[df["Market Cap"] > 5_000_000_000]  # 500 crores in rupees

        return df
    
    except Exception as fault:
        print(f"Error processing ticker counter = {counter}: {fault}")
        return pd.DataFrame()
