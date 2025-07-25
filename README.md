# City Layout Generator

A Python tool for generating and visualizing procedural city layouts with realistic urban zones.

## Overview

This project generates city layouts with the following features:
- **Historical center** - Central old town area (10-20% of city radius)
- **Ring system** - 1-3 concentric rings around the center (based on city size)
- **Outskirts** - Outer residential areas
- **Industrial zones** - Located outside the city (2 or 4 zones depending on size)
- **District centers** - Service hubs distributed throughout each ring

## City Size Rules

- **1-4 km radius**: 1 ring, 2 industrial zones
- **5-9 km radius**: 2 rings, 2 industrial zones  
- **10-15 km radius**: 3 rings, 4 industrial zones

Larger cities have more district centers per ring.

<img width="990" height="590" alt="city_size_comparison" src="https://github.com/user-attachments/assets/c5b0fcc9-d854-46bb-939f-1c403964327c" />

## Requirements

- Python 3.6+
- matplotlib
- plotly
- numpy

## Usage

### Generate a Single City

```bash
python main.py -r 10 -o my_city.html
```

Options:
- `-r, --radius`: City radius in km (1-15, default: 10)
- `-o, --output`: Output HTML filename (default: city_layout.html)
- `--no-browser`: Don't auto-open the visualization

### Generate Multiple Sample Cities

```bash
python generate_city_samples.py
```

This creates 75 city visualizations (5 variations for each radius from 1-15 km) in the `city_visualizations/` folder.

## Project Structure

- `core/` - Core city models and layout generation logic
  - `city.py` - City data structures
  - `layout.py` - Layout generation algorithm
- `visualization/` - Visualization modules
  - `plotly_viz.py` - Interactive Plotly visualizations
- `config.py` - Configuration parameters for city generation
- `main.py` - Single city generation entry point
- `generate_city_samples.py` - Batch city generation with matplotlib
