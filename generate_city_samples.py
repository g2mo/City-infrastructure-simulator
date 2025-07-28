"""
Test script to generate and visualize cities of various sizes using matplotlib
Generates 5 random cities for each radius from 1-15 km (75 cities total)
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Wedge
import matplotlib.patches as mpatches
from pathlib import Path
import os

from core import LayoutGenerator


def plot_city_layout(ax, city, title):
    """Plot city layout using matplotlib"""
    # Set equal aspect ratio
    ax.set_aspect('equal')

    # Plot city boundary
    city_circle = Circle((0, 0), city.radius, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(city_circle)

    # Plot historical center
    hist_circle = Circle((0, 0), city.historical_center_radius,
                         fill=True, facecolor='darkred', alpha=0.3, edgecolor='darkred')
    ax.add_patch(hist_circle)

    # Plot rings
    colors = ['blue', 'green', 'orange']
    for i, ring in enumerate(city.rings):
        # Create annulus using Wedge
        annulus = Wedge((0, 0), ring.outer_radius, 0, 360,
                        width=ring.outer_radius - ring.inner_radius,
                        facecolor=colors[i % len(colors)], alpha=0.2,
                        edgecolor=colors[i % len(colors)])
        ax.add_patch(annulus)

    # Plot outskirts
    outskirts = Wedge((0, 0), city.outskirts_outer_radius, 0, 360,
                      width=city.outskirts_outer_radius - city.outskirts_inner_radius,
                      facecolor='gray', alpha=0.1, edgecolor='gray', linestyle='--')
    ax.add_patch(outskirts)

    # Plot industrial zones
    for zone in city.industrial_zones:
        ind_circle = Circle((zone.x, zone.y), zone.radius,
                            fill=True, facecolor='brown', alpha=0.4, edgecolor='brown')
        ax.add_patch(ind_circle)
        ax.text(zone.x, zone.y, zone.direction, ha='center', va='center',
                fontweight='bold', fontsize=8)

    # Plot buildings if they exist
    if hasattr(city, 'buildings') and city.buildings:
        building_colors = {
            'apartment': '#4169E1',
            'house': '#32CD32',
            'office': '#FF8C00',
            'commercial': '#DC143C',
            'factory': '#8B4513'
        }

        for b_type, color in building_colors.items():
            buildings = city.get_buildings_by_type(b_type)
            if buildings:
                x_coords = [b.x for b in buildings]
                y_coords = [b.y for b in buildings]
                ax.scatter(x_coords, y_coords, color=color, s=1, alpha=0.6, label=b_type)

    # Plot district centers
    for ring in city.rings:
        if ring.district_centers:
            x_coords = [c.x for c in ring.district_centers]
            y_coords = [c.y for c in ring.district_centers]
            ax.scatter(x_coords, y_coords, color='red',
                       s=30, marker='*', edgecolor='black', linewidth=0.5, zorder=10)

    # Set limits
    bounds = city.get_bounds()
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])

    # Add grid
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)

    # Labels
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Distance (km)')
    ax.set_title(title, fontsize=10, pad=10)


def generate_single_city_plot(radius, iteration, output_dir):
    """Generate and save a single city plot"""
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8))

    # Generate city with buildings
    from core import BuildingGenerator
    generator = LayoutGenerator(radius)
    city = generator.generate()

    # Generate buildings
    building_gen = BuildingGenerator(city)
    building_gen.generate()

    # Plot city
    plot_city_layout(ax, city,
                     f'City Radius: {radius} km - Instance {iteration + 1}\n'
                     f'Buildings: {len(city.buildings)} | '
                     f'Centers: {len(city.get_all_district_centers())}')

    # Save
    filename = f'city_r{radius:02d}_v{iteration + 1}.png'
    filepath = output_dir / filename
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    return city


def create_summary_grid(radius, cities, output_dir):
    """Create a summary grid showing all 5 variations for a given radius"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, city in enumerate(cities):
        if i < 5:  # Only plot first 5
            plot_city_layout(axes[i], city, f'Instance {i + 1}')

    # Hide the 6th subplot
    axes[5].set_visible(False)

    # Overall title
    fig.suptitle(f'City Variations - Radius: {radius} km', fontsize=16, fontweight='bold')

    plt.tight_layout()

    # Save summary
    filename = f'city_r{radius:02d}_summary.png'
    filepath = output_dir / filename
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()


def create_size_comparison():
    """Create a comparison showing one city of each size"""
    fig, axes = plt.subplots(3, 5, figsize=(20, 12))
    axes = axes.flatten()

    for i, radius in enumerate(range(1, 16)):
        # Generate one city for each radius
        generator = LayoutGenerator(radius)
        city = generator.generate()

        # Plot
        plot_city_layout(axes[i], city, f'{radius} km')

    fig.suptitle('City Size Comparison (1-15 km radius)', fontsize=20, fontweight='bold')
    plt.tight_layout()

    # Save
    output_dir = Path('city_visualizations')
    filepath = output_dir / 'city_size_comparison.png'
    plt.savefig(filepath, dpi=200, bbox_inches='tight')
    plt.close()


