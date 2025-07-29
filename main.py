"""
Main entry point for city layout generation
Updated to include building generation

Author: Guglielmo Cimolai
Date: 29/07/2025
"""

import argparse
import webbrowser
from pathlib import Path

from core import City, LayoutGenerator, BuildingGenerator
from visualization import CityVisualizer
from config import CITY_PARAMS


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

    args = parser.parse_args()

    # Validate radius
    if args.radius < CITY_PARAMS['min_radius'] or args.radius > CITY_PARAMS['max_radius']:
        print(f"Error: City radius must be between {CITY_PARAMS['min_radius']} "
              f"and {CITY_PARAMS['max_radius']} km")
        return 1

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
    return 0


if __name__ == "__main__":
    exit(main())
