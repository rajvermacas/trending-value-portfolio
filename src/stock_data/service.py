import os
import pandas as pd
from stock_data import params
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Set
import builtins


def get_nifty_stock_names(csv_path: str=None) -> List[str]:
    if csv_path is None:
        csv_path = os.path.join(os.getenv("INPUT_DIR"), params.NIFTY_STOCKS_CSV_FILENAME)

    print(f"Getting all nifty stocks from path: {csv_path}")
    df = pd.read_csv(csv_path)
    df['Symbol'] = df['Symbol']+".NS"

    return list(df.Symbol)

def _get_rounded_value(value: float, decimals: int=2) -> float:
    return round(value, decimals) if value is not None and isinstance(value, float) else None

def get_stocks_with_financials(tickers: Set[str]) -> pd.DataFrame:
    all_metrics = []
    for ticker in tickers:
        try:
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
            
            # Extract the requested metrics
            try:
                metrics = {
                    "Ticker": ticker,
                    "Price-to-Earnings Ratio": _get_rounded_value(info.get("trailingPE", -1)),
                    "Price-to-Book Ratio": _get_rounded_value(info.get("priceToBook", -1)),
                    "Price-to-Sales Ratio": _get_rounded_value(info.get("priceToSalesTrailing12Months", -1)),
                    "EV-to-EBITDA Ratio": _get_rounded_value(info.get("enterpriseToEbitda", -1)),
                    "Price-to-Cash Flow Ratio": _get_rounded_value(price_to_cash_flow),
                    "Dividend Yield": _get_rounded_value(info.get("dividendYield", -1) * 100),
                    "Market Cap": info.get("marketCap"),
                }
            except Exception as fault:
                print(f"Error extracting financial metrics for ticker={ticker}: {fault}")
            
            all_metrics.append(metrics)
        
        except Exception as fault:
            print(f"Error fetching financial metrics for ticker={ticker}: {fault}")
    
    df = pd.DataFrame(all_metrics)
    return df

def get_price_change(df: pd.DataFrame, days: int=180) -> pd.DataFrame:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    if df.empty:
        raise Exception("Input dataframe is empty. No price change can be calculated.")

    # Download price data for all tickers for the last 6 months
    data = yf.download(df.Ticker.tolist(), start=start_date, end=end_date)

    # Check if data is an empty DataFrame
    if data.empty:
        print(f"Warning: Downloaded price data is empty. Unable to calculate price changes.Tickers={df.Ticker.tolist()}")
        builtins.logging.debug(f"Warning: Downloaded price data is empty. Unable to calculate price changes.Tickers={df.Ticker.tolist()}")
        
        df['Price Change Percent'] = None
        return df

    price_changes = []
    for ticker in df.Ticker:
        try:
            if ticker in data["Close"].columns:
                initial_price = data["Close"][ticker].iloc[0]
                final_price = data["Close"][ticker].iloc[-1]
                price_change = round(((final_price - initial_price) / initial_price) * 100, 2)
                price_changes.append(price_change)
            else:
                price_changes.append(None)
        
        except Exception as fault:
            print(f"Error calculating price change for ticker={ticker}: {fault}")
    
    try:
        df['Price Change Percent'] = price_changes
    except Exception as fault:
        print(f"Error assigning price change to dataframe: {fault}")

    return df
    

if __name__=="__main__":
    import sys
    sys.path.append(r"C:\Users\mrina\Documents\Projects\trending-value-portfolio\src")
    
    from main import init_project
    init_project()

    tickers = get_nifty_stock_names()
    df = get_stocks_with_financials(tickers)
    df = get_price_change(df)
    print(df)