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
    logger.info("Starting Tampa Bay Tri-County Rental Market Tracker run.")
    
    # Official RentCast path extension for active rental searches
    target_endpoint = "listings/rental/long-term"  
    
    # Mapping our targeted counties to prominent cities within them
    target_cities = {
        "Pasco": "Land O Lakes",
        "Hillsborough": "Tampa",
        "Pinellas": "St. Petersburg"
    }
    state_target = "FL"
    
    all_extracted_records = []
    
    # Cycle through our geographic keys
    for county, city in target_cities.items():
        logger.info(f"=== Beginning Data Ingestion for {county} County ({city}) ===")
        
        base_parameters = {
            "city": city,
            "state": state_target,
            "status": "Active",
            "limit": 25
        }
        
        current_page = 1
        max_pages = 1  # Safe baseline test
        
        while current_page <= max_pages:
            page_params = base_parameters.copy()
            # RentCast uses 'offset' for pagination, calculation moves batches forward
            page_params["offset"] = (current_page - 1) * base_parameters["limit"]
            
            data = fetch_api_data(target_endpoint, query_params=page_params)
            if not data or not isinstance(data, list):
                break
                
            # Tag each record row with its matching metadata parameters
            for record in data:
                if isinstance(record, dict):
                    record["meta_source_county"] = county
                    record["meta_source_city"] = city
                    
            all_extracted_records.extend(data)
            logger.info(f"Gathered {len(data)} listings from {city} (Page {current_page}).")
            current_page += 1

    # Step 3: Run Storage Ingestion
    save_data_to_csv(all_extracted_records, filename_prefix="tampa_bay_rental_tracker")
