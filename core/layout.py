"""
Layout generation module - creates city layout based on rules
Updated to assign district types
"""

import math
import random
from typing import List, Tuple

from core.city import City, Ring, DistrictCenter, IndustrialZone
from config import (
    HISTORICAL_CENTER, RING_SYSTEM, INDUSTRIAL_ZONES,
    DISTRICT_CENTERS, LAYOUT_PARAMS, DISTRICT_TYPE_DISTRIBUTION
)


class LayoutGenerator:
    """Generates city layout based on radius"""

    def __init__(self, city_radius: float):
        """Initialize generator with city radius"""
        self.city_radius = city_radius
        self.buffer_distance = city_radius * LAYOUT_PARAMS['boundary_buffer_fraction']
        self.min_center_distance = city_radius * LAYOUT_PARAMS['min_center_distance_fraction']
        self.next_district_id = 0

    def generate(self) -> City:
        """Generate complete city layout with seamless zone transitions"""
        # Generate all zone boundaries sequentially to ensure no gaps
        boundaries = self._generate_zone_boundaries()

        # Extract boundaries
        historical_radius = boundaries['historical_center_end']
        ring_boundaries = boundaries['rings']
        outskirts_inner = boundaries['outskirts_start']
        outskirts_outer = boundaries['outskirts_end']

        # Create rings from boundaries
        rings = []
        for i, (inner, outer) in enumerate(ring_boundaries):
            rings.append(Ring(
                inner_radius=inner,
                outer_radius=outer,
                ring_number=i + 1
            ))

        # Generate industrial zones
        industrial_zones = self._generate_industrial_zones()

        # Create city object
        city = City(
            radius=self.city_radius,
            historical_center_radius=historical_radius,
            rings=rings,
            outskirts_inner_radius=outskirts_inner,
            outskirts_outer_radius=outskirts_outer,
            industrial_zones=industrial_zones
        )

        # Create historical center district (always mixed)
        city.historical_center_district = DistrictCenter(
            id=self.next_district_id,
            x=0,
            y=0,
            ring=0,  # 0 indicates historical center
            angle=0,
            district_type='mixed'
        )
        self.next_district_id += 1
        city.district_centers.append(city.historical_center_district)

        # Generate district centers for each ring with types
        for ring in city.rings:
            centers = self._generate_district_centers_for_ring(ring)
            ring.district_centers = centers
            city.district_centers.extend(centers)

        return city

    def _generate_zone_boundaries(self) -> dict:
        """Generate all zone boundaries sequentially to ensure complete coverage"""
        boundaries = {}

        # 1. Historical center: starts at 0, ends at 10-20% of city radius
        historical_center_fraction = random.uniform(
            HISTORICAL_CENTER['min_radius_fraction'],
            HISTORICAL_CENTER['max_radius_fraction']
        )
        historical_center_end = self.city_radius * historical_center_fraction
        boundaries['historical_center_end'] = historical_center_end

        # 2. Determine where ring system should end (60-70% of city radius)
        ring_system_end_fraction = RING_SYSTEM['end_fraction'] + random.uniform(
            -RING_SYSTEM['end_variation'],
            RING_SYSTEM['end_variation']
        )
        ring_system_end = self.city_radius * ring_system_end_fraction

        # 3. Generate rings to fill space between historical center and ring system end
        num_rings = self._get_num_rings()
        ring_boundaries = self._generate_ring_boundaries(
            start=historical_center_end,
            end=ring_system_end,
            num_rings=num_rings
        )
        boundaries['rings'] = ring_boundaries

        # 4. Outskirts: starts where rings end, goes to city boundary
        boundaries['outskirts_start'] = ring_system_end
        boundaries['outskirts_end'] = self.city_radius

        return boundaries

    def _generate_ring_boundaries(self, start: float, end: float, num_rings: int) -> List[Tuple[float, float]]:
        """Generate ring boundaries to fill space between start and end"""
        if num_rings == 0:
            return []

        ring_boundaries = []

        if num_rings == 1:
            # Single ring fills entire space
            ring_boundaries.append((start, end))
        else:
            # Multiple rings: divide space with some randomness
            total_width = end - start

            # Generate random widths for each ring
            random_factors = [random.uniform(0.8, 1.2) for _ in range(num_rings)]
            total_factor = sum(random_factors)

            # Normalize to ensure they sum to total width
            ring_widths = [(factor / total_factor) * total_width for factor in random_factors]

            # Create boundaries
            current_position = start
            for i, width in enumerate(ring_widths):
                ring_start = current_position
                ring_end = current_position + width

                # Ensure last ring ends exactly at the target
                if i == num_rings - 1:
                    ring_end = end

                ring_boundaries.append((ring_start, ring_end))
                current_position = ring_end

        return ring_boundaries

    def _generate_industrial_zones(self) -> List[IndustrialZone]:
        """Generate industrial zones based on city size"""
        zones = []

        distance = self.city_radius * INDUSTRIAL_ZONES['distance_fraction']
        zone_radius = self.city_radius * INDUSTRIAL_ZONES['radius_fraction']

        if self.city_radius < INDUSTRIAL_ZONES['threshold_radius']:
            # 2 zones: East and West
            directions = [('E', 0), ('W', math.pi)]
        else:
            # 4 zones: N, S, E, W
            directions = [
                ('N', math.pi / 2),
                ('S', 3 * math.pi / 2),
                ('E', 0),
                ('W', math.pi)
            ]

        for direction, angle in directions:
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)

            zones.append(IndustrialZone(
                x=x,
                y=y,
                radius=zone_radius,
                direction=direction
            ))

        return zones

    def _get_num_rings(self) -> int:
        """Get number of rings based on city radius"""
        if self.city_radius < 5.0:
            return 1
        elif self.city_radius < 10.0:
            return 2
        else:
            return 3

    def _interpolate_district_count(self, ring_number: int) -> int:
        """Interpolate number of district centers for a ring based on city radius"""
        ring_key = f'ring_{ring_number}'

        if ring_key not in DISTRICT_CENTERS:
            return 0

        min_count = DISTRICT_CENTERS[ring_key]['min']
        max_count = DISTRICT_CENTERS[ring_key]['max']

        # Linear interpolation from 1km to 15km
        t = (self.city_radius - 1.0) / 14.0  # Normalize to [0, 1]
        t = max(0, min(1, t))  # Clamp to [0, 1]

        count = int(min_count + t * (max_count - min_count))
        return max(1, count)  # Ensure at least 1 center

    def _select_district_type(self, ring_number: int) -> str:
        """Select a district type based on ring-specific probabilities"""
        ring_key = f'ring_{ring_number}'

        if ring_key not in DISTRICT_TYPE_DISTRIBUTION:
            return 'mixed'  # Default

        probabilities = DISTRICT_TYPE_DISTRIBUTION[ring_key]
        types = list(probabilities.keys())
        weights = list(probabilities.values())

        return random.choices(types, weights=weights)[0]

    def _generate_district_centers_for_ring(self, ring: Ring) -> List[DistrictCenter]:
        """Generate district centers for a specific ring using angular sectors"""
        num_centers = self._interpolate_district_count(ring.ring_number)

        if num_centers == 0:
            return []

        centers = []

        # Divide ring into angular sectors
        angle_per_sector = 2 * math.pi / num_centers

        for i in range(num_centers):
            # Define angular sector boundaries
            angle_start = i * angle_per_sector
            angle_end = (i + 1) * angle_per_sector

            # Random angle within sector
            angle = random.uniform(angle_start + 0.1, angle_end - 0.1)

            # Random radius within ring boundaries (with buffer)
            min_r = ring.inner_radius + self.buffer_distance
            max_r = ring.outer_radius - self.buffer_distance

            # Ensure valid range
            if min_r >= max_r:
                # If ring is too thin for buffer, use smaller buffer
                buffer = min(self.buffer_distance, (ring.outer_radius - ring.inner_radius) * 0.2)
                min_r = ring.inner_radius + buffer
                max_r = ring.outer_radius - buffer

            radius = random.uniform(min_r, max_r)

            # Convert to Cartesian coordinates
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            # Select district type based on ring
            district_type = self._select_district_type(ring.ring_number)

            centers.append(DistrictCenter(
                id=self.next_district_id,
                x=x,
                y=y,
                ring=ring.ring_number,
                angle=angle,
                district_type=district_type
            ))
            self.next_district_id += 1

        return centers
