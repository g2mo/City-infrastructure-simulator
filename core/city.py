"""
City module - defines the city structure
Updated to include buildings as graph nodes, district types, and grid areas
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import math
import networkx as nx


@dataclass
class Building:
    """Represents a building in the city"""
    id: int
    x: float  # Position in km
    y: float  # Position in km
    building_type: str  # 'apartment', 'house', 'office', 'commercial', 'factory'
    zone: str  # Which zone the building is in
    primary_district: int = -1  # ID of primary influencing district
    district_influences: Dict[int, float] = field(default_factory=dict)  # District ID -> influence strength

    def distance_to(self, other: 'Building') -> float:
        """Calculate distance to another building in km"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class DistrictCenter:
    """Represents a district center point"""
    id: int  # Unique district ID
    x: float
    y: float
    ring: int  # Which ring this center belongs to (0 = historical center)
    angle: float  # Angle in radians from east
    district_type: str  # 'residential', 'commercial', 'mixed'

    def distance_to(self, other: 'DistrictCenter') -> float:
        """Calculate distance to another district center"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def distance_to_point(self, x: float, y: float) -> float:
        """Calculate distance to a point"""
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)


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
class GridArea:
    """Represents a local grid area with its own orientation and spacing"""
    id: int
    center_x: float
    center_y: float
    rotation: float  # Grid rotation in radians
    spacing: float  # Grid spacing in km
    zone: str  # Which zone this grid belongs to

    def snap_to_grid(self, x: float, y: float) -> Tuple[float, float]:
        """Snap a position to the nearest grid point"""
        # Translate to grid origin
        dx = x - self.center_x
        dy = y - self.center_y

        # Rotate to align with grid
        cos_r = math.cos(-self.rotation)
        sin_r = math.sin(-self.rotation)
        grid_x = dx * cos_r - dy * sin_r
        grid_y = dx * sin_r + dy * cos_r

        # Snap to nearest grid point
        snapped_x = round(grid_x / self.spacing) * self.spacing
        snapped_y = round(grid_y / self.spacing) * self.spacing

        # Rotate back
        cos_r = math.cos(self.rotation)
        sin_r = math.sin(self.rotation)
        final_x = snapped_x * cos_r - snapped_y * sin_r + self.center_x
        final_y = snapped_x * sin_r + snapped_y * cos_r + self.center_y

        return final_x, final_y


@dataclass
class City:
    """Represents the city with its layout structure and buildings"""
    radius: float  # City radius in km
    historical_center_radius: float
    rings: List[Ring] = field(default_factory=list)
    outskirts_inner_radius: float = 0.0
    outskirts_outer_radius: float = 0.0
    industrial_zones: List[IndustrialZone] = field(default_factory=list)
    historical_center_district: Optional[DistrictCenter] = None  # Special district for historical center
    district_centers: List[DistrictCenter] = field(default_factory=list)
    buildings: List[Building] = field(default_factory=list)
    building_graph: nx.Graph = field(default_factory=nx.Graph)
    grid_areas: List[GridArea] = field(default_factory=list)  # Local grid areas for ordered placement

    def __post_init__(self):
        """Validate city data"""
        if self.radius <= 0:
            raise ValueError(f"City radius must be positive, got {self.radius}")

    def add_building(self, building: Building):
        """Add a building to the city and graph"""
        self.buildings.append(building)
        # Add building as node to graph
        self.building_graph.add_node(
            building.id,
            pos=(building.x, building.y),
            type=building.building_type,
            zone=building.zone,
            primary_district=building.primary_district
        )

    def set_grid_areas(self, grid_areas: List[GridArea]):
        """Set the grid areas for the city"""
        self.grid_areas = grid_areas

    def get_zone_at_position(self, x: float, y: float) -> str:
        """Determine which zone a position belongs to"""
        distance = math.sqrt(x ** 2 + y ** 2)

        # Check industrial zones first
        for iz in self.industrial_zones:
            iz_dist = math.sqrt((x - iz.x) ** 2 + (y - iz.y) ** 2)
            if iz_dist <= iz.radius:
                return 'industrial'

        # Check other zones by radius
        if distance <= self.historical_center_radius:
            return 'historical_center'

        # Check rings
        for ring in self.rings:
            if ring.inner_radius <= distance <= ring.outer_radius:
                return f'ring_{ring.ring_number}'

        # Check outskirts
        if self.outskirts_inner_radius <= distance <= self.outskirts_outer_radius:
            return 'outskirts'

        # Outside city
        return 'outside'

    def get_num_rings(self) -> int:
        """Get the number of rings based on city radius"""
        if self.radius < 5.0:
            return 1
        elif self.radius < 10.0:
            return 2
        else:
            return 3

    def get_all_district_centers(self) -> List[DistrictCenter]:
        """Get all district centers from all rings plus historical center"""
        centers = []
        if self.historical_center_district:
            centers.append(self.historical_center_district)
        for ring in self.rings:
            centers.extend(ring.district_centers)
        return centers

    def get_district_by_id(self, district_id: int) -> Optional[DistrictCenter]:
        """Get a district center by its ID"""
        for district in self.get_all_district_centers():
            if district.id == district_id:
                return district
        return None

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of the city including industrial zones"""
        # Include industrial zones which are at 120% of city radius
        padding = self.radius * 0.3
        return (-self.radius - padding, -self.radius - padding,
                self.radius + padding, self.radius + padding)

    def get_buildings_by_type(self, building_type: str) -> List[Building]:
        """Get all buildings of a specific type"""
        return [b for b in self.buildings if b.building_type == building_type]

    def to_dict(self) -> Dict:
        """Convert city to dictionary for serialization"""
        building_stats = {}
        for b_type in ['apartment', 'house', 'office', 'commercial', 'factory']:
            building_stats[b_type] = len(self.get_buildings_by_type(b_type))

        district_stats = {}
        for district in self.get_all_district_centers():
            if district.district_type not in district_stats:
                district_stats[district.district_type] = 0
            district_stats[district.district_type] += 1

        return {
            'radius': self.radius,
            'historical_center_radius': self.historical_center_radius,
            'num_rings': len(self.rings),
            'num_district_centers': len(self.get_all_district_centers()),
            'num_industrial_zones': len(self.industrial_zones),
            'num_buildings': len(self.buildings),
            'building_stats': building_stats,
            'district_stats': district_stats,
            'num_grid_areas': len(self.grid_areas),
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
