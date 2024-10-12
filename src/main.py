# ============================ Project setup ================================
from dotenv import load_dotenv
import sys
import os
import argparse
import pandas as pd


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


if __name__ == "__main__":
    init_project()

# ============================ Business logic ==============================
if __name__ == "__main__":
    print("Main execution starts")
    from stock_data.service import get_nifty_stock_names, get_stocks_with_financials
    from indicator.service import process_stocks
    from multiprocessing import Pool

    ticker_names = get_nifty_stock_names()

    page_size = 50
    params = []
    result_dataframes = []

    for i in range(0, len(ticker_names), page_size):                    
        ticker_names_page = ticker_names[i:i+page_size]        
        params.append((ticker_names_page))
    
    process_count = os.cpu_count()
    
    with Pool(process_count) as p:
        result_dataframes = p.map(process_stocks, params)

    # Combine all dataframes into a single dataframe
    combined_df = pd.concat(result_dataframes, ignore_index=True)

    # Sort the combined dataframe by "Sum of Ranks" in ascending order
    combined_df = combined_df.sort_values(by="Sum of Ranks", ascending=True)

    print("Combined and sorted dataframe:")
    print(combined_df)

    # Optionally, you can save the combined dataframe to a CSV file
    output_file = os.path.join(os.environ['OUTPUT_DIR'], "combined_stock_metrics.csv")
    combined_df.to_csv(output_file, index=False)
    print(f"Combined stock metrics saved to: {output_file}")
