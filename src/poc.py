import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def get_stock_metrics(tickers):
    # Calculate the date 6 months ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    # Download price data for all tickers for the last 6 months
    data = yf.download(tickers, start=start_date, end=end_date)
    
    all_metrics = []
    for ticker in tickers:
        # Create a Ticker object
        stock = yf.Ticker(ticker)
        
        # Fetch the data
        info = stock.info
        
        # Fetch cash flow data
        cash_flow = stock.cashflow
        
        # Calculate Price to Cash Flow ratio
        cash_flow_from_operations_column_name = "Operating Cash Flow"

        if not cash_flow.empty and cash_flow_from_operations_column_name in cash_flow.index:
            cash_flow_from_operations = cash_flow.loc[cash_flow_from_operations_column_name].iloc[0]
            if cash_flow_from_operations != 0:
                price_to_cash_flow = info.get('marketCap', 0) / cash_flow_from_operations
            else:
                price_to_cash_flow = None
        else:
            price_to_cash_flow = None
        
        # Calculate the percentage change in price over the last 6 months
        if ticker in data["Close"].columns:
            initial_price = data["Close"][ticker].iloc[0]
            final_price = data["Close"][ticker].iloc[-1]
            price_change_6m = ((final_price - initial_price) / initial_price) * 100
        else:
            price_change_6m = None
        
        # Extract the requested metrics
        metrics = {
            "Ticker": ticker,
            "Price-to-Earnings Ratio": info.get("trailingPE"),
            "Price-to-Book Ratio": info.get("priceToBook"),
            "Price-to-Sales Ratio": info.get("priceToSalesTrailing12Months"),
            "EV-to-EBITDA": info.get("enterpriseToEbitda"),
            "Price-to-Cash Flow": price_to_cash_flow,
            "Market Cap": info.get("marketCap"),
            "Dividend Yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else None,
            "6-Month Price Change (%)": price_change_6m
        }
        
        all_metrics.append(metrics)
    
    df = pd.DataFrame(all_metrics)
    
    # List of metrics to rank
    metrics_to_rank = [
        "Price-to-Earnings Ratio",
        "Price-to-Book Ratio",
        "Price-to-Sales Ratio",
        "EV-to-EBITDA",
        "Price-to-Cash Flow",
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


if __name__ == "__main__":
    # Example usage
    tickers = ["DIXON.NS", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", 
            "ICICIBANK.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "AXISBANK.NS"]

    metrics_df = get_stock_metrics(tickers)
    metrics_df = metrics_df.sort_values(by="Sum of Ranks", ascending=True)

    # Display the DataFrame
    print(metrics_df)

    # Save the DataFrame to a CSV file
    output_file = os.path.join(r"C:\Users\mrina\Documents\Projects\trending-value-portfolio\output", "stock_metrics.csv")
    metrics_df.to_csv(output_file, index=False)
    print(f"Stock metrics saved to: {output_file}")

    # Optionally, save the DataFrame to a CSV file
    # metrics_df.to_csv("stock_metrics.csv", index=False)
