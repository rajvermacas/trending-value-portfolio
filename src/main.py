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
from stock_data.service import get_stock_data
from indicator.service import assign_ranks_to_financial_metrics
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

    # Sort the dataframe by "Price Change Percentage" in descending order
    builtins.logging.info(f"Sorting dataframe by 6M Return")
    df = df.sort_values(by="6M Return", ascending=False)

    # Filter out top 25 stocks
    builtins.logging.info(f"Filtering out top 25 stocks")
    df = df.head(25)

    return df


if __name__ == "__main__":
    print("Main execution starts")

    result_dataframes = []

    if os.getenv("LOCAL_MODE") == "True":
        print("Running in local mode")

    else:
        print("Running in non local mode")

        process_count = os.cpu_count()
        print(f"Process count: {process_count}")

    # Combine all dataframes into a single dataframe
    df = get_stock_data()
    df = assign_ranks_to_financial_metrics(df)

    df = trending_value_strategy(df)

    # df = df.sort_values(by="6M Return", ascending=False)
    
    builtins.logging.info("Combined and sorted dataframe:")
    builtins.logging.info(df)

    # Optionally, you can save the combined dataframe to a CSV file
    output_file = os.path.join(os.environ['OUTPUT_DIR'], "trending_value_portfolio.csv")
    df.to_csv(output_file, index=False)
    print(f"Combined stock metrics saved to: {output_file}")
