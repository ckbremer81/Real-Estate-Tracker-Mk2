import logging
import os
import sys
import datetime
from dotenv import load_dotenv
import requests
import pandas as pd
from sqlalchemy import create_engine

# 1. Setup Logging Configuration (writes to console AND app.log file)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 2. Bootstrapping configurations
load_dotenv()
API_TOKEN = os.getenv("API_BEARER_TOKEN")

# Hardcoded absolute routes to bypass any conflicting configuration files
API_BASE_URL = "https://api.rentcast.io/v1"

if not API_TOKEN:
    logger.critical("Missing critical API_BEARER_TOKEN configuration.")
    sys.exit(1)


def fetch_api_data(endpoint: str, query_params: dict = None) -> dict:
    """Network Function: Authenticates and downloads raw RentCast real estate data."""
    url = f"{API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    
    headers = {
        "X-Api-Key": API_TOKEN,
        "Accept": "application/json"
    }
    
    logger.info(f"Initiating connection to endpoint: /{endpoint} with params: {query_params}")
    try:
        response = requests.get(url, headers=headers, params=query_params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code if http_err.response else "Unknown"
        logger.error(f"HTTP payload failure {status_code}: {http_err}")
    except requests.exceptions.RequestException as net_err:
        logger.error(f"Network transport error encountered: {net_err}")
    return {}


# ==========================================
# DECOUPLED STORAGE LAYER OPTIONS
# ==========================================

def save_data_to_csv(records: list, filename_prefix: str) -> str:
    """Storage Option A: Handles formatting and saving to a flat local file."""
    if not records:
        logger.warning("No records provided to save to CSV.")
        return ""
        
    df = pd.json_normalize(records)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    output_file = f"{filename_prefix}_{today_str}.csv"
    
    df.to_csv(output_file, index=False)
    logger.info(f"Successfully saved TOTAL of {len(df)} rows across all pages to {output_file}")
    return output_file


# ==========================================
# CORE EXECUTION PIPELINE CONTROL PANEL
# ==========================================

if __name__ == "__main__":
    logger.info("Starting Pasco County Rental Market Micro-Trends Tracker run.")
    
    # Official RentCast path extension for active rental searches
    target_endpoint = "listings/rental/long-term"  
    
    # Loop through major high-growth and rental cities strictly within Pasco County
    pasco_cities = ["Land O Lakes", "Wesley Chapel", "New Port Richey", "Zephyrhills"]
    state_target = "FL"
    
    all_extracted_records = []
    
    #for city in pasco_cities:
    #    logger.info(f"=== Beginning Data Ingestion for {city}, Pasco County ===")
        
    #    base_parameters = {
    #        "city": city,
    #        "state": state_target,
    #        "status": "Active",
    #        "limit": 25
    #    }
        
    #    current_page = 1
    #    max_pages = 1 
        
    #    while current_page <= max_pages:
    #        page_params = base_parameters.copy()
    #        page_params["offset"] = (current_page - 1) * base_parameters["limit"]
            
    #        data = fetch_api_data(target_endpoint, query_params=page_params)
    #        if not data or not isinstance(data, list):
    #            break
                
            # Tag each record row with its matching metadata parameters
    #        for record in data:
    #            if isinstance(record, dict):
    #                record["meta_source_county"] = "Pasco"
    #                record["meta_source_city"] = city
                    
    #        all_extracted_records.extend(data)
    #        logger.info(f"Gathered {len(data)} listings from {city} (Page {current_page}).")
    #        current_page += 1

    # ==========================================
    # Step 3: Run Orchestrated Storage & Compilation
    # ==========================================
    
    # Action A: Save the fresh daily snapshot file
    daily_file = save_data_to_csv(all_extracted_records, filename_prefix="pasco_rental_tracker")
    
    # Action B: AUTOMATED COMPILATION & TRANSFORMATION LAYER
    import glob
    
    logger.info("Initializing automated data compilation layer...")
    historical_files = sorted(glob.glob("pasco_rental_tracker_*.csv"))
    
    if historical_files:
        logger.info(f"Automated pipeline located {len(historical_files)} historical files to merge.")
        
        df_list = []
        for file in historical_files:
            # Read each historical sheet safely keeping leading zeros on zips
            current_df = pd.read_csv(file, dtype={"zipCode": str})
            df_list.append(current_df)
            
        # Stack all historical data vertically into one master DataFrame
        master_df = pd.concat(df_list, ignore_index=True)
        logger.info(f"Initial raw union complete: Loaded {len(master_df)} total property observations.")
        
        # ==========================================
        # AUTOMATED DATA CLEANING LAYER
        # ==========================================
        logger.info("Executing automated data cleansing routines...")
        
        # 1. Column Selection: Keep ONLY fields valuable for analysis
        columns_to_keep = [
            "formattedAddress", "city", "zipCode", 
            "price", "propertyType", "bedrooms", "bathrooms", "squareFootage", 
            "yearBuilt", "latitude", "longitude", "listedDate"
        ]
        
        # Filter dataframe only picking columns that actually exist in the data
        existing_columns = [col for col in columns_to_keep if col in master_df.columns]
        cleaned_df = master_df[existing_columns].copy()
        
        # 2. Defensive Cleaning
        cleaned_df.dropna(subset=["formattedAddress", "price", "zipCode"], inplace=True)

        # ==========================================
        # DATE FORMATTING OPERATION
        # ==========================================
        if "listedDate" in cleaned_df.columns:
            # Step A: Convert the raw text/timestamp string into a standardized Pandas datetime object
            cleaned_df["listedDate"] = pd.to_datetime(cleaned_df["listedDate"], errors='coerce')
            
            # Step B: Strip out the time components, leaving a clean "YYYY-MM-DD" date format
            cleaned_df["listedDate"] = cleaned_df["listedDate"].dt.date
        # ==========================================
        
        # 3. Data Type Hardening: Ensures zip codes keep string integrity and prices act as clean integers for charts
        cleaned_df["zipCode"] = cleaned_df["zipCode"].astype(str).str.split('.').str[0].str.zfill(5)
        cleaned_df["price"] = pd.to_numeric(cleaned_df["price"], errors='coerce').fillna(0).astype(int)
        
        if "squareFootage" in cleaned_df.columns:
            cleaned_df["squareFootage"] = pd.to_numeric(cleaned_df["squareFeet"], errors='coerce').fillna(0).astype(int)
            
        # 4. Remove exact duplicates to preserve timeseries trend integrity
        cleaned_df.drop_duplicates(subset=["formattedAddress", "price", "city"], keep="first", inplace=True)
        
        # Save out the structured, optimized asset file for BI tools
        master_output = "master_pasco_rental_trends.csv"
        cleaned_df.to_csv(master_output, index=False)
        logger.info(f"Clean pipeline complete! Saved {len(cleaned_df)} pristine rows to {master_output}")
    else:
        logger.warning("No historical tracker files found in workspace to compile.")
