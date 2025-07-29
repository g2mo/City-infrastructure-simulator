"""
Plotly visualization for city layout
Enhanced with district types and toggleable layers
"""

import plotly.graph_objects as go
import numpy as np
from typing import List

from core.city import City
from config import (
    VISUALIZATION,
    BUILDING_COLORS,
    DISTRICT_COLORS,
    BUILDING_GENERATION
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

        # Add district influence areas (subtle) - toggleable
        self._add_district_influence_areas(fig)

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

    def _add_city_zones(self, fig: go.Figure):
        """Add city zones as background layers"""
        # Create a single toggleable group for all zones
        # City boundary
        self._add_circle(fig, 0, 0, self.city.radius,
                         name="City Zones",  # Group name
                         color=self.colors['city_boundary'],
                         fill=False, width=2, showlegend=True,
                         legendgroup='zones', visible='legendonly')

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
