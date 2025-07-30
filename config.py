"""
Configuration file for City Layout Framework
Enhanced with district type system and chaos/order parameters
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
    'distance_fraction': 1.15,  # 115% of city radius
    'radius_fraction': 0.1,  # 10% of city radius
    'threshold_radius': 7.5,  # km - threshold for 2 vs 4 zones
}

# District centers per ring (min and max for interpolation)
DISTRICT_CENTERS = {
    'ring_1': {'min': 4, 'max': 8},
    'ring_2': {'min': 6, 'max': 10},
    'ring_3': {'min': 8, 'max': 12},
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
    'ring_1': 0.9,  # 90% district, 10% zone
    'ring_2': 0.8,  # 80% district, 20% zone
    'ring_3': 0.7,  # 70% district, 30% zone
    'outskirts': 0.5,  # 50% district, 50% zone
    'industrial': 0.0,  # 0% district, 100% zone
    'outside': 0.5,  # 50% district, 50% zone
    'default': 0.5  # Default if zone not found
}

# Chaos vs Order parameters
CHAOS_ORDER = {
    # Chaos factor by zone (0 = fully ordered grid, 1 = fully chaotic)
    'zone_chaos': {
        'historical_center': 1.0,  # Fully chaotic
        'ring_1': 0.95,  # Very chaotic
        'ring_2': 0.55,  # Mixed, more chaotic than ordered
        'ring_3': 0.15,  # Mixed, more ordered than chaotic
        'outskirts': 0.1,  # Almost ordered
        'outside': 0.0,  # Fully ordered
        'industrial': 0.0  # Fully ordered
    },

    # Grid spacing by zone (in km)
    'grid_spacing': {
        'historical_center': {'min': 0.010, 'max': 0.020},  # 10-20m (barely used)
        'ring_1': {'min': 0.010, 'max': 0.040},  # 10-40m
        'ring_2': {'min': 0.025, 'max': 0.075},  # 25-75m
        'ring_3': {'min': 0.050, 'max': 0.150},  # 50-150m
        'outskirts': {'min': 0.100, 'max': 0.200},  # 100-200m
        'outside': {'min': 0.150, 'max': 0.300},  # 150-300m
        'industrial': {'min': 0.050, 'max': 0.150}  # 50-150m
    },

    # Sigmoid transition parameters
    'transition_center': 0.65,  # Fraction of city radius where transition centers
    'transition_sharpness': 1.0,  # Higher = sharper transition (increase for clearer boundary)

    # Grid rotation parameters
    'max_grid_rotation': 45,  # Maximum degrees of rotation for local grids

    # Number of grid sectors for areas without districts
    'outskirts_grid_sectors': 13,  # Sectors in outskirts
    'outside_grid_sectors': 15,  # Sectors outside city
}

# Layout generation parameters
LAYOUT_PARAMS = {
    'boundary_buffer_fraction': 0.05,  # 5% of city radius buffer from boundaries
    'min_center_distance_fraction': 0.05,  # 5% minimum distance between centers
}

# Building generation parameters
BUILDING_GENERATION = {
    'center_density': 80,  # buildings per km² at city center
    'district_attractor_sigma': 0.05,  # sigma for district attractors (as fraction of city radius)
    'district_attractor_strength': 1.0,  # strength of district attractor boost (e.g. 1.0 = 100% boost)
    'district_influence_sigma': 0.1,  # sigma for district influence on building types

    # City-wide gaussian density parameters
    'density_sigma_factor': 0.5,  # Sigma as fraction of city radius (0.5 = city_radius is 2*sigma)
    'density_falloff_power': 0.5,  # Power for density falloff beyond city boundary (higher = sharper cutoff)
    'max_generation_radius': 1.15,  # Maximum radius for building generation as fraction of city radius

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
            'house': 0.05,
            'office': 0.20,
            'commercial': 0.30,
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
