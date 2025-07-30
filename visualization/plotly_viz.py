"""
Plotly visualization for city layout
Enhanced with district types, toggleable layers, and grid visualization
"""

import plotly.graph_objects as go
import numpy as np
import math
from typing import List

from core.city import City
from config import (
    VISUALIZATION,
    BUILDING_COLORS,
    DISTRICT_COLORS,
    BUILDING_GENERATION,
    CHAOS_ORDER
)


class CityVisualizer:
    """Creates interactive Plotly visualizations of city layout"""

    def __init__(self, city: City):
        """Initialize visualizer with a city"""
        self.city = city
        self.colors = VISUALIZATION['colors']
        self.sizes = VISUALIZATION['sizes']

    def create_figure(self) -> go.Figure:
        """Create the main city visualization with buildings and toggleable layers"""
        fig = go.Figure()

        # Add city zones (background layers) - toggleable
        self._add_city_zones(fig)

        # Add local grid patterns and tessellation - toggleable
        self._add_grid_patterns(fig)

        # Add district influence areas (subtle) - toggleable
        self._add_district_influence_areas(fig)

        # Add chaos/order gradient visualization - toggleable
        self._add_chaos_order_gradient(fig)

        # Add buildings by type - each type toggleable
        self._add_buildings(fig)

        # Add district centers with types
        self._add_district_centers(fig)

        # Add industrial zones
        self._add_industrial_zones(fig)

        # Update layout
        bounds = self.city.get_bounds()

        # Count buildings by type
        building_counts = {}
        for b_type in ['apartment', 'house', 'office', 'commercial', 'factory']:
            building_counts[b_type] = len(self.city.get_buildings_by_type(b_type))

        title_text = (f'City Layout - Radius: {self.city.radius} km | '
                      f'Total Buildings: {len(self.city.buildings)}<br>'
                      f'<span style="font-size: 14px">Click legend items to toggle visibility</span>')

        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=16)
            ),
            xaxis=dict(
                title='Distance (km)',
                range=[bounds[0], bounds[2]],
                scaleanchor='y',
                scaleratio=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='gray'
            ),
            yaxis=dict(
                title='Distance (km)',
                range=[bounds[1], bounds[3]],
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='gray'
            ),
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='black',
                borderwidth=1,
                itemsizing='constant',
                tracegroupgap=10
            ),
            height=800,
            width=1200,
            plot_bgcolor='white',
            hovermode='closest'
        )

        return fig

    def _add_grid_patterns(self, fig: go.Figure):
        """Add visualization of complete grid tessellation"""
        if not self.city.grid_areas:
            return

        # Create a Voronoi-style tessellation visualization
        # We'll create a mesh of points and color them by their nearest grid
        bounds = self.city.get_bounds()
        resolution = 100  # Grid resolution for tessellation

        x = np.linspace(bounds[0], bounds[2], resolution)
        y = np.linspace(bounds[1], bounds[3], resolution)
        X, Y = np.meshgrid(x, y)

        # For each point, find nearest grid and get its ID
        grid_ids = np.zeros_like(X)

        for i in range(resolution):
            for j in range(resolution):
                px, py = X[i, j], Y[i, j]
                min_dist = float('inf')
                nearest_grid_id = -1

                for grid in self.city.grid_areas:
                    dist = np.sqrt((px - grid.center_x) ** 2 + (py - grid.center_y) ** 2)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_grid_id = grid.id

                grid_ids[i, j] = nearest_grid_id

        # Create contour plot for tessellation
        fig.add_trace(go.Contour(
            x=x,
            y=y,
            z=grid_ids,
            contours=dict(
                coloring='lines',
                showlabels=False,
            ),
            line=dict(width=3, color='darkblue'),
            showscale=False,
            name="Grid Tessellation",
            showlegend=True,
            legendgroup='grids',
            visible='legendonly',
            hoverinfo='skip',
            opacity=0.7
        ))

        # Now add the actual grid lines for each grid area
        for grid in self.city.grid_areas:
            # Determine the extent of this grid's influence
            # Use Voronoi-like approach - draw grids where this is the nearest grid

            # Find approximate bounds of this grid's region
            grid_points_x = []
            grid_points_y = []

            # Sample points to find this grid's domain
            # Use larger search radius for outer grids
            if grid.zone in ['outskirts', 'outside']:
                test_radius = self.city.radius * 0.8
            else:
                test_radius = self.city.radius * 0.4
            test_resolution = 30

            for dx in np.linspace(-test_radius, test_radius, test_resolution):
                for dy in np.linspace(-test_radius, test_radius, test_resolution):
                    test_x = grid.center_x + dx
                    test_y = grid.center_y + dy

                    # Check if this grid is nearest to this point
                    min_dist = float('inf')
                    nearest = None
                    for g in self.city.grid_areas:
                        dist = np.sqrt((test_x - g.center_x) ** 2 + (test_y - g.center_y) ** 2)
                        if dist < min_dist:
                            min_dist = dist
                            nearest = g

                    if nearest and nearest.id == grid.id:
                        grid_points_x.append(test_x)
                        grid_points_y.append(test_y)

            if not grid_points_x:
                continue

            # Find bounds of this grid's region
            min_x, max_x = min(grid_points_x), max(grid_points_x)
            min_y, max_y = min(grid_points_y), max(grid_points_y)

            # Draw grid lines within this region
            cos_r = math.cos(grid.rotation)
            sin_r = math.sin(grid.rotation)

            # Calculate how many grid lines we need
            diagonal = np.sqrt((max_x - min_x) ** 2 + (max_y - min_y) ** 2)
            n_lines = int(diagonal / grid.spacing) + 2

            # Draw vertical lines in grid space
            for i in range(-n_lines // 2, n_lines // 2 + 1):
                x_grid = i * grid.spacing
                y_start = -diagonal / 2
                y_end = diagonal / 2

                # Transform to world space
                x1 = x_grid * cos_r - y_start * sin_r + grid.center_x
                y1 = x_grid * sin_r + y_start * cos_r + grid.center_y
                x2 = x_grid * cos_r - y_end * sin_r + grid.center_x
                y2 = x_grid * sin_r + y_end * cos_r + grid.center_y

                # Clip to region bounds
                if self._line_intersects_box(x1, y1, x2, y2, min_x, min_y, max_x, max_y):
                    fig.add_trace(go.Scatter(
                        x=[x1, x2],
                        y=[y1, y2],
                        mode='lines',
                        line=dict(color='lightblue', width=1.5),
                        opacity=0.6,
                        hoverinfo='skip',
                        showlegend=False,
                        legendgroup='grids',
                        visible='legendonly'
                    ))

        # Add grid centers for reference
        if self.city.grid_areas:
            grid_x = [g.center_x for g in self.city.grid_areas]
            grid_y = [g.center_y for g in self.city.grid_areas]
            grid_zones = [g.zone for g in self.city.grid_areas]

            fig.add_trace(go.Scatter(
                x=grid_x,
                y=grid_y,
                mode='markers',
                marker=dict(
                    size=8,
                    color='darkblue',
                    symbol='diamond',
                    line=dict(width=1, color='white')
                ),
                text=[f'Grid {i}<br>Zone: {z}' for i, z in enumerate(grid_zones)],
                hoverinfo='text',
                name="Grid Centers",
                showlegend=True,
                legendgroup='grids',
                visible='legendonly'
            ))

            # Draw horizontal lines in grid space
            for i in range(-n_lines // 2, n_lines // 2 + 1):
                y_grid = i * grid.spacing
                x_start = -diagonal / 2
                x_end = diagonal / 2

                # Transform to world space
                x1 = x_start * cos_r - y_grid * sin_r + grid.center_x
                y1 = x_start * sin_r + y_grid * cos_r + grid.center_y
                x2 = x_end * cos_r - y_grid * sin_r + grid.center_x
                y2 = x_end * sin_r + y_grid * cos_r + grid.center_y

                # Clip to region bounds
                if self._line_intersects_box(x1, y1, x2, y2, min_x, min_y, max_x, max_y):
                    fig.add_trace(go.Scatter(
                        x=[x1, x2],
                        y=[y1, y2],
                        mode='lines',
                        line=dict(color='lightblue', width=1.5),
                        opacity=0.6,
                        hoverinfo='skip',
                        showlegend=False,
                        legendgroup='grids',
                        visible='legendonly'
                    ))

    def _line_intersects_box(self, x1, y1, x2, y2, min_x, min_y, max_x, max_y):
        """Check if a line segment intersects with a box"""
        # Simple check - if either endpoint is in the box or the line crosses it
        if (min_x <= x1 <= max_x and min_y <= y1 <= max_y) or \
                (min_x <= x2 <= max_x and min_y <= y2 <= max_y):
            return True

        # Check if line crosses box boundaries
        # This is a simplified check - for full accuracy would need proper line-box intersection
        return not (max(x1, x2) < min_x or min(x1, x2) > max_x or
                    max(y1, y2) < min_y or min(y1, y2) > max_y)

    def _add_chaos_order_gradient(self, fig: go.Figure):
        """Add a heatmap showing the chaos/order gradient"""
        # Create a grid for the heatmap
        resolution = 50
        bounds = self.city.get_bounds()
        x = np.linspace(bounds[0], bounds[2], resolution)
        y = np.linspace(bounds[1], bounds[3], resolution)
        X, Y = np.meshgrid(x, y)

        # Calculate chaos factor at each point
        Z = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                # Calculate distance from center
                distance = np.sqrt(X[i, j] ** 2 + Y[i, j] ** 2)
                normalized_distance = distance / self.city.radius

                # Sigmoid function
                center = CHAOS_ORDER['transition_center']
                sharpness = CHAOS_ORDER['transition_sharpness']
                chaos_factor = 1 / (1 + np.exp(sharpness * (normalized_distance - center)))

                # Apply zone-based overrides
                zone = self.city.get_zone_at_position(X[i, j], Y[i, j])
                if zone in CHAOS_ORDER['zone_chaos']:
                    chaos_factor = CHAOS_ORDER['zone_chaos'][zone]

                Z[i, j] = chaos_factor

        # Add contour plot
        fig.add_trace(go.Contour(
            x=x,
            y=y,
            z=Z,
            colorscale=[[0, 'darkgreen'], [0.5, 'yellow'], [1, 'darkred']],
            opacity=0.3,
            contours=dict(
                start=0,
                end=1,
                size=0.1,
            ),
            colorbar=dict(
                title="Chaos Factor",
                tickmode="array",
                tickvals=[0, 0.5, 1],
                ticktext=["Ordered", "Mixed", "Chaotic"],
                len=0.5,
                x=1.15
            ),
            name="Chaos/Order Gradient",
            showlegend=True,
            legendgroup='chaos_gradient',
            visible='legendonly',
            hovertemplate='Chaos Factor: %{z:.2f}<extra></extra>'
        ))

    def _add_city_zones(self, fig: go.Figure):
        """Add city zones as background layers"""
        # City boundary
        self._add_circle(fig, 0, 0, self.city.radius,
                         name="City Boundary",  # More descriptive name
                         color=self.colors['city_boundary'],
                         fill=False, width=3, showlegend=True,
                         legendgroup='zones', visible=True)  # Always visible

        # Add 2-sigma boundary indicator (dashed line)
        sigma_factor = BUILDING_GENERATION.get('density_sigma_factor', 0.5)
        two_sigma_radius = 2 * sigma_factor * self.city.radius
        if abs(two_sigma_radius - self.city.radius) > 0.01:  # Only show if different from city radius
            theta = np.linspace(0, 2 * np.pi, 100)
            circle_x = two_sigma_radius * np.cos(theta)
            circle_y = two_sigma_radius * np.sin(theta)

            fig.add_trace(go.Scatter(
                x=circle_x,
                y=circle_y,
                mode='lines',
                line=dict(color='darkgray', width=2, dash='dash'),
                opacity=0.5,
                name="2σ Boundary (95%)",
                showlegend=True,
                legendgroup='zones',
                hoverinfo='skip'
            ))

        # Add 1-sigma boundary indicator (dotted line)
        one_sigma_radius = sigma_factor * self.city.radius
        theta = np.linspace(0, 2 * np.pi, 100)
        circle_x = one_sigma_radius * np.cos(theta)
        circle_y = one_sigma_radius * np.sin(theta)

        fig.add_trace(go.Scatter(
            x=circle_x,
            y=circle_y,
            mode='lines',
            line=dict(color='lightgray', width=1, dash='dot'),
            opacity=0.3,
            name="1σ Boundary (68%)",
            showlegend=True,
            legendgroup='zones',
            visible='legendonly',
            hoverinfo='skip'
        ))

        # Historical center
        self._add_circle(fig, 0, 0, self.city.historical_center_radius,
                         name="Historical Center",
                         color=self.colors['historical_center'],
                         fill=True, opacity=0.1, showlegend=False,
                         legendgroup='zones', visible='legendonly')

        # Rings
        for ring in self.city.rings:
            color = self.colors.get(f'ring_{ring.ring_number}', 'blue')
            self._add_annulus(fig, ring.inner_radius, ring.outer_radius,
                              name=f"Ring {ring.ring_number}",
                              color=color, opacity=0.08, showlegend=False,
                              legendgroup='zones', visible='legendonly')

        # Outskirts
        self._add_annulus(fig, self.city.outskirts_inner_radius,
                          self.city.outskirts_outer_radius,
                          name="Outskirts",
                          color=self.colors['outskirts'],
                          opacity=0.05, showlegend=False,
                          legendgroup='zones', visible='legendonly')

    def _add_district_influence_areas(self, fig: go.Figure):
        """Add subtle district influence areas"""
        # Add one legend entry for all influence areas
        first = True
        for district in self.city.get_all_district_centers():
            color = DISTRICT_COLORS.get(district.district_type, 'gray')

            # Add influence circle
            self._add_circle(
                fig, district.x, district.y,
                BUILDING_GENERATION['district_influence_sigma'] * self.city.radius * 2,
                name="District Influences" if first else None,
                color=color,
                fill=True, opacity=0.05,
                showlegend=first,
                legendgroup='influences',
                visible='legendonly'
            )
            first = False

    def _add_buildings(self, fig: go.Figure):
        """Add buildings to the figure by type"""
        building_types = ['apartment', 'house', 'office', 'commercial', 'factory']

        for b_type in building_types:
            buildings = self.city.get_buildings_by_type(b_type)

            if buildings:
                x_coords = [b.x for b in buildings]
                y_coords = [b.y for b in buildings]

                # Create hover text with district influence info
                hover_texts = []
                for b in buildings:
                    # Get primary district info
                    primary_district = self.city.get_district_by_id(b.primary_district)
                    district_info = "None"
                    if primary_district:
                        influence_pct = b.district_influences.get(b.primary_district, 0) * 100
                        district_info = f"{primary_district.district_type} ({influence_pct:.0f}%)"

                    hover_text = (
                        f'{b_type.capitalize()}<br>'
                        f'Position: ({b.x:.3f}, {b.y:.3f})<br>'
                        f'Zone: {b.zone}<br>'
                        f'Primary District: {district_info}'
                    )
                    hover_texts.append(hover_text)

                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='markers',
                    name=f'{b_type.capitalize()} ({len(buildings)})',
                    marker=dict(
                        size=self.sizes['building'],
                        color=BUILDING_COLORS[b_type],
                        symbol='circle',
                        line=dict(width=0)
                    ),
                    hovertext=hover_texts,
                    hoverinfo='text',
                    legendgroup=f'building_{b_type}',
                    showlegend=True
                ))

    def _add_district_centers(self, fig: go.Figure):
        """Add district centers with type visualization"""
        # Group by district type for legend
        district_types = {}
        for district in self.city.get_all_district_centers():
            if district.district_type not in district_types:
                district_types[district.district_type] = []
            district_types[district.district_type].append(district)

        # Add districts by type
        for dtype, districts in district_types.items():
            x_coords = [d.x for d in districts]
            y_coords = [d.y for d in districts]

            color = DISTRICT_COLORS.get(dtype, 'gray')

            # Create hover text
            hover_texts = []
            for d in districts:
                ring_name = "Historical Center" if d.ring == 0 else f"Ring {d.ring}"
                hover_texts.append(
                    f'District Center<br>'
                    f'Type: {d.district_type}<br>'
                    f'Location: {ring_name}<br>'
                    f'Position: ({d.x:.2f}, {d.y:.2f})'
                )

            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers',
                name=f'{dtype.capitalize()} Districts ({len(districts)})',
                marker=dict(
                    size=self.sizes['district_center'],
                    color=color,
                    symbol='star',
                    line=dict(width=1, color='black')
                ),
                hovertext=hover_texts,
                hoverinfo='text',
                legendgroup=f'district_{dtype}',
                showlegend=True
            ))

    def _add_industrial_zones(self, fig: go.Figure):
        """Add industrial zones"""
        first = True
        for zone in self.city.industrial_zones:
            self._add_circle(fig, zone.x, zone.y, zone.radius,
                             name="Industrial Zones" if first else None,
                             color=self.colors['industrial'],
                             fill=True, opacity=0.2,
                             showlegend=first,
                             legendgroup='industrial')
            first = False

            # Add center marker
            fig.add_trace(go.Scatter(
                x=[zone.x],
                y=[zone.y],
                mode='markers+text',
                name=f'Industrial Center {zone.direction}',
                marker=dict(
                    size=self.sizes['industrial_center'],
                    color=self.colors['industrial'],
                    symbol='square',
                    line=dict(width=2, color='black')
                ),
                text=[zone.direction],
                textposition='middle center',
                textfont=dict(size=10, color='white', family='Arial Black'),
                showlegend=False,
                legendgroup='industrial'
            ))

    def _add_circle(self, fig: go.Figure, x: float, y: float, radius: float,
                    name: str, color: str, fill: bool = False,
                    opacity: float = 1.0, width: int = 1, showlegend: bool = True,
                    legendgroup: str = None, visible: bool = True):
        """Add a circle to the figure"""
        theta = np.linspace(0, 2 * np.pi, 100)
        circle_x = x + radius * np.cos(theta)
        circle_y = y + radius * np.sin(theta)

        trace_params = {
            'x': circle_x,
            'y': circle_y,
            'mode': 'lines',
            'line': dict(color=color, width=width),
            'opacity': opacity,
            'hoverinfo': 'skip',
            'showlegend': showlegend
        }

        if name:
            trace_params['name'] = name
        if legendgroup:
            trace_params['legendgroup'] = legendgroup
        if visible == 'legendonly':
            trace_params['visible'] = 'legendonly'

        if fill:
            trace_params['fill'] = 'toself'
            trace_params['fillcolor'] = color

        fig.add_trace(go.Scatter(**trace_params))

    def _add_annulus(self, fig: go.Figure, inner_radius: float, outer_radius: float,
                     name: str, color: str, opacity: float = 0.2, showlegend: bool = True,
                     legendgroup: str = None, visible: bool = True):
        """Add an annulus (ring) to the figure"""
        theta = np.linspace(0, 2 * np.pi, 100)

        # Outer circle
        outer_x = outer_radius * np.cos(theta)
        outer_y = outer_radius * np.sin(theta)

        # Inner circle (reversed for proper fill)
        inner_x = inner_radius * np.cos(theta[::-1])
        inner_y = inner_radius * np.sin(theta[::-1])

        # Combine paths
        x_path = np.concatenate([outer_x, inner_x, [outer_x[0]]])
        y_path = np.concatenate([outer_y, inner_y, [outer_y[0]]])

        trace_params = {
            'x': x_path,
            'y': y_path,
            'mode': 'lines',
            'line': dict(color=color, width=1),
            'fill': 'toself',
            'fillcolor': color,
            'opacity': opacity,
            'hoverinfo': 'skip',
            'showlegend': showlegend
        }

        if name:
            trace_params['name'] = name
        if legendgroup:
            trace_params['legendgroup'] = legendgroup
        if visible == 'legendonly':
            trace_params['visible'] = 'legendonly'

        fig.add_trace(go.Scatter(**trace_params))
