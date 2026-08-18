# Real Estate Tracker

An automated, production-grade data ingestion pipeline that tracks daily rental market velocity, inventory shifts, and pricing micro-trends across high-growth sectors in Pasco County, Florida.
Pulls from the cities of: Land O Lakes, Wesley Chapel, New Port Richey and Zephyrhills

## Business Value & Target Metrics
Real estate decisions require localized, longitudinal data. This automated engine captures data snapshots across four distinct market archetypes. Updates on the 1,3,6,8,10,13,15,17,20,22,24,27 days of the month

**Database Goal:**
* Average Rent Shifts: Weekly tracking of regional pricing drift by city.
* Inventory Velocity: Measuring market demand by tracking how quickly live listings are posted and removed.
* Price Elasticity: Mapping geographic variations in pricing spikes down to the zip code level.

## Sample Data Fields Captured
The pipeline automatically structures raw nested JSON payloads into a clean, flat relational schema containing:
* `id` / `sourceUrl` (Listing traceability)
* `price` / `propertyType` / `bedrooms` / `bathrooms` (Structural features)
* `address` / `city` / `zipCode` / `meta_source_city` (Geographic filters)
* `meta_source_county` (Enriched county for BI analysis)

## 📂 Repository File Structure
```text
pasco-county-trends/
├── .github/workflows/
│   └── run_scraper.yml    # GitHub Actions workflow orchestration script
├── .gitignore             # Strict environment exclusions (keeps keys/logs local)
├── app.py                 # Core decoupled execution script (Network & Storage loops)
├── requirements.txt       # Unified Python library dependencies
└── pasco_rental_tracker_YYYY-MM-DD.csv   # Automatically committed daily data assets
```

## Automated Workflow Steps (Daily at 00:00 EDT)
## Important Daylight Saving Time (EDT) Note: update workflow to 0 4 * * * in Spring and 0 5 * * * in Fall
