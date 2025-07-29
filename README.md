# City Infrastructure Generator

A sophisticated urban layout generator that creates realistic city structures using gaussian field-based algorithms and district influence systems. The generator produces organic city layouts with buildings distributed according to configurable zones and district types.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Examples](#examples)
- [API Reference](#api-reference)

## Overview

This project generates procedural cities with realistic layouts inspired by European urban development patterns. Unlike grid-based city generators, this system uses gaussian density fields and district attractors to create organic, naturally-flowing city structures.

### Key Concepts
- **Gaussian Density Fields**: Building placement follows a gaussian distribution centered at the city center
- **District Attractors**: Each district acts as a local density attractor with typed influence (residential/commercial/mixed)
- **Seamless Zones**: City zones (historical center, rings, outskirts) transition smoothly without gaps
- **Organic Placement**: Buildings are placed chaotically with minimum distance constraints, avoiding grid patterns

## Features

### 🏙️ City Structure
- **Historical Center**: Dense, mixed-use core (10-20% of city radius)
- **Ring System**: 1-3 concentric rings based on city size
- **Outskirts**: Low-density residential areas
- **Industrial Zones**: Peripheral manufacturing districts

### 🏢 Building Types
- **Residential**: Apartments and houses
- **Commercial**: Retail stores and shops
- **Office**: Business and administrative buildings
- **Industrial**: Factories and warehouses
- **Mixed**: Combination of uses

### 🎯 District System
- **Typed Districts**: Residential, commercial, or mixed-use
- **Gaussian Influence**: Soft boundaries with overlapping effects
- **Weighted Blending**: Building types influenced by multiple districts

### 📊 Visualization
- **Interactive Plotly Dashboard**: Zoom, pan, and hover for details
- **Toggleable Layers**: Show/hide zones, buildings, districts
- **Building Filtering**: Toggle individual building types
- **District Information**: Type and influence visualization

## Installation

### Requirements
- Python 3.8+
- NumPy
- Plotly
- NetworkX

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd city-infrastructure-generator

# Install dependencies
pip install numpy plotly networkx

# Run the generator
python main.py
```

## Quick Start

### Generate a Default City
```bash
python main.py
```

### Custom City Sizes
```bash
# Small town (3km radius)
python main.py -r 3

# Medium city (7km radius)
python main.py -r 7

# Large metropolis (12km radius)
python main.py -r 12
```

### Advanced Options
```bash
# Generate without buildings (layout only)
python main.py -r 10 --no-buildings

# Save to custom file
python main.py -r 8 -o my_city.html

# Don't open browser
python main.py -r 5 --no-browser
```

### Batch Generation
```bash
# Generate sample cities of all sizes
python generate_city_samples.py
```

## Architecture

### Project Structure
```
city-infrastructure-generator/
├── config.py                 # All configuration parameters
├── core/
│   ├── __init__.py
│   ├── city.py              # City, Building, District models
│   ├── layout.py            # Layout generation logic
│   └── building_generator.py # Building placement algorithms
├── visualization/
│   ├── __init__.py
│   └── plotly_viz.py        # Interactive visualization
├── main.py                  # CLI interface
└── generate_city_samples.py # Batch generation tool
```

### Core Components

#### City Model
- **City**: Container for all urban elements
- **Building**: Individual structure with type and location
- **DistrictCenter**: Typed attractor with gaussian influence
- **Ring**: Annular zone containing districts
- **IndustrialZone**: Special peripheral zones

#### Algorithms
- **LayoutGenerator**: Creates city structure and districts
- **BuildingGenerator**: Places buildings using density fields
- **CityVisualizer**: Renders interactive visualizations

## Configuration

### Key Parameters in `config.py`

#### City Structure
```python
HISTORICAL_CENTER = {
    'min_radius_fraction': 0.10,  # 10% of city radius
    'max_radius_fraction': 0.20,  # 20% of city radius
}

RING_SYSTEM = {
    'end_fraction': 0.65,     # Rings end at 65% of radius
    'end_variation': 0.05,    # ±5% random variation
}
```

#### District Distribution
```python
DISTRICT_TYPE_DISTRIBUTION = {
    'ring_1': {
        'residential': 0.2,
        'commercial': 0.4,
        'mixed': 0.4
    },
    'ring_2': {
        'residential': 0.3,
        'commercial': 0.3,
        'mixed': 0.4
    },
    'ring_3': {
        'residential': 0.5,
        'commercial': 0.2,
        'mixed': 0.3
    }
}
```

#### Building Generation
```python
BUILDING_GENERATION = {
    'center_density': 100,  # buildings/km² at center
    'district_attractor_sigma': 0.05,  # relative to city radius
    'district_attractor_strength': 0.3,  # 30% density boost
    'district_influence_sigma': 0.1,  # influence spread
}
```

#### District Influence Strength
```python
DISTRICT_INFLUENCE_STRENGTH = {
    'historical_center': 0.3,  # 30% district, 70% zone
    'ring_1': 0.6,            # 60% district, 40% zone
    'ring_2': 0.7,            # 70% district, 30% zone
    'ring_3': 0.8,            # 80% district, 20% zone
    'outskirts': 0.5,         # 50% district, 50% zone
}
```

## Examples

### Small Town (3km radius)
- 1 ring system
- ~300 buildings
- 2 industrial zones
- Focus on residential

### Medium City (7km radius)
- 2 ring system
- ~1,500 buildings
- 2 industrial zones
- Balanced mixed-use

### Large Metropolis (12km radius)
- 3 ring system
- ~4,500 buildings
- 4 industrial zones
- Complex district interactions

### Design Decisions

#### Why Gaussian Fields?
- Natural density falloff from center
- Smooth transitions between zones
- Realistic clustering patterns
- Mathematically elegant

#### Why District Types?
- Creates realistic neighborhoods
- Enables mixed-use development
- Provides local character
- Influences building distribution

#### Why Organic Placement?
- Avoids unrealistic grid patterns
- Simulates historical growth
- Creates visual interest
- More European-style

## API Reference

### Core Classes

#### LayoutGenerator
```python
generator = LayoutGenerator(city_radius: float)
city = generator.generate() -> City
```

#### BuildingGenerator
```python
generator = BuildingGenerator(city: City)
generator.generate() -> None  # Modifies city in-place
```

#### CityVisualizer
```python
viz = CityVisualizer(city: City)
fig = viz.create_figure() -> plotly.graph_objects.Figure
```

### City Methods
```python
city.add_building(building: Building)
city.get_zone_at_position(x: float, y: float) -> str
city.get_all_district_centers() -> List[DistrictCenter]
city.get_buildings_by_type(building_type: str) -> List[Building]
city.get_district_by_id(district_id: int) -> DistrictCenter
```