def main():
    """Generate and plot multiple random cities for each radius"""
    # Create output directory
    output_dir = Path('city_visualizations')
    output_dir.mkdir(exist_ok=True)

    # Create subdirectories for each radius
    for radius in range(1, 16):
        radius_dir = output_dir / f'radius_{radius:02d}km'
        radius_dir.mkdir(exist_ok=True)

    print("Generating city visualizations...")
    print("=" * 50)

    # Generate cities
    total_cities = 0
    city_sizes = list(range(1, 16))  # 1 to 15 km
    cities_per_radius = 5

    for radius in city_sizes:
        print(f"\nGenerating cities with radius {radius} km...")
        radius_dir = output_dir / f'radius_{radius:02d}km'

        cities = []
        for iteration in range(cities_per_radius):
            city = generate_single_city_plot(radius, iteration, radius_dir)
            cities.append(city)
            total_cities += 1
            print(f"  - Generated city {iteration + 1}/{cities_per_radius}")

        # Create summary grid for this radius
        create_summary_grid(radius, cities, radius_dir)
        print(f"  - Created summary grid for {radius} km cities")

    # Create overall size comparison
    print("\nCreating size comparison chart...")
    create_size_comparison()

    # Create a master summary showing statistics
    print("\nCreating statistics summary...")
    create_statistics_summary(city_sizes, cities_per_radius, output_dir)

    print("\n" + "=" * 50)
    print(f"✓ Generated {total_cities} city visualizations!")
    print(f"✓ Output saved in: {output_dir.absolute()}")
    print("\nFolder structure:")
    print("  city_visualizations/")
    print("    ├── city_size_comparison.png")
    print("    ├── statistics_summary.png")
    for radius in range(1, 16):
        print(f"    ├── radius_{radius:02d}km/")
        print(f"    │   ├── city_r{radius:02d}_v1.png to city_r{radius:02d}_v5.png")
        print(f"    │   └── city_r{radius:02d}_summary.png")


def create_statistics_summary(city_sizes, cities_per_radius, output_dir):
    """Create a summary chart showing statistics across all city sizes"""
    # Collect statistics
    stats = {
        'radius': [],
        'avg_centers': [],
        'min_centers': [],
        'max_centers': [],
        'num_rings': [],
        'num_industrial': []
    }

    for radius in city_sizes:
        centers_count = []
        num_rings = 0
        num_industrial = 0

        # Generate a few cities to get statistics
        for _ in range(10):
            generator = LayoutGenerator(radius)
            city = generator.generate()
            centers_count.append(len(city.get_all_district_centers()))
            num_rings = len(city.rings)
            num_industrial = len(city.industrial_zones)

        stats['radius'].append(radius)
        stats['avg_centers'].append(np.mean(centers_count))
        stats['min_centers'].append(np.min(centers_count))
        stats['max_centers'].append(np.max(centers_count))
        stats['num_rings'].append(num_rings)
        stats['num_industrial'].append(num_industrial)

    # Create plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

    # District centers plot
    ax1.plot(stats['radius'], stats['avg_centers'], 'b-', linewidth=2, label='Average')
    ax1.fill_between(stats['radius'], stats['min_centers'], stats['max_centers'],
                     alpha=0.3, label='Range')
    ax1.set_xlabel('City Radius (km)')
    ax1.set_ylabel('Number of District Centers')
    ax1.set_title('District Centers vs City Size')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Rings plot
    ax2.step(stats['radius'], stats['num_rings'], 'g-', linewidth=2, where='post')
    ax2.set_xlabel('City Radius (km)')
    ax2.set_ylabel('Number of Rings')
    ax2.set_title('Ring System vs City Size')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 4)

    # Industrial zones plot
    ax3.step(stats['radius'], stats['num_industrial'], 'r-', linewidth=2, where='post')
    ax3.set_xlabel('City Radius (km)')
    ax3.set_ylabel('Number of Industrial Zones')
    ax3.set_title('Industrial Zones vs City Size')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 5)

    # City area plot
    areas = [np.pi * r ** 2 for r in stats['radius']]
    ax4.plot(stats['radius'], areas, 'm-', linewidth=2)
    ax4.set_xlabel('City Radius (km)')
    ax4.set_ylabel('City Area (km²)')
    ax4.set_title('City Area vs Radius')
    ax4.grid(True, alpha=0.3)

    fig.suptitle('City Generation Statistics Summary', fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save
    filepath = output_dir / 'statistics_summary.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    main()
