"""
1. Create input files per sector. 
for example: ticker_tape_241201_communication_services
Create these files for all the sector

2. For all the files created in step 1, Run main.py to create output file like below:
trending_value_portfolio_ticker_tape_241201_communication_services.csv

3. Combine all the top 3 stocks from all the output files created in step 2 into one file like below:
treding_value_portfolio_all_sectors_2_stocks.csv

4. Run double_sort.py to create output file like below:
double_sorted_portfolio_treding_value_portfolio_all_sectors_2_stocks_241201.csv
"""

import pandas as pd
import os
from datetime import datetime

def normalize_column(series):
    """Normalize values to a 0-1 scale"""
    min_val = series.min()
    max_val = series.max()
    return (series - min_val) / (max_val - min_val)

def double_sort_strategy(df: pd.DataFrame, return_weight: float = 0.6, rank_weight: float = 0.4) -> pd.DataFrame:
    """
    Sort stocks based on both 6M Return and Sum of Ranks using a weighted approach
    
    Args:
        df: Input DataFrame
        return_weight: Weight for 6M Return (default: 0.6)
        rank_weight: Weight for Sum of Ranks (default: 0.4)
    """
    if df.empty:
        raise Exception("DataFrame is empty")
    
    # Store original order (sorted by 6M Return)
    df_original = df.sort_values('6M Return', ascending=False).reset_index(drop=True)
    df_original['Original_Rank'] = df_original.index + 1
    
    # Normalize both columns to 0-1 scale
    df['Normalized_Return'] = normalize_column(df['6M Return'])
    # For Sum of Ranks, we want lower values to be better, so we invert the normalization
    df['Normalized_Ranks'] = 1 - normalize_column(df['Sum of Ranks'])
    
    # Calculate weighted score
    df['Combined_Score'] = (df['Normalized_Return'] * return_weight + 
                          df['Normalized_Ranks'] * rank_weight)
    
    # Sort by combined score in descending order
    df_sorted = df.sort_values('Combined_Score', ascending=False).reset_index(drop=True)
    df_sorted['New_Rank'] = df_sorted.index + 1
    
    # Merge original ranks
    df_sorted = df_sorted.merge(df_original[['Name', 'Original_Rank']], on='Name', how='left')
    
    # Drop temporary columns
    df_sorted = df_sorted.drop(['Normalized_Return', 'Normalized_Ranks', 'Combined_Score'], axis=1)
    
    return df_sorted

def main():
    # Read input file
    input_file_name = 'treding_value_portfolio_all_sectors_2_stocks.csv'
    input_file = os.path.join('/root/projects/output', input_file_name)
    df = pd.read_csv(input_file)
    
    # Apply double sorting strategy
    result_df = double_sort_strategy(df)
    
    # Save results
    timestamp = datetime.now().strftime('%y%m%d')
    output_file = os.path.join('/root/projects/output', f'double_sorted_portfolio_{input_file_name[:-4]}_{timestamp}.csv')
    result_df.to_csv(output_file, index=False)
    
    print(f"\nTop 10 stocks after double sorting:")
    print(result_df[['Name', '6M Return', 'Sum of Ranks']].head(10))
    
    print("\nRanking Changes:")
    for _, row in result_df.head(10).iterrows():
        rank_change = row['Original_Rank'] - row['New_Rank']
        change_str = "↑" if rank_change > 0 else "↓" if rank_change < 0 else "="
        print(f"Stock: {row['Name']}, Previous ranking={row['Original_Rank']}, Current ranking={row['New_Rank']} ({change_str})")
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()