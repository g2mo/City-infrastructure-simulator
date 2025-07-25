"""
Configuration file for City Layout Framework
Simplified for sequential boundary generation
"""

# City size parameters
CITY_PARAMS = {
    'min_radius': 1.0,  # km
    'max_radius': 15.0,  # km
}

# Historical center parameters (as fraction of city radius)
HISTORICAL_CENTER = {
    'min_radius_fraction': 0.10,  # 10% of city radius
    'max_radius_fraction': 0.20,  # 20% of city radius
}

# Ring system parameters
RING_SYSTEM = {
    'end_fraction': 0.70,  # Ring system ends at ~70% of city radius
    'end_variation': 0.10,  # 5% variation (so 60-80% range)
}

# Note: Outskirts automatically fill from ring system end to city boundary (100%)
# No configuration needed since it's determined by ring system end

# Industrial zones parameters
INDUSTRIAL_ZONES = {
    'distance_fraction': 1.20,  # 120% of city radius
    'radius_fraction': 0.10,    # 10% of city radius
    'threshold_radius': 7.5,    # km - threshold for 2 vs 4 zones
}

# District centers per ring (min and max for interpolation)
# Values are for city radius 1km (min) to 15km (max)
DISTRICT_CENTERS = {
    'ring_1': {'min': 6, 'max': 10},
    'ring_2': {'min': 8, 'max': 14},
    'ring_3': {'min': 10, 'max': 18},
}

# Layout generation parameters
LAYOUT_PARAMS = {
    'boundary_buffer_fraction': 0.05,  # 5% of city radius buffer from boundaries
    'min_center_distance_fraction': 0.05,  # 5% minimum distance between centers
}

# Visualization parameters
VISUALIZATION = {
    'colors': {
        'city_boundary': 'black',
        'historical_center': 'darkred',
        'ring_1': 'darkblue',
        'ring_2': 'darkgreen',
        'ring_3': 'darkorange',
        'outskirts': 'gray',
        'industrial': 'brown',
        'district_center': 'red',
    },
    'sizes': {
        'district_center': 8,
        'industrial_center': 10,
    }
}
