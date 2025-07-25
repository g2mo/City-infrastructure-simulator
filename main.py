"""
Main entry point for city layout generation
"""

import argparse
import webbrowser
from pathlib import Path

from core import City, LayoutGenerator
from visualization import CityVisualizer
from config import CITY_PARAMS


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate city layout')
    parser.add_argument(
        '-r', '--radius',
        type=float,
        default=10.0,
        help=f"City radius in km (default: 10.0, min: {CITY_PARAMS['min_radius']}, "
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

    args = parser.parse_args()

    # Validate radius
    if args.radius < CITY_PARAMS['min_radius'] or args.radius > CITY_PARAMS['max_radius']:
        print(f"Error: City radius must be between {CITY_PARAMS['min_radius']} "
              f"and {CITY_PARAMS['max_radius']} km")
        return 1

    print(f"Generating city layout with radius {args.radius} km...")

    # Generate city
    generator = LayoutGenerator(args.radius)
    city = generator.generate()

    # Print summary
    print(f"\nCity Layout Summary:")
    print(f"  - Historical Center Radius: {city.historical_center_radius:.2f} km")
    print(f"  - Number of Rings: {len(city.rings)}")
    for ring in city.rings:
        print(f"    - Ring {ring.ring_number}: {ring.inner_radius:.2f} - {ring.outer_radius:.2f} km "
              f"({len(ring.district_centers)} district centers)")
    print(f"  - Outskirts: {city.outskirts_inner_radius:.2f} - {city.outskirts_outer_radius:.2f} km")
    print(f"  - Industrial Zones: {len(city.industrial_zones)}")
    print(f"  - Total District Centers: {len(city.get_all_district_centers())}")

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
