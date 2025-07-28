"""
Plotly visualization for city layout
Updated to include building visualization with filtering
"""

import plotly.graph_objects as go
import numpy as np
from typing import List

from core.city import City
from config import VISUALIZATION, BUILDING_COLORS


class CityVisualizer:
    """Creates interactive Plotly visualizations of city layout"""

    def __init__(self, city: City):
        """Initialize visualizer with a city"""
        self.city = city
        self.colors = VISUALIZATION['colors']
        self.sizes = VISUALIZATION['sizes']

    def create_figure(self) -> go.Figure:
        """Create the main city visualization with buildings"""
        fig = go.Figure()

        # Add city zones (background layers)
        self._add_city_zones(fig)

        # Add buildings by type
        self._add_buildings(fig)

        # Add district centers
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
                      f'Buildings: {len(self.city.buildings)} | '
                      f'Apartments: {building_counts["apartment"]} | '
                      f'Houses: {building_counts["house"]} | '
                      f'Offices: {building_counts["office"]} | '
                      f'Commercial: {building_counts["commercial"]} | '
                      f'Factories: {building_counts["factory"]}')

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
                itemsizing='constant'
            ),
            height=800,
            width=1000,
            plot_bgcolor='white',
            hovermode='closest'
        )

        return fig

    def _add_city_zones(self, fig: go.Figure):
        """Add city zones as background layers"""
        # City boundary
        self._add_circle(fig, 0, 0, self.city.radius,
                         name="City Boundary",
                         color=self.colors['city_boundary'],
                         fill=False, width=2, showlegend=False)

        # Historical center
        self._add_circle(fig, 0, 0, self.city.historical_center_radius,
                         name="Historical Center",
                         color=self.colors['historical_center'],
                         fill=True, opacity=0.1, showlegend=False)

        # Rings
        for ring in self.city.rings:
            color = self.colors.get(f'ring_{ring.ring_number}', 'blue')
            self._add_annulus(fig, ring.inner_radius, ring.outer_radius,
                              name=f"Ring {ring.ring_number}",
                              color=color, opacity=0.08, showlegend=False)

        # Outskirts
        self._add_annulus(fig, self.city.outskirts_inner_radius,
                          self.city.outskirts_outer_radius,
                          name="Outskirts",
                          color=self.colors['outskirts'],
                          opacity=0.05, showlegend=False)

    def _add_buildings(self, fig: go.Figure):
        """Add buildings to the figure by type"""
        building_types = ['apartment', 'house', 'office', 'commercial', 'factory']

        for b_type in building_types:
            buildings = self.city.get_buildings_by_type(b_type)

            if buildings:
                x_coords = [b.x for b in buildings]
                y_coords = [b.y for b in buildings]

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
                    hovertemplate=(f'{b_type.capitalize()}<br>'
                                   'Position: (%{x:.3f}, %{y:.3f})<br>'
                                   'Zone: %{text}<extra></extra>'),
                    text=[b.zone for b in buildings],
                    legendgroup='buildings',
                    showlegend=True
                ))

    def _add_district_centers(self, fig: go.Figure):
        """Add district centers"""
        for ring in self.city.rings:
            if ring.district_centers:
                x_coords = [c.x for c in ring.district_centers]
                y_coords = [c.y for c in ring.district_centers]

                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='markers',
                    name=f'District Centers - Ring {ring.ring_number}',
                    marker=dict(
                        size=self.sizes['district_center'],
                        color=self.colors.get(f'ring_{ring.ring_number}', 'blue'),
                        symbol='star',
                        line=dict(width=1, color='black')
                    ),
                    hovertemplate='District Center<br>Ring: %{text}<br>Position: (%{x:.2f}, %{y:.2f})<extra></extra>',
                    text=[f'{ring.ring_number}'] * len(x_coords),
                    showlegend=False
                ))

    def _add_industrial_zones(self, fig: go.Figure):
        """Add industrial zones"""
        for zone in self.city.industrial_zones:
            self._add_circle(fig, zone.x, zone.y, zone.radius,
                             name=f"Industrial Zone {zone.direction}",
                             color=self.colors['industrial'],
                             fill=True, opacity=0.2, showlegend=False)

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
                showlegend=False
            ))

    def _add_circle(self, fig: go.Figure, x: float, y: float, radius: float,
                    name: str, color: str, fill: bool = False,
                    opacity: float = 1.0, width: int = 1, showlegend: bool = True):
        """Add a circle to the figure"""
        theta = np.linspace(0, 2 * np.pi, 100)
        circle_x = x + radius * np.cos(theta)
        circle_y = y + radius * np.sin(theta)

        if fill:
            fig.add_trace(go.Scatter(
                x=circle_x,
                y=circle_y,
                mode='lines',
                name=name,
                line=dict(color=color, width=width),
                fill='toself',
                fillcolor=color,
                opacity=opacity,
                hoverinfo='skip',
                showlegend=showlegend
            ))
        else:
            fig.add_trace(go.Scatter(
                x=circle_x,
                y=circle_y,
                mode='lines',
                name=name,
                line=dict(color=color, width=width),
                opacity=opacity,
                hoverinfo='skip',
                showlegend=showlegend
            ))

    def _add_annulus(self, fig: go.Figure, inner_radius: float, outer_radius: float,
                     name: str, color: str, opacity: float = 0.2, showlegend: bool = True):
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

        fig.add_trace(go.Scatter(
            x=x_path,
            y=y_path,
            mode='lines',
            name=name,
            line=dict(color=color, width=1),
            fill='toself',
            fillcolor=color,
            opacity=opacity,
            hoverinfo='skip',
            showlegend=showlegend
        ))
