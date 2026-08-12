import logging
import glob
import os
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def compile_daily_trackers(input_pattern: str, output_filename: str):
    """
    Finds all daily real estate CSV files, merges them chronologically,
    removes duplicate rows, and prepares a unified analytical dataset.
    """
    # 1. Gather all matching daily CSV files in the folder
    csv_files = sorted(glob.glob(input_pattern))
    
    if not csv_files:
        logger.warning(f"No files found matching pattern: {input_pattern}")
        return
        
    logger.info(f"Found {len(csv_files)} historical daily files to process.")
    
    # 2. Read and stack all individual sheets into a single master list
    df_list = []
    for file in csv_files:
        logger.info(f"Reading data from: {os.path.basename(file)}")
        # Read the file and ensure text columns don't drop leading zeros (like Zip Codes)
        current_df = pd.read_csv(file, dtype={"zipCode": str})
        df_list.append(current_df)
        
    # Combine all individual tables vertically
    master_df = pd.concat(df_list, ignore_index=True)
    logger.info(f"Initial raw union complete: Loaded {len(master_df)} total property observations.")
    
    # 3. Clean up the data layer
    master_df.drop_duplicates(inplace=True)
    
    # 4. Save the compiled file
    master_df.to_csv(output_filename, index=False)
    logger.info(f"Data consolidation successful! Saved {len(master_df)} clean rows to {output_filename}")


if __name__ == "__main__":
    logger.info("Initializing historical data consolidation pipeline.")
    
    search_criteria = "pasco_rental_tracker_*.csv"
    final_output = "master_pasco_rental_trends.csv"
    
    compile_daily_trackers(search_criteria, final_output)
