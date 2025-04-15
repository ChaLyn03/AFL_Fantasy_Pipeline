# AFL Fantasy Stats Pipeline

This repository implements an end‐to‐end pipeline for retrieving, processing, and analyzing AFL Fantasy statistics. The system is broken down into several stages. It first fetches raw data from public endpoints, then collates and stores the data in a SQLite database, calculates derivative (or “secondary”) metrics, and finally integrates the processed data with your team information to create summary reports. This README details each component, the data flow, and the overall conceptual design.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Pipeline Components](#pipeline-components)
   - [Data Scraping](#data-scraping)
   - [Data Collation and Storage](#data-collation-and-storage)
   - [Derivative Metrics Calculation](#derivative-metrics-calculation)
   - [Team Stats Integration](#team-stats-integration)
4. [Database Structure](#database-structure)
5. [Usage Instructions](#usage-instructions)
6. [Code Structure Diagram](#code-structure-diagram)
7. [Notes and Customization](#notes-and-customization)

## Overview

The project comprises several Python scripts that work together in a pipeline:

1. **Data Collection:**  
   Two scraping scripts pull raw player and coach data from AFL Fantasy API endpoints in JSON format.

2. **Data Collation:**  
   A dedicated script reads the scraped JSON data, dynamically detects available stat keys (like rounds for prices, scores, ranks, transfers, etc.), and creates a comprehensive SQLite database containing raw player data, coach data, and a combined dataset.

3. **Derivative Metrics Calculation:**  
   A subsequent script copies the raw collated database and augments it by calculating derivative statistics (e.g., points per game, consistency, recent trends, cost efficiency). These columns are added to tables (for both players and coaches) in the new database.

4. **Team Statistics:**  
   The final script uses live API calls to obtain the current team composition (including adjustments for pending trades) and then queries the derivative database to produce a team statistics report. It exports the result as a CSV file and also creates a dedicated team database.

## Prerequisites

- **Python 3.x:** The scripts use Python’s standard libraries plus `requests` for HTTP API calls.
- **SQLite3:** The pipelines use SQLite3 for database storage and analysis.
- **Internet Connection:** Needed for the API calls to fetch the latest data.
- **Valid Authentication Cookie:** For the team API endpoints, ensure that your cookie header is current and valid.

Install required Python packages (if not already installed):

```bash
pip install requests
```

## Pipeline Components

### Data Scraping

- **1PlayerScrape.py**  
  Retrieves player statistics from the AFL Fantasy players API.

- **2CoachScrape.py**  
  Retrieves coach statistics from the coach-specific API.

### Data Collation and Storage

- **5StatCollate.py**  
  Reads the player and coach JSON files and builds a structured SQLite database with dynamic stat columns.

### Derivative Metrics Calculation

- **7StatDerivatives.py**  
  Generates computed metrics like efficiency, consistency, trend, and cost-effectiveness.

### Team Stats Integration

- **9TeamStats.py**  
  Fetches team composition, applies pending trades, and queries the database for team-specific stats. Outputs to CSV and DB.

## Database Structure

- **6StatCollate.db**: Raw compiled player and coach stats
- **8StatAll.db**: Includes derivative calculations
- **10TeamStats.db**: Filtered records for your team
- **11TeamStats.csv**: Exported team metrics

## Usage Instructions

# AFL Fantasy Stats Pipeline 

A Python pipeline to scrape, process, and analyze AFL Fantasy player data. 

## Features
- Scrapes player and coach data
- Merges and processes raw stats into SQLite
- Computes derived statistics
- Extracts team-specific data into CSVs

## Project Structure
- `scripts/`: All functional pipeline scripts
- `data/`: Contains raw, interim, and final processed data
- `config/`: Configurable constants and paths
- `notebooks/`: Exploratory Jupyter Notebooks
- `tests/`: Unit tests

## Getting Started
1. Clone the repo:
    ```bash
    git clone https://github.com/yourusername/AFLFantasy.git
    cd AFLFantasy
    ```

2. Create virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the pipeline:
    ```bash
    python scripts/1PlayerScrape.py
    python scripts/2CoachScrape.py
    python scripts/5StatCollate.py
    python scripts/7DerivativeStats.py
    python scripts/9TeamStats.py
    ```

## To Do
- Add player projections model
- Integrate weather/contextual data
- Build web dashboard or CLI


## Code Structure Diagram

```
[1PlayerScrape.py]   [2CoachScrape.py]
         |                      |
         v                      v
   3Player.json           4Coach.json
             \           /
              \         /
               \       /
            [5StatCollate.py] 
               (Creates 6StatCollate.db)
                        |
                        v
            [7StatDerivatives.py]
             (Updates DB → 8StatAll.db)
                        |
                        v
             [9TeamStats.py] 
      (Queries 8StatAll.db with team info)
                        |
                        v
             [10TeamStats.db] & [11TeamStats.csv]
```

## Notes and Customization

- Scripts dynamically create columns based on detected rounds/stats in JSON.
- Cookie headers must be valid for authenticated team API access.
- Extensible via new scripts for additional analysis or visualization.

---

*End of README*