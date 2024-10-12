import os
import pandas as pd
from stock_data import params
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Set


def get_nifty_stock_names() -> List[str]:
    # The result set will contain .NS suffix
    csv_path = os.path.join(os.getenv("INPUT_DIR"), params.NIFTY_STOCKS_CSV_FILENAME)
    print(f"Getting all nifty stocks from path: {csv_path}")

    df = pd.read_csv(csv_path)
    df['Symbol'] = df['Symbol']+".NS"

    return list(df.Symbol)

def get_stocks_with_financials(tickers: Set[str], lookback_days=180) -> pd.DataFrame:
    # Download financial data for all tickers
    # Calculate the date 6 months ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)

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
            "EV-to-EBITDA Ratio": info.get("enterpriseToEbitda"),
            "Price-to-Cash Flow Ratio": price_to_cash_flow,
            "Dividend Yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else None,
            "Market Cap": info.get("marketCap"),
            "6-Month Price Change (%)": price_change_6m
        }
        
        all_metrics.append(metrics)
    
    df = pd.DataFrame(all_metrics)
    return df


if __name__=="__main__":
    import sys
    sys.path.append(r"C:\Users\mrina\Documents\Projects\trending-value-portfolio\src")
    
    from main import init_project
    init_project()

    start_date = "2024-07-25"
    end_date = "2024-09-26"
    ticker_names = ["DIXON.NS", "PGEL.NS"]

    # get_tickers_data(start_date, end_date, ticker_names)
