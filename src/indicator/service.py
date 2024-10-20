import pandas as pd
from typing import List
from utils.service import init_log
import builtins


def assign_ranks_to_financial_metrics(df: pd.DataFrame) -> pd.DataFrame:
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

    # List of metrics to rank
    metrics_to_rank = [
        "PE Ratio",
        "PB Ratio",
        "PS Ratio",
        "EV/EBITDA Ratio",
        "Price / CFO",
        "Dividend Yield"
    ]
    
    # Rank each metric
    for metric in metrics_to_rank:
        # Handle None, NA, or missing values
        df[metric] = pd.to_numeric(df[metric], errors='coerce')
        
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
