# ============================ Project setup ================================
from dotenv import load_dotenv
import sys
import os
import argparse
import pandas as pd
import logging
import builtins


def init_project():
    # Set up PYTHONPATH
    project_src_dir = os.path.dirname(__file__)
    sys.path.append(project_src_dir)
    print(f"Project source directory: {project_src_dir}")

    project_root_dir = os.path.dirname(project_src_dir)
    
    os.environ['ROOT_DIR'] = project_root_dir
    os.environ['OUTPUT_DIR'] = os.path.join(project_root_dir, 'output')
    os.environ['INPUT_DIR'] = os.path.join(project_root_dir, 'input')
    os.environ['ASSET_DIR'] = os.path.join(project_root_dir, 'asset')

    # Load environment variables from .env file
    env_file_path = os.path.join(project_root_dir, '.env')
    load_dotenv(env_file_path)

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Initialize project environment")
    parser.add_argument('--local', action='store_true', help='Run in local mode')
    args = parser.parse_args()

    os.environ['LOCAL_MODE'] = str(args.local)

    from utils.service import init_log
    init_log("main")


if __name__ == "__main__":
    init_project()

# ============================ Business logic ==============================
from stock_data.service import get_nifty_stock_names, get_price_change
from indicator.service import process_stocks
from multiprocessing import Pool
import math


def trending_value_strategy(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise Exception("Dataframe is empty. Cannot run algorithm.")

    # Filter out 10% of the lowest sum of ranks stocks
    builtins.logging.info(f"Filtering out 10% of the lowest sum of ranks stocks for tickers")
    ten_percent = int(len(df) * 0.1)
    if ten_percent < 1:
        ten_percent = 1
        
    df = df.nsmallest(n=ten_percent, columns="Sum of Ranks")

    # Get price change in the last 6 months
    builtins.logging.info(f"Get price change for tickers")
    df = get_price_change(df)

    # Sort the dataframe by "Price Change Percentage" in descending order
    builtins.logging.info(f"Sorting dataframe by Price Change Percentage")
    df = df.sort_values(by="Price Change Percent", ascending=False)

    # Filter out top 25 stocks
    builtins.logging.info(f"Filtering out top 25 stocks")
    df = df.head(25)

    return df


if __name__ == "__main__":
    print("Main execution starts")

    result_dataframes = []

    if os.getenv("LOCAL_MODE") == "True":
        print("Running in local mode")
        # ticker_names = ["AEGISCHEM.NS", "PVP.NS"]

        csv_path = os.path.join(os.getenv("INPUT_DIR"), "nifty_stock_names_copy.csv")
        ticker_names = get_nifty_stock_names(csv_path)

        result_dataframes.append(process_stocks(ticker_names, 0))

    else:
        print("Running in non local mode")

        process_count = os.cpu_count()
        print(f"Process count: {process_count}")

        ticker_names = get_nifty_stock_names()
        page_size = len(ticker_names) // process_count
        
        if page_size == 0:
            page_size = process_count

        print(f"Stock Page size: {page_size}")
        params = []

        for i in range(0, len(ticker_names), page_size):                    
            ticker_names_page = ticker_names[i:i+page_size]        
            params.append((ticker_names_page, math.ceil(i/page_size)))

        with Pool(process_count) as p:
            print("Running in distributed mode. Please check logs in output/logs")
            result_dataframes = p.starmap(process_stocks, params)

    # Combine all dataframes into a single dataframe
    combined_df = pd.concat(result_dataframes, ignore_index=True)

    if combined_df.empty:
        raise Exception("Combined dataframe is empty")
    
    combined_df = trending_value_strategy(combined_df)

    # Sort the combined dataframe by "Sum of Ranks" in ascending order
    # combined_df = combined_df.sort_values(by="Price Change Percent", ascending=False)

    builtins.logging.info("Combined and sorted dataframe:")
    builtins.logging.info(combined_df)

    # Optionally, you can save the combined dataframe to a CSV file
    output_file = os.path.join(os.environ['OUTPUT_DIR'], "stock_with_financials.csv")
    combined_df.to_csv(output_file, index=False)
    print(f"Combined stock metrics saved to: {output_file}")
