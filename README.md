# ASOS Inventory Analytics Dashboard

An interactive analytics dashboard built using Python, Pandas, Plotly, and Streamlit to analyze ASOS product inventory and identify revenue losses caused by stockouts.

## Overview

Fashion e-commerce platforms often lose potential revenue when popular products go out of stock. This project analyzes ASOS product data to estimate stockout-driven revenue loss and identify brands that may require better inventory planning.

The dashboard transforms raw product listings into actionable business insights through data cleaning, feature engineering, and interactive visualizations.

## Features

* Interactive Streamlit dashboard
* Brand-wise inventory analysis
* Stockout rate calculation across product sizes
* Estimated lost revenue due to unavailable inventory
* Dynamic filtering by brand and price range
* Brand strategy visualization using pricing and demand indicators
* Revenue impact analysis of stockouts
* Product-level ranking of inventory risks

## Data Processing

The raw dataset was cleaned and transformed using Pandas:

* Removed invalid and missing price records
* Extracted brand information from product descriptions
* Standardized inconsistent brand names
* Filtered low-frequency brands to improve analysis quality
* Computed stockout counts and stockout rates
* Estimated lost revenue using stockout information and product pricing

## Key Insights

* Several premium brands exhibit both high prices and high stockout rates, indicating strong customer demand.
* A significant portion of potential revenue is lost due to inventory shortages.
* Certain brands consistently experience higher stockout levels and may benefit from improved replenishment strategies.
* Price tier analysis reveals differences in stockout behavior across product categories.

## Tech Stack

* Python
* Pandas
* Plotly
* Streamlit

## Dashboard Components

1. KPI Summary Cards
2. Brand Strategy Map
3. Top Revenue-Loss Brands
4. Stockout Distribution Analysis
5. Price Tier vs Stockout Heatmap
6. Product-Level Revenue Loss Table

## Run Locally

```bash
pip install -r requirements.txt
streamlit run asos_dashboard.py
```

## Live Demo

https://asos-dashboard.streamlit.app/

## Author

Abheeshta Saddhanapu

