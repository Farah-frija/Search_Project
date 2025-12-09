import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import List, Dict, Any

class GridVisualizer:
    """Interactive grid visualization using Plotly"""
    
    def __init__(self, grid_data: Dict[str, Any],show_costs=False):
        self.grid_data = grid_data
        self.width = grid_data['width']
        self.height = grid_data['height']
        self.show_cost=show_costs
        # Color scheme
        self.colors = {
            'empty': 'white',
            'store': '#FFA726',  # Orange
            'customer': '#42A5F5',  # Blue
            'tunnel': '#AB47BC',  # Purple
            'obstacle': '#424242',  # Gray
            'path': '#4CAF50',  # Green
            'visited': '#E0E0E0',  # Light gray
            'frontier': '#B3E5FC',  # Light blue
            'current': '#FF5722',  # Deep orange
        }
    
    def create_interactive_plot(self):
        """Create interactive grid plot"""
        fig = go.Figure()
        
        # Create grid background
        self._add_grid_background(fig)
        
        # Add obstacles
        self._add_obstacles2(fig)
        #Add costs
        if(self.show_cost):
            self._add_edge_costs(fig)
        # Add tunnels
        self._add_tunnels(fig)
        
        # Add stores
        self._add_stores(fig)
        
        # Add customers
        self._add_customers(fig)
        
        # Update layout
        fig.update_layout(
            title="Delivery Grid",
            xaxis=dict(
                range=[-1, self.width],
                showgrid=True,
                zeroline=False,
                showline=True,
                mirror=True,
                tickmode='linear',
                tick0=0,
                dtick=1
            ),
            yaxis=dict(
                range=[-1, self.height],
                showgrid=True,
                zeroline=False,
                showline=True,
                mirror=True,
                tickmode='linear',
                tick0=0,
                dtick=1,
                scaleanchor="x",
                scaleratio=1
            ),
            plot_bgcolor='white',
            width=600,
            height=600,
            hovermode='closest',
            showlegend=True
        )
        
        return fig
    def _add_edge_costs(self, fig):
        """Add edge costs to the plot"""
        if 'traffic_edges' in self.grid_data:
            for edge in self.grid_data['traffic_edges']:
                x1, y1 = edge['from']['x'], edge['from']['y']
                x2, y2 = edge['to']['x'], edge['to']['y']
                cost = edge.get('cost', 1)
                 # GRADIENT COLOR BASED ON COST
                if cost == 1:
                    text_color = '#2E7D32'  # Green for normal cost
                    bg_color = 'rgba(46, 125, 50, 0.1)'  # Light green background
                elif cost <= 3:
                    text_color = '#F57C00'  # Orange for medium cost
                    bg_color = 'rgba(245, 124, 0, 0.1)'  # Light orange background
                else:
                    text_color = '#D32F2F'  # Red for high cost
                    bg_color = 'rgba(211, 47, 47, 0.1)'  # Light red background
                # Skip obstacles (cost == 0) as they're already shown
                if cost > 0:
                    # Calculate midpoint for text
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2

                    # Add cost text
                    fig.add_trace(go.Scatter(
                        x=[mid_x],
                        y=[mid_y],
                        mode='text',
                        text=[str(cost)],
                        textfont=dict(
                            size=12,
                    
                        color=text_color,
                        weight='bold',
                        family='Arial'
                        ),
                        name='Edge Cost',
                        hoverinfo='text',
                        hovertext=f"Cost: {cost} from ({x1},{y1}) to ({x2},{y2})",
                        showlegend=False
                    ))
                
                # Optionally add a thin line to show the edge
                fig.add_trace(go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode='lines',
                    line=dict(
                        color='lightgray' if cost == 1 else 'orange',
                        width=1,
                        dash='dot' if cost > 1 else None
                    ),
                    opacity=0.5,
                    showlegend=False,
                    hoverinfo='skip'
                ))
    
    def _add_obstacles2(self, fig):
        """Add obstacles to the plot"""
        obstacles = []
        if 'traffic_edges' in self.grid_data:
            for edge in self.grid_data['traffic_edges']:
                x1, y1 = edge['from']['x'], edge['from']['y']
                x2, y2 = edge['to']['x'], edge['to']['y']
                cost = edge.get('cost', 1)

                # Only show obstacles (cost == 0) in this method
                if cost == 0:
                    # Add line for obstacle
                    fig.add_trace(go.Scatter(
                        x=[x1, x2],
                        y=[y1, y2],
                        mode='lines',
                        line=dict(color=self.colors['obstacle'], width=3),
                        name='Obstacle',
                        hoverinfo='skip'
                    ))

                    # Add thick point at center
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    obstacles.append((center_x, center_y))
    
    def _add_grid_background(self, fig):
        """Add grid lines"""
        # Vertical lines
        for x in range(self.width + 1):
            fig.add_trace(go.Scatter(
                x=[x, x],
                y=[0, self.height],
                mode='lines',
                line=dict(color='lightgray', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Horizontal lines
        for y in range(self.height + 1):
            fig.add_trace(go.Scatter(
                x=[0, self.width],
                y=[y, y],
                mode='lines',
                line=dict(color='lightgray', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    def _add_obstacles(self, fig):
        """Add obstacles to the plot"""
        obstacles = []
        for edge in self.grid_data.get('traffic_edges', []):
            if edge['cost'] == 0:
                # This is an obstacle
                x1, y1 = edge['from']['x'], edge['from']['y']
                x2, y2 = edge['to']['x'], edge['to']['y']
                
                # Add line for obstacle
                fig.add_trace(go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode='lines',
                    line=dict(color=self.colors['obstacle'], width=3),
                    name='Obstacle',
                    hoverinfo='skip'
                ))
                
                # Add thick point at center
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                obstacles.append((center_x, center_y))
        
        if obstacles:
            obs_x, obs_y = zip(*obstacles)
            fig.add_trace(go.Scatter(
                x=obs_x,
                y=obs_y,
                mode='markers',
                marker=dict(
                    symbol='x',
                    size=15,
                    color=self.colors['obstacle'],
                    line=dict(width=2)
                ),
                name='Obstacle Center',
                hoverinfo='skip'
            ))
    
    def _add_tunnels(self, fig):
        """Add tunnels to the plot"""
        for tunnel in self.grid_data.get('tunnels', []):
            x1, y1 = tunnel['entrance']['x'], tunnel['entrance']['y']
            x2, y2 = tunnel['exit']['x'], tunnel['exit']['y']
            
            # Add tunnel line (dashed)
            fig.add_trace(go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode='lines',
                line=dict(
                    color=self.colors['tunnel'],
                    width=2,
                    dash='dash'
                ),
                name='Tunnel',
                hoverinfo='text',
                hovertext=f"Tunnel: ({x1},{y1}) ↔ ({x2},{y2})"
            ))
            
            # Add tunnel markers
            fig.add_trace(go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode='markers',
                marker=dict(
                    symbol='diamond',
                    size=12,
                    color=self.colors['tunnel'],
                    line=dict(width=2, color='white')
                ),
                name='Tunnel Entrance/Exit',
                hoverinfo='text',
                hovertext=[f"Tunnel Entrance ({x1},{y1})", f"Tunnel Exit ({x2},{y2})"],
                showlegend=False
            ))
    
    def _add_stores(self, fig):
        """Add stores to the plot"""
        stores = self.grid_data.get('stores', [])
        if stores:
            store_x = [s['x'] for s in stores]
            store_y = [s['y'] for s in stores]
            store_names = [f"Store {i+1}" for i in range(len(stores))]
            
            fig.add_trace(go.Scatter(
                x=store_x,
                y=store_y,
                mode='markers+text',
                marker=dict(
                    symbol='square',
                    size=20,
                    color=self.colors['store'],
                    line=dict(width=2, color='black')
                ),
                text=store_names,
                textposition="top center",
                name='Store',
                hoverinfo='text',
                hovertext=[f"Store at ({x},{y})" for x, y in zip(store_x, store_y)]
            ))
    
    def _add_customers(self, fig):
        """Add customers to the plot"""
        customers = self.grid_data.get('customers', [])
        if customers:
            customer_x = [c['x'] for c in customers]
            customer_y = [c['y'] for c in customers]
            customer_names = [f"Customer {i+1}" for i in range(len(customers))]
            
            fig.add_trace(go.Scatter(
                x=customer_x,
                y=customer_y,
                mode='markers+text',
                marker=dict(
                    symbol='circle',
                    size=18,
                    color=self.colors['customer'],
                    line=dict(width=2, color='black')
                ),
                text=customer_names,
                textposition="top center",
                name='Customer',
                hoverinfo='text',
                hovertext=[f"Customer at ({x},{y})" for x, y in zip(customer_x, customer_y)]
            ))
    
    def plot_path(self, path_positions: List[Dict[str, int]]):
        """Add a path to the existing plot"""
        fig = self.create_interactive_plot()
        
        if path_positions:
            path_x = [pos['x'] for pos in path_positions]
            path_y = [pos['y'] for pos in path_positions]
            
            # Add path line
            fig.add_trace(go.Scatter(
                x=path_x,
                y=path_y,
                mode='lines+markers',
                line=dict(
                    color=self.colors['path'],
                    width=3
                ),
                marker=dict(
                    size=8,
                    color=self.colors['path'],
                    symbol='circle'
                ),
                name='Delivery Path',
                hoverinfo='text',
                hovertext=[f"Step {i}: ({x},{y})" for i, (x, y) in enumerate(zip(path_x, path_y))]
            ))
            
            # Add start and end markers
            fig.add_trace(go.Scatter(
                x=[path_x[0], path_x[-1]],
                y=[path_y[0], path_y[-1]],
                mode='markers',
                marker=dict(
                    symbol=['triangle-right', 'star'],
                    size=15,
                    color=[self.colors['store'], self.colors['customer']],
                    line=dict(width=2, color='black')
                ),
                name='Start/End',
                hovertext=['Start', 'End'],
                showlegend=False
            ))
        
        return fig
    
    def plot_search_progress(self, visited: List[Dict], frontier: List[Dict]):
        """Visualize search progress with visited and frontier nodes"""
        fig = self.create_interactive_plot()
        
        # Add visited nodes
        if visited:
            visited_x = [pos['x'] for pos in visited]
            visited_y = [pos['y'] for pos in visited]
            
            fig.add_trace(go.Scatter(
                x=visited_x,
                y=visited_y,
                mode='markers',
                marker=dict(
                    symbol='square',
                    size=10,
                    color=self.colors['visited'],
                    opacity=0.7
                ),
                name='Visited Nodes',
                hoverinfo='text',
                hovertext=[f"Visited ({x},{y})" for x, y in zip(visited_x, visited_y)]
            ))
        
        # Add frontier nodes
        if frontier:
            frontier_x = [pos['x'] for pos in frontier]
            frontier_y = [pos['y'] for pos in frontier]
            
            fig.add_trace(go.Scatter(
                x=frontier_x,
                y=frontier_y,
                mode='markers',
                marker=dict(
                    symbol='circle',
                    size=12,
                    color=self.colors['frontier'],
                    opacity=0.7,
                    line=dict(width=1, color='black')
                ),
                name='Frontier Nodes',
                hoverinfo='text',
                hovertext=[f"Frontier ({x},{y})" for x, y in zip(frontier_x, frontier_y)]
            ))
        
        return fig