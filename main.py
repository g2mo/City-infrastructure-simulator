"""
Main entry point for city layout generation
Updated to include building generation and chaos/order parameters

Author: Guglielmo Cimolai
Date: 30/07/2025
"""

import argparse
import webbrowser
import math
from pathlib import Path

from core import City, LayoutGenerator, BuildingGenerator
from visualization import CityVisualizer
from config import CITY_PARAMS, CHAOS_ORDER, BUILDING_GENERATION


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate city layout with buildings')
    parser.add_argument(
        '-r', '--radius',
        type=float,
        default=12.0,
        help=f"City radius in km (default: 12.0, min: {CITY_PARAMS['min_radius']}, "
             f"max: {CITY_PARAMS['max_radius']})"
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='city_layout.html',
        help='Output HTML filename (default: city_layout.html)'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically'
    )
    parser.add_argument(
        '--no-buildings',
        action='store_true',
        help='Generate only layout without buildings'
    )
    parser.add_argument(
        '--transition-center',
        type=float,
        default=None,
        help=f'Center of chaos-to-order transition as fraction of city radius '
             f'(default: {CHAOS_ORDER["transition_center"]})'
    )
    parser.add_argument(
        '--transition-sharpness',
        type=float,
        default=None,
        help=f'Sharpness of chaos-to-order transition, higher = sharper '
             f'(default: {CHAOS_ORDER["transition_sharpness"]})'
    )
    parser.add_argument(
        '--force-order',
        action='store_true',
        help='Force all zones to be fully ordered (for testing grid system)'
    )
    parser.add_argument(
        '--density-sigma',
        type=float,
        default=None,
        help=f'Gaussian density sigma as fraction of city radius '
             f'(default: {BUILDING_GENERATION["density_sigma_factor"]}). '
             f'0.5 means city radius = 2*sigma (95%% of buildings within city)'
    )
    parser.add_argument(
        '--density-falloff',
        type=float,
        default=None,
        help=f'Sharpness of density falloff beyond city boundary '
             f'(default: {BUILDING_GENERATION["density_falloff_power"]}). '
             f'Higher values create sharper cutoff'
    )

    args = parser.parse_args()

    # Validate radius
    if args.radius < CITY_PARAMS['min_radius'] or args.radius > CITY_PARAMS['max_radius']:
        print(f"Error: City radius must be between {CITY_PARAMS['min_radius']} "
              f"and {CITY_PARAMS['max_radius']} km")
        return 1

    # Update chaos/order parameters if provided
    if args.transition_center is not None:
        CHAOS_ORDER['transition_center'] = args.transition_center
        print(f"Using transition center: {args.transition_center}")

    if args.transition_sharpness is not None:
        CHAOS_ORDER['transition_sharpness'] = args.transition_sharpness
        print(f"Using transition sharpness: {args.transition_sharpness}")

    if args.force_order:
        print("Forcing fully ordered placement in all zones")
        for zone in CHAOS_ORDER['zone_chaos']:
            CHAOS_ORDER['zone_chaos'][zone] = 0.0

    if args.density_sigma is not None:
        BUILDING_GENERATION['density_sigma_factor'] = args.density_sigma
        print(f"Using density sigma factor: {args.density_sigma}")

    if args.density_falloff is not None:
        BUILDING_GENERATION['density_falloff_power'] = args.density_falloff
        print(f"Using density falloff power: {args.density_falloff}")

    print(f"Generating city layout with radius {args.radius} km...")

    # Generate city layout
    layout_generator = LayoutGenerator(args.radius)
    city = layout_generator.generate()

    # Generate buildings if requested
    if not args.no_buildings:
        building_generator = BuildingGenerator(city)
        building_generator.generate()

    # Print summary
    print(f"\nCity Generation Summary:")
    print(f"  - City Radius: {city.radius} km")
    print(f"  - Historical Center: {city.historical_center_radius:.2f} km")
    print(f"  - Number of Rings: {len(city.rings)}")
    for ring in city.rings:
        print(f"    - Ring {ring.ring_number}: {ring.inner_radius:.2f} - {ring.outer_radius:.2f} km "
              f"({len(ring.district_centers)} district centers)")
    print(f"  - Outskirts: {city.outskirts_inner_radius:.2f} - {city.outskirts_outer_radius:.2f} km")
    print(f"  - Industrial Zones: {len(city.industrial_zones)}")
    print(f"  - Total District Centers: {len(city.get_all_district_centers())}")

    if not args.no_buildings:
        print(f"\nBuilding Statistics:")
        for b_type in ['apartment', 'house', 'office', 'commercial', 'factory']:
            count = len(city.get_buildings_by_type(b_type))
            percentage = (count / len(city.buildings) * 100) if city.buildings else 0
            print(f"  - {b_type.capitalize()}: {count} ({percentage:.1f}%)")
        print(f"  - Total Buildings: {len(city.buildings)}")

        # Count buildings within city radius
        buildings_within = sum(1 for b in city.buildings if math.sqrt(b.x ** 2 + b.y ** 2) <= city.radius)
        buildings_outside = len(city.buildings) - buildings_within
        print(f"  - Within City Boundary: {buildings_within} ({buildings_within / len(city.buildings) * 100:.1f}%)")
        print(f"  - Outside City Boundary: {buildings_outside} ({buildings_outside / len(city.buildings) * 100:.1f}%)")

        print(f"\nChaos/Order System:")
        print(f"  - Grid Areas: {len(city.grid_areas)}")
        print(
            f"  - Transition Center: {CHAOS_ORDER['transition_center']} (at {CHAOS_ORDER['transition_center'] * city.radius:.1f} km)")
        print(f"  - Transition Sharpness: {CHAOS_ORDER['transition_sharpness']}")
        print(f"\nDensity Control:")
        print(
            f"  - Sigma Factor: {BUILDING_GENERATION['density_sigma_factor']} (city radius = {1 / BUILDING_GENERATION['density_sigma_factor']:.1f}σ)")
        print(f"  - ~95% of buildings within: {2 * BUILDING_GENERATION['density_sigma_factor'] * city.radius:.1f} km")
        print(f"  - Falloff Power: {BUILDING_GENERATION['density_falloff_power']}")

    # Create visualization
    print(f"\nCreating visualization...")
    visualizer = CityVisualizer(city)
    fig = visualizer.create_figure()

    # Save to file
    filepath = Path(args.output)
    fig.write_html(filepath, include_plotlyjs='cdn')
    print(f"Visualization saved to: {filepath.absolute()}")

    # Open in browser
    if not args.no_browser:
        print("Opening visualization in browser...")
        webbrowser.open(f'file://{filepath.absolute()}')

    print("\nDone!")
    print("\nVisualization Tips:")
    print("Toggle these layers in the legend to explore the city structure:")
    print("  - 'Grid Tessellation' - Shows the Voronoi-like grid regions")
    print("  - 'Grid Centers' - Shows the center points of each grid area")
    print("  - 'Chaos/Order Gradient' - Heatmap of the chaos-to-order transition")
    print("  - 'City Zones' - Traditional ring structure")
    print("\nTry zooming into the outskirts to see the grid alignment!")
    return 0


if __name__ == "__main__":
    exit(main())
