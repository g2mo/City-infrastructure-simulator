"""
Building generation module - creates buildings based on gaussian density
Updated to include district type influences and chaos/order grid system
"""

import math
import random
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

from core.city import City, Building, GridArea
from config import (
    BUILDING_GENERATION,
    BUILDING_COLORS,
    DISTRICT_BUILDING_PROBABILITIES,
    DISTRICT_INFLUENCE_STRENGTH,
    CHAOS_ORDER
)


class BuildingGenerator:
    """Generates buildings for a city using gaussian density distribution with chaos/order system"""

    def __init__(self, city: City):
        """Initialize generator with a city"""
        self.city = city
        self.next_building_id = 0
        self.min_building_distance = 0.005  # 5 meters in km

        # Calculate gaussian parameters using configurable sigma
        self.sigma_factor = BUILDING_GENERATION['density_sigma_factor']
        self.sigma = city.radius * self.sigma_factor  # Now city radius = 2*sigma when factor = 0.5
        self.center_density = BUILDING_GENERATION['center_density']  # buildings per km²
        self.density_falloff_power = BUILDING_GENERATION['density_falloff_power']
        self.max_generation_radius = BUILDING_GENERATION['max_generation_radius']

        # Zone probabilities for building types
        self.zone_probabilities = BUILDING_GENERATION['zone_probabilities']

        # Generate grid areas
        self.grid_areas = self._generate_grid_areas()
        # Store grid areas in city for visualization
        self.city.set_grid_areas(self.grid_areas)

    def generate(self) -> None:
        """Generate all buildings for the city"""
        print(f"Generating buildings for city with radius {self.city.radius} km...")

        # Generate candidate positions based on density
        positions, placement_stats = self._generate_building_positions()

        # Assign building types and create buildings
        for x, y in positions:
            zone = self.city.get_zone_at_position(x, y)

            # Calculate district influences
            district_influences = self._calculate_district_influences(x, y)

            # Select building type based on zone and district influences
            building_type = self._select_building_type(zone, district_influences)

            if building_type:  # Only create if valid type for zone
                # Find primary district (strongest influence)
                primary_district = -1
                if district_influences:
                    primary_district = max(district_influences.items(), key=lambda x: x[1])[0]

                building = Building(
                    id=self.next_building_id,
                    x=x,
                    y=y,
                    building_type=building_type,
                    zone=zone,
                    primary_district=primary_district,
                    district_influences=district_influences
                )
                self.city.add_building(building)
                self.next_building_id += 1

        print(f"Generated {len(self.city.buildings)} buildings")
        print(
            f"  - Grid-aligned: {placement_stats['grid']} ({placement_stats['grid'] / max(1, placement_stats['total']) * 100:.1f}%)")
        print(
            f"  - Chaotic: {placement_stats['chaotic']} ({placement_stats['chaotic'] / max(1, placement_stats['total']) * 100:.1f}%)")

    def _generate_grid_areas(self) -> List[GridArea]:
        """Generate grid areas for the city"""
        grid_areas = []
        grid_id = 0

        # Create grids for each district in rings (but only for less chaotic areas)
        for district in self.city.get_all_district_centers():
            zone = f"ring_{district.ring}" if district.ring > 0 else "historical_center"

            # Skip grids for very chaotic areas
            if zone in ['historical_center'] or CHAOS_ORDER['zone_chaos'].get(zone, 1.0) > 0.8:
                continue

            # Random rotation for variety
            rotation = random.uniform(-CHAOS_ORDER['max_grid_rotation'],
                                      CHAOS_ORDER['max_grid_rotation']) * math.pi / 180

            # Get spacing for this zone
            spacing_range = CHAOS_ORDER['grid_spacing'].get(zone, {'min': 0.05, 'max': 0.08})
            spacing = random.uniform(spacing_range['min'], spacing_range['max'])

            grid_areas.append(GridArea(
                id=grid_id,
                center_x=district.x,
                center_y=district.y,
                rotation=rotation,
                spacing=spacing,
                zone=zone
            ))
            grid_id += 1

        # Create grid sectors for outskirts (single layer, larger sectors)
        num_outskirts_sectors = CHAOS_ORDER['outskirts_grid_sectors']

        for i in range(num_outskirts_sectors):
            angle = (2 * math.pi * i) / num_outskirts_sectors
            # Place at middle of outskirts
            radius = (self.city.outskirts_inner_radius + self.city.outskirts_outer_radius) / 2

            rotation = random.uniform(-CHAOS_ORDER['max_grid_rotation'],
                                      CHAOS_ORDER['max_grid_rotation']) * math.pi / 180
            spacing_range = CHAOS_ORDER['grid_spacing']['outskirts']
            spacing = random.uniform(spacing_range['min'], spacing_range['max'])

            grid_areas.append(GridArea(
                id=grid_id,
                center_x=radius * math.cos(angle),
                center_y=radius * math.sin(angle),
                rotation=rotation,
                spacing=spacing,
                zone='outskirts'
            ))
            grid_id += 1

        # Create grid sectors for outside areas (single layer, larger sectors)
        num_outside_sectors = CHAOS_ORDER['outside_grid_sectors']

        for i in range(num_outside_sectors):
            angle = (2 * math.pi * i) / num_outside_sectors
            # Place just beyond city boundary (105% instead of 115%)
            radius = self.city.radius * 1.05

            rotation = random.uniform(-CHAOS_ORDER['max_grid_rotation'],
                                      CHAOS_ORDER['max_grid_rotation']) * math.pi / 180
            spacing_range = CHAOS_ORDER['grid_spacing']['outside']
            spacing = random.uniform(spacing_range['min'], spacing_range['max'])

            grid_areas.append(GridArea(
                id=grid_id,
                center_x=radius * math.cos(angle),
                center_y=radius * math.sin(angle),
                rotation=rotation,
                spacing=spacing,
                zone='outside'
            ))
            grid_id += 1

        # Create grids for industrial zones
        for iz in self.city.industrial_zones:
            rotation = random.uniform(-CHAOS_ORDER['max_grid_rotation'],
                                      CHAOS_ORDER['max_grid_rotation']) * math.pi / 180
            spacing_range = CHAOS_ORDER['grid_spacing']['industrial']
            spacing = random.uniform(spacing_range['min'], spacing_range['max'])

            grid_areas.append(GridArea(
                id=grid_id,
                center_x=iz.x,
                center_y=iz.y,
                rotation=rotation,
                spacing=spacing,
                zone='industrial'
            ))
            grid_id += 1

        return grid_areas

    def _calculate_chaos_factor(self, x: float, y: float) -> float:
        """Calculate chaos factor at a position using sigmoid transition"""
        distance_from_center = math.sqrt(x ** 2 + y ** 2)
        normalized_distance = distance_from_center / self.city.radius

        # Sigmoid function centered at transition point
        center = CHAOS_ORDER['transition_center']
        sharpness = CHAOS_ORDER['transition_sharpness']

        # Sigmoid: 1 / (1 + exp(sharpness * (x - center)))
        # This gives 1 (chaotic) at center and 0 (ordered) at edge
        chaos_factor = 1 / (1 + math.exp(sharpness * (normalized_distance - center)))

        return chaos_factor

    def _find_nearest_grid_area(self, x: float, y: float) -> Optional[GridArea]:
        """Find the nearest grid area to a position using simple nearest neighbor"""
        if not self.grid_areas:
            return None

        min_distance = float('inf')
        nearest_grid = None

        for grid in self.grid_areas:
            distance = math.sqrt((x - grid.center_x) ** 2 + (y - grid.center_y) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_grid = grid

        return nearest_grid

    def _generate_building_positions(self) -> List[Tuple[float, float]]:
        """Generate building positions based on gaussian density with chaos/order system"""
        positions = []

        # Define sampling area (limited by max_generation_radius)
        max_radius = self.city.radius * self.max_generation_radius

        # Create grid for sampling
        grid_resolution = int(max_radius * 50)  # ~50 points per km (increased from 40)
        x_points = np.linspace(-max_radius, max_radius, grid_resolution)
        y_points = np.linspace(-max_radius, max_radius, grid_resolution)

        # Track occupied positions for minimum distance
        occupied = []

        # Track placement statistics
        placement_stats = {
            'chaotic': 0,
            'grid': 0,
            'total': 0
        }

        for x in x_points:
            for y in y_points:
                # Calculate density at this point
                density = self._calculate_density_at_point(x, y)

                # Convert density to probability (buildings per km² to probability per sample)
                cell_area = (2 * max_radius / grid_resolution) ** 2
                probability = density * cell_area

                # Sample based on probability
                if random.random() < probability:
                    # Get chaos factor for this position
                    chaos_factor = self._calculate_chaos_factor(x, y)

                    # Get zone-based chaos
                    zone = self.city.get_zone_at_position(x, y)
                    if zone in CHAOS_ORDER['zone_chaos']:
                        # Use zone-based chaos directly (no max, to ensure outskirts are ordered)
                        chaos_factor = CHAOS_ORDER['zone_chaos'][zone]

                    # Apply chaos/order placement
                    final_x, final_y = x, y  # Default to original position

                    # Always find nearest grid for ordered areas
                    nearest_grid = self._find_nearest_grid_area(x, y)

                    # Force grid alignment in zero-chaos zones
                    if chaos_factor == 0.0 and nearest_grid:
                        # Perfect grid alignment
                        grid_x, grid_y = nearest_grid.snap_to_grid(x, y)
                        final_x = grid_x
                        final_y = grid_y
                        placement_stats['grid'] += 1
                    elif chaos_factor < 0.5 and nearest_grid:
                        # In ordered areas, use grid with some variation
                        grid_x, grid_y = nearest_grid.snap_to_grid(x, y)
                        placement_stats['grid'] += 1

                        if chaos_factor < 0.1:
                            # Almost perfect grid alignment
                            max_offset = nearest_grid.spacing * 0.02
                            final_x = grid_x + random.uniform(-max_offset, max_offset)
                            final_y = grid_y + random.uniform(-max_offset, max_offset)
                        else:
                            # Some variation based on chaos
                            max_offset = nearest_grid.spacing * 0.15 * chaos_factor
                            final_x = grid_x + random.uniform(-max_offset, max_offset)
                            final_y = grid_y + random.uniform(-max_offset, max_offset)
                    else:
                        # Chaotic placement
                        placement_stats['chaotic'] += 1
                        offset = 0.025  # km
                        final_x = x + random.uniform(-offset, offset)
                        final_y = y + random.uniform(-offset, offset)

                    placement_stats['total'] += 1

                    # Check minimum distance
                    if self._check_minimum_distance(final_x, final_y, occupied):
                        positions.append((final_x, final_y))
                        occupied.append((final_x, final_y))

                        # Keep occupied list manageable
                        if len(occupied) > 100:
                            occupied = occupied[-50:]

        return positions, placement_stats

    def _calculate_density_at_point(self, x: float, y: float) -> float:
        """Calculate building density at a point using gaussian + district attractors"""
        # Main gaussian density from city center
        distance_from_center = math.sqrt(x ** 2 + y ** 2)
        gaussian_value = math.exp(-(distance_from_center ** 2) / (2 * self.sigma ** 2))
        base_density = self.center_density * gaussian_value

        # Apply boundary penalty for locations beyond city radius
        if distance_from_center > self.city.radius:
            # Sharp falloff beyond city boundary
            excess_distance = distance_from_center - self.city.radius
            boundary_penalty = math.exp(-self.density_falloff_power * (excess_distance / (0.1 * self.city.radius)))
            base_density *= boundary_penalty

        # Add district center attractors
        attractor_boost = 0
        for center in self.city.get_all_district_centers():
            distance_to_center = math.sqrt((x - center.x) ** 2 + (y - center.y) ** 2)
            # Soft gaussian bump with configurable parameters
            attractor_sigma = BUILDING_GENERATION['district_attractor_sigma'] * self.city.radius
            attractor_strength = BUILDING_GENERATION['district_attractor_strength']

            attractor_value = attractor_strength * math.exp(
                -(distance_to_center ** 2) / (2 * attractor_sigma ** 2)
            )
            attractor_boost = max(attractor_boost, attractor_value)  # Use max, not sum

        # Combine base density with attractor boost
        total_density = base_density * (1 + attractor_boost)

        # Boost density in ordered areas to ensure grid is visible
        zone = self.city.get_zone_at_position(x, y)
        if zone in ['outskirts']:
            # Slightly increase density in outskirts (within city)
            total_density *= 1.2
        elif zone == 'outside' and distance_from_center < self.city.radius * 1.05:
            # Only boost density for "outside" areas very close to city
            total_density *= 0.8

        return total_density

    def _calculate_district_influences(self, x: float, y: float) -> Dict[int, float]:
        """Calculate influence of each district at a position"""
        influences = {}

        for district in self.city.get_all_district_centers():
            distance = district.distance_to_point(x, y)

            # Gaussian influence with district-specific sigma
            sigma = BUILDING_GENERATION['district_influence_sigma'] * self.city.radius
            influence = math.exp(-(distance ** 2) / (2 * sigma ** 2))

            # Only store significant influences
            if influence > 0.01:
                influences[district.id] = influence

        # Normalize influences to sum to 1
        total = sum(influences.values())
        if total > 0:
            influences = {k: v / total for k, v in influences.items()}

        return influences

    def _check_minimum_distance(self, x: float, y: float,
                                occupied: List[Tuple[float, float]]) -> bool:
        """Check if position maintains minimum distance from other buildings"""
        # In perfectly ordered areas, skip distance check to allow grid packing
        zone = self.city.get_zone_at_position(x, y)
        if zone in ['outskirts', 'outside', 'industrial'] and CHAOS_ORDER['zone_chaos'].get(zone, 1.0) == 0.0:
            # In perfectly ordered zones, allow tighter packing
            min_distance = self.min_building_distance * 0.3
        elif zone in ['outskirts', 'outside', 'industrial']:
            min_distance = self.min_building_distance * 0.5  # Allow tighter packing in grids
        else:
            min_distance = self.min_building_distance

        for ox, oy in occupied[-50:]:  # Check last 50 positions for efficiency
            distance = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
            if distance < min_distance:
                return False
        return True

    def _select_building_type(self, zone: str, district_influences: Dict[int, float]) -> str:
        """Select building type based on zone and district influences"""
        # Get base zone probabilities
        if zone not in self.zone_probabilities:
            return None

        zone_probs = self.zone_probabilities[zone].copy()

        # If no district influences, use zone probabilities
        if not district_influences:
            return self._sample_from_probabilities(zone_probs)

        # Calculate blended probabilities based on district influences
        blended_probs = {}

        for building_type in ['apartment', 'house', 'office', 'commercial', 'factory']:
            # Start with zone probability
            zone_prob = zone_probs.get(building_type, 0)

            # Calculate district-influenced probability
            district_prob = 0
            for district_id, influence in district_influences.items():
                district = self.city.get_district_by_id(district_id)
                if district:
                    # Get district type probabilities
                    district_type_probs = DISTRICT_BUILDING_PROBABILITIES.get(
                        district.district_type, {}
                    )
                    district_prob += influence * district_type_probs.get(building_type, 0)

            # Get influence strength for this zone
            strength_key = f"{zone}"
            if strength_key not in DISTRICT_INFLUENCE_STRENGTH:
                # Try to find a matching ring
                if zone.startswith('ring_'):
                    strength_key = zone
                else:
                    strength_key = 'default'

            influence_strength = DISTRICT_INFLUENCE_STRENGTH.get(strength_key, 0.5)

            # Blend zone and district probabilities
            blended_probs[building_type] = (
                    (1 - influence_strength) * zone_prob +
                    influence_strength * district_prob
            )

        return self._sample_from_probabilities(blended_probs)

    def _sample_from_probabilities(self, probabilities: Dict[str, float]) -> str:
        """Sample a building type from probability distribution"""
        if not probabilities:
            return None

        # Random selection based on probabilities
        types = list(probabilities.keys())
        weights = list(probabilities.values())

        # Ensure weights sum to 1 (or less)
        total_weight = sum(weights)
        if total_weight > 1:
            weights = [w / total_weight for w in weights]

        # Add "no building" probability if total < 1
        if total_weight < 1:
            types.append(None)
            weights.append(1 - total_weight)

        return random.choices(types, weights=weights)[0]
