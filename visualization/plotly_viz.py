"""
Plotly visualization for city layout
"""

import plotly.graph_objects as go
import numpy as np
from typing import List

from core.city import City
from config import VISUALIZATION


class CityVisualizer:
    """Creates interactive Plotly visualizations of city layout"""

    def __init__(self, city: City):
        """Initialize visualizer with a city"""
        self.city = city
        self.colors = VISUALIZATION['colors']
        self.sizes = VISUALIZATION['sizes']

    def create_figure(self) -> go.Figure:
        """Create the main city visualization"""
        fig = go.Figure()

        # Add city boundary
        self._add_circle(fig, 0, 0, self.city.radius,
                         name="City Boundary",
                         color=self.colors['city_boundary'],
                         fill=False, width=2)

        # Add historical center
        self._add_circle(fig, 0, 0, self.city.historical_center_radius,
                         name="Historical Center",
                         color=self.colors['historical_center'],
                         fill=True, opacity=0.2)

        # Add rings
        for ring in self.city.rings:
            color = self.colors.get(f'ring_{ring.ring_number}', 'blue')
            self._add_annulus(fig, ring.inner_radius, ring.outer_radius,
                              name=f"Ring {ring.ring_number}",
                              color=color, opacity=0.15)

        # Add outskirts
        self._add_annulus(fig, self.city.outskirts_inner_radius,
                          self.city.outskirts_outer_radius,
                          name="Outskirts",
                          color=self.colors['outskirts'],
                          opacity=0.1)

        # Add district centers
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
                        symbol='circle',
                        line=dict(width=1, color='black')
                    ),
                    hovertemplate='District Center<br>Ring: %{text}<br>Position: (%{x:.2f}, %{y:.2f})<extra></extra>',
                    text=[f'{ring.ring_number}'] * len(x_coords)
                ))

        # Add industrial zones
        for zone in self.city.industrial_zones:
            self._add_circle(fig, zone.x, zone.y, zone.radius,
                             name=f"Industrial Zone {zone.direction}",
                             color=self.colors['industrial'],
                             fill=True, opacity=0.3)

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

        # Update layout
        bounds = self.city.get_bounds()

        fig.update_layout(
            title=dict(
                text=f'City Layout - Radius: {self.city.radius} km | '
                     f'Rings: {len(self.city.rings)} | '
                     f'District Centers: {len(self.city.get_all_district_centers())}',
                font=dict(size=20)
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
                borderwidth=1
            ),
            height=800,
            width=1000,
            plot_bgcolor='white',
            hovermode='closest'
        )

        return fig

    def _add_circle(self, fig: go.Figure, x: float, y: float, radius: float,
                    name: str, color: str, fill: bool = False,
                    opacity: float = 1.0, width: int = 1):
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
                hoverinfo='skip'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=circle_x,
                y=circle_y,
                mode='lines',
                name=name,
                line=dict(color=color, width=width),
                opacity=opacity,
                hoverinfo='skip'
            ))

    def _add_annulus(self, fig: go.Figure, inner_radius: float, outer_radius: float,
                     name: str, color: str, opacity: float = 0.2):
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
            hoverinfo='skip'
        ))
