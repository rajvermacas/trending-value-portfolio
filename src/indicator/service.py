import pandas as pd
from stock_data.service import get_nifty_stock_names, get_stocks_with_financials
from typing import List


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

def process_stocks(ticker_names: List[str]) -> pd.DataFrame:
    df = get_stocks_with_financials(ticker_names)
    df = assign_ranks_to_financial_metrics(df)
    df = df.sort_values(by="Sum of Ranks", ascending=True)
    return df
