"""
Analyze stock price movements between two dates and display the results.

Usage:
    python get_stocks_price_movement.py [--start_date YYYY-MM-DD] [--end_date YYYY-MM-DD]

Arguments:
    --start_date : Optional. Start date for analysis in YYYY-MM-DD format.
                   Default: 6 months ago from today.
    --end_date   : Optional. End date for analysis in YYYY-MM-DD format.
                   Default: Today's date.

Input:
    - CSV file: 'trending_value_portfolio_ticker_tape_241104.csv' in the 'input' directory.
    - The CSV file should contain at least two columns: 'Name' and 'Symbol'.

Output:
    - Displays stock price movement analysis for the specified period.
    - Shows individual stock performance and portfolio summary.

Note:
    - NSE stock symbols are automatically appended with '.NS'.
    - Dates are validated to ensure correct format.
"""


import pandas as pd
from datetime import datetime, date, timedelta
import yfinance as yf
import argparse
import os

def validate_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format. Please use YYYY-MM-DD")

def get_stock_data(company_name, symbol, start_date, end_date):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            print(f"No data available for {company_name} ({symbol})")
            return None
        
        start_price = hist.iloc[0]['Close']
        end_price = hist.iloc[-1]['Close']
        price_change = end_price - start_price
        price_change_percent = (price_change / start_price) * 100
        
        return {
            'company': company_name,
            'symbol': symbol,
            'start_price': start_price,
            'end_price': end_price,
            'price_change': price_change,
            'price_change_percent': price_change_percent
        }
    except Exception as e:
        print(f"Error fetching data for {company_name} ({symbol}): {str(e)}")
        return None

def get_nse_performance(start_date, end_date):
    try:
        # Fetch NIFTY 50 data using ^NSEI symbol
        nifty = yf.Ticker("^NSEI")
        hist = nifty.history(start=start_date, end=end_date)
        
        if hist.empty:
            return None
            
        start_price = hist.iloc[0]['Close']
        end_price = hist.iloc[-1]['Close']
        price_change = end_price - start_price
        price_change_percent = (price_change / start_price) * 100
        
        return {
            'start_price': start_price,
            'end_price': end_price,
            'price_change': price_change,
            'price_change_percent': price_change_percent
        }
    except Exception as e:
        print(f"Error fetching NSE data: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Analyze stock price movements between two dates')
    parser.add_argument('--start_date', type=validate_date, 
                      help='Start date in YYYY-MM-DD format (default: 6 months ago)')
    parser.add_argument('--end_date', type=validate_date, default=date.today(),
                      help='End date in YYYY-MM-DD format (default: today)')
    
    args = parser.parse_args()
    
    # If start_date is not provided, set it to 6 months ago
    if not args.start_date:
        args.start_date = date.today() - timedelta(days=180)
    
    # Get NSE performance first
    nse_performance = get_nse_performance(args.start_date, args.end_date)
    
    # Read stock names from CSV file
    try:
        input_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'input', 'trending_value_portfolio_ticker_tape_241104.csv')
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return

    results = []
    for _, row in df.iterrows():
        symbol = f"{row['Symbol']}.NS"  # Append .NS to the symbol for NSE stocks
        data = get_stock_data(row['Name'], symbol, args.start_date, args.end_date)
        if data:
            results.append(data)

    # Convert results to DataFrame and display
    if results:
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('price_change_percent', ascending=False)
        pd.set_option('display.float_format', '{:.2f}'.format)
        
        print("\nStock Price Movement Analysis:")
        print(f"Period: {args.start_date} to {args.end_date}")
        print("\nIndividual Stock Performance:")
        print(results_df[['company', 'symbol', 'start_price', 'end_price', 'price_change', 'price_change_percent']])
        
        # Calculate and display portfolio summary
        print("\nPortfolio Summary:")
        print("-" * 50)
        print(f"Analysis Period: {args.start_date} to {args.end_date}")
        print("-" * 50)
        print(f"Total Stocks Analyzed: {len(results_df)}")
        portfolio_return = results_df['price_change_percent'].mean()
        print(f"Portfolio Average Return: {portfolio_return:.2f}%")
        
        # Add NSE comparison if available
        if nse_performance:
            nse_return = nse_performance['price_change_percent']
            outperformance = portfolio_return - nse_return
            print(f"NSE Return: {nse_return:.2f}%")
            print(f"Portfolio Outperformance: {outperformance:+.2f}%")  # + sign for positive values
            
            # Count stocks beating NSE
            beats_nse = len(results_df[results_df['price_change_percent'] > nse_return])
            print(f"Stocks Beating NSE: {beats_nse} out of {len(results_df)} ({(beats_nse/len(results_df)*100):.1f}%)")
        
        print(f"\nBest Performer: {results_df.iloc[0]['company']} ({results_df.iloc[0]['price_change_percent']:.2f}%)")
        print(f"Worst Performer: {results_df.iloc[-1]['company']} ({results_df.iloc[-1]['price_change_percent']:.2f}%)")
        gainers = len(results_df[results_df['price_change_percent'] > 0])
        losers = len(results_df[results_df['price_change_percent'] < 0])
        neutral = len(results_df[results_df['price_change_percent'] == 0])
        print(f"Gainers: {gainers} stocks")
        print(f"Losers: {losers} stocks")
        print(f"Neutral: {neutral} stocks")
        
        # Calculate quartile performance
        quartiles = results_df['price_change_percent'].quantile([0.25, 0.5, 0.75])
        print(f"\nQuartile Performance:")
        print(f"25th Percentile: {quartiles[0.25]:.2f}%")
        print(f"Median: {quartiles[0.5]:.2f}%")
        print(f"75th Percentile: {quartiles[0.75]:.2f}%")
        
        # Final reminder of analysis period
        print("\n" + "-" * 50)
        print(f"Analysis Period: {args.start_date} to {args.end_date}")
        print("-" * 50)
    else:
        print("No data available for the specified period")

if __name__ == "__main__":
    main()