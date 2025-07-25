"""
City module - defines the city structure
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import math


@dataclass
class DistrictCenter:
    """Represents a district center point"""
    x: float
    y: float
    ring: int  # Which ring this center belongs to (0 = historical center)
    angle: float  # Angle in radians from east

    def distance_to(self, other: 'DistrictCenter') -> float:
        """Calculate distance to another district center"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class IndustrialZone:
    """Represents an industrial zone"""
    x: float
    y: float
    radius: float
    direction: str  # 'N', 'S', 'E', 'W'


@dataclass
class Ring:
    """Represents a ring (annulus) in the city"""
    inner_radius: float
    outer_radius: float
    ring_number: int
    district_centers: List[DistrictCenter] = field(default_factory=list)


@dataclass
class City:
    """Represents the city with its layout structure"""
    radius: float  # City radius in km
    historical_center_radius: float
    rings: List[Ring]
    outskirts_inner_radius: float
    outskirts_outer_radius: float
    industrial_zones: List[IndustrialZone]
    district_centers: List[DistrictCenter] = field(default_factory=list)

    def __post_init__(self):
        """Validate city data"""
        if self.radius <= 0:
            raise ValueError(f"City radius must be positive, got {self.radius}")

    def get_num_rings(self) -> int:
        """Get the number of rings based on city radius"""
        if self.radius < 5.0:
            return 1
        elif self.radius < 10.0:
            return 2
        else:
            return 3

    def get_all_district_centers(self) -> List[DistrictCenter]:
        """Get all district centers from all rings"""
        centers = []
        for ring in self.rings:
            centers.extend(ring.district_centers)
        return centers

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of the city including industrial zones"""
        # Include industrial zones which are at 120% of city radius
        padding = self.radius * 0.3
        return (-self.radius - padding, -self.radius - padding,
                self.radius + padding, self.radius + padding)

    def to_dict(self) -> Dict:
        """Convert city to dictionary for serialization"""
        return {
            'radius': self.radius,
            'historical_center_radius': self.historical_center_radius,
            'num_rings': len(self.rings),
            'num_district_centers': len(self.get_all_district_centers()),
            'num_industrial_zones': len(self.industrial_zones),
            'rings': [
                {
                    'ring_number': ring.ring_number,
                    'inner_radius': ring.inner_radius,
                    'outer_radius': ring.outer_radius,
                    'num_centers': len(ring.district_centers)
                }
                for ring in self.rings
            ]
        }
