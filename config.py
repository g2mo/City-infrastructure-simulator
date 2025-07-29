"""
Configuration file for City Layout Framework
Enhanced with district type system
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
    'end_fraction': 0.65,  # Ring system ends at ~65% of city radius
    'end_variation': 0.05,  # ±5% variation (so 60-70% range)
}

# Industrial zones parameters
INDUSTRIAL_ZONES = {
    'distance_fraction': 1.20,  # 120% of city radius
    'radius_fraction': 0.1,  # 10% of city radius
    'threshold_radius': 7.5,  # km - threshold for 2 vs 4 zones
}

# District centers per ring (min and max for interpolation)
DISTRICT_CENTERS = {
    'ring_1': {'min': 6, 'max': 10},
    'ring_2': {'min': 8, 'max': 14},
    'ring_3': {'min': 10, 'max': 18},
}

# District type distribution by ring
DISTRICT_TYPE_DISTRIBUTION = {
    'ring_1': {
        'residential': 0.2,
        'commercial': 0.6,
        'mixed': 0.2
    },
    'ring_2': {
        'residential': 0.3,
        'commercial': 0.3,
        'mixed': 0.4
    },
    'ring_3': {
        'residential': 0.6,
        'commercial': 0.2,
        'mixed': 0.2
    }
}

# Building probabilities by district type
DISTRICT_BUILDING_PROBABILITIES = {
    'residential': {
        'apartment': 0.60,
        'house': 0.20,
        'office': 0.05,
        'commercial': 0.15,
        'factory': 0.0
    },
    'commercial': {
        'apartment': 0.10,
        'house': 0.0,
        'office': 0.40,
        'commercial': 0.50,
        'factory': 0.0
    },
    'mixed': {
        'apartment': 0.35,
        'house': 0.10,
        'office': 0.25,
        'commercial': 0.30,
        'factory': 0.0
    }
}

# District influence strength by zone (how much districts override zone probabilities)
DISTRICT_INFLUENCE_STRENGTH = {
    'historical_center': 0.0,  # 0% district, 100% zone
    'ring_1': 0.4,  # 40% district, 60% zone
    'ring_2': 0.6,  # 60% district, 40% zone
    'ring_3': 0.8,  # 80% district, 20% zone
    'outskirts': 0.5,  # 50% district, 50% zone
    'industrial': 0.0,  # 0% district, 100% zone
    'outside': 0.5,  # 50% district, 50% zone
    'default': 0.5  # Default if zone not found
}

# Layout generation parameters
LAYOUT_PARAMS = {
    'boundary_buffer_fraction': 0.04,  # 4% of city radius buffer from boundaries
    'min_center_distance_fraction': 0.04,  # 4% minimum distance between centers
}

# Building generation parameters
BUILDING_GENERATION = {
    'center_density': 100,  # buildings per km² at city center
    'district_attractor_sigma': 0.05,  # sigma for district attractors (as fraction of city radius)
    'district_attractor_strength': 0.3,  # strength of district attractor boost (0.3 = 30% boost)
    'district_influence_sigma': 0.1,  # sigma for district influence on building types

    # Building type probabilities by zone
    'zone_probabilities': {
        'historical_center': {
            'apartment': 0.15,
            'house': 0.0,
            'office': 0.40,
            'commercial': 0.45,
            'factory': 0.0
        },
        'ring_1': {  # Inner ring
            'apartment': 0.35,
            'house': 0.0,
            'office': 0.30,
            'commercial': 0.35,
            'factory': 0.0
        },
        'ring_2': {  # Middle ring
            'apartment': 0.45,
            'house': 0.0,
            'office': 0.20,
            'commercial': 0.35,
            'factory': 0.0
        },
        'ring_3': {  # Outer ring
            'apartment': 0.40,
            'house': 0.15,
            'office': 0.15,
            'commercial': 0.30,
            'factory': 0.0
        },
        'outskirts': {
            'apartment': 0.10,
            'house': 0.60,
            'office': 0.10,
            'commercial': 0.20,
            'factory': 0.0
        },
        'industrial': {
            'apartment': 0.0,
            'house': 0.0,
            'office': 0.15,
            'commercial': 0.0,
            'factory': 0.85
        },
        'outside': {  # Beyond city boundary
            'apartment': 0.05,
            'house': 0.70,
            'office': 0.05,
            'commercial': 0.20,
            'factory': 0.0
        }
    }
}

# Building colors for visualization
BUILDING_COLORS = {
    'apartment': '#4169E1',  # Royal Blue
    'house': '#32CD32',  # Lime Green
    'office': '#FF8C00',  # Dark Orange
    'commercial': '#DC143C',  # Crimson
    'factory': '#8B4513'  # Saddle Brown
}

# District colors by type
DISTRICT_COLORS = {
    'residential': '#228B22',  # Forest Green
    'commercial': '#4B0082',  # Indigo
    'mixed': '#FF1493'  # Deep Pink
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
        'district_center': 12,
        'industrial_center': 10,
        'building': 3,
    }
}
