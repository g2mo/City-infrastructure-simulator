"""
Building generation module - creates buildings based on gaussian density
Updated to include district type influences
"""

import math
import random
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass

from core.city import City, Building
from config import (
    BUILDING_GENERATION,
    BUILDING_COLORS,
    DISTRICT_BUILDING_PROBABILITIES,
    DISTRICT_INFLUENCE_STRENGTH
)


class BuildingGenerator:
    """Generates buildings for a city using gaussian density distribution"""

    def __init__(self, city: City):
        """Initialize generator with a city"""
        self.city = city
        self.next_building_id = 0
        self.min_building_distance = 0.005  # 5 meters in km

        # Calculate gaussian parameters
        self.sigma = city.radius / 2  # 2*sigma = city radius
        self.center_density = BUILDING_GENERATION['center_density']  # buildings per km²

        # Zone probabilities for building types
        self.zone_probabilities = BUILDING_GENERATION['zone_probabilities']

    def generate(self) -> None:
        """Generate all buildings for the city"""
        print(f"Generating buildings for city with radius {self.city.radius} km...")

        # Generate candidate positions based on density
        positions = self._generate_building_positions()

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

    def _generate_building_positions(self) -> List[Tuple[float, float]]:
        """Generate building positions based on gaussian density"""
        positions = []

        # Define sampling area (up to 125% of city radius)
        max_radius = self.city.radius * 1.25

        # Create grid for sampling
        grid_resolution = int(max_radius * 40)  # ~40 points per km
        x_points = np.linspace(-max_radius, max_radius, grid_resolution)
        y_points = np.linspace(-max_radius, max_radius, grid_resolution)

        # Track occupied positions for minimum distance
        occupied = []

        for x in x_points:
            for y in y_points:
                # Calculate density at this point
                density = self._calculate_density_at_point(x, y)

                # Convert density to probability (buildings per km² to probability per sample)
                cell_area = (2 * max_radius / grid_resolution) ** 2
                probability = density * cell_area

                # Sample based on probability
                if random.random() < probability:
                    # Check minimum distance
                    if self._check_minimum_distance(x, y, occupied):
                        positions.append((x, y))
                        occupied.append((x, y))

                        # Keep occupied list manageable
                        if len(occupied) > 100:
                            occupied = occupied[-50:]

        # Add some randomness to positions (organic feel)
        final_positions = []
        for x, y in positions:
            # Small random offset (up to 25 meters)
            offset = 0.025  # km
            new_x = x + random.uniform(-offset, offset)
            new_y = y + random.uniform(-offset, offset)
            final_positions.append((new_x, new_y))

        return final_positions

    def _calculate_density_at_point(self, x: float, y: float) -> float:
        """Calculate building density at a point using gaussian + district attractors"""
        # Main gaussian density from city center
        distance_from_center = math.sqrt(x ** 2 + y ** 2)
        gaussian_value = math.exp(-(distance_from_center ** 2) / (2 * self.sigma ** 2))
        base_density = self.center_density * gaussian_value

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
        for ox, oy in occupied[-50:]:  # Check last 50 positions for efficiency
            distance = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
            if distance < self.min_building_distance:
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
