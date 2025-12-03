# app/frontend/components/charts.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st

class DeliveryCharts:
    """Chart components for delivery route planning visualization"""
    
    @staticmethod
    def create_grid_chart(grid_data: Dict, path_positions: List[Dict] = None,
                         visited_positions: List[Dict] = None,
                         frontier_positions: List[Dict] = None) -> go.Figure:
        """
        Create grid visualization chart
        
        Args:
            grid_data: Grid data dictionary
            path_positions: List of path positions (for highlighting)
            visited_positions: List of visited positions
            frontier_positions: List of frontier positions
            
        Returns:
            Plotly Figure object
        """
        if not grid_data or 'grid' not in grid_data:
            return go.Figure()
        
        grid = grid_data['grid']
        width = grid.get('width', 10)
        height = grid.get('height', 10)
        
        fig = go.Figure()
        
        # ===== GRID BACKGROUND =====
        # Add vertical grid lines
        for x in range(width + 1):
            fig.add_trace(go.Scatter(
                x=[x, x], y=[0, height],
                mode='lines',
                line=dict(color='lightgray', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add horizontal grid lines
        for y in range(height + 1):
            fig.add_trace(go.Scatter(
                x=[0, width], y=[y, y],
                mode='lines',
                line=dict(color='lightgray', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # ===== OBSTACLES (if available) =====
        if 'traffic_edges' in grid:
            obstacles = []
            for edge in grid['traffic_edges']:
                if edge.get('cost', 1) == 0:  # Obstacle
                    x1, y1 = edge['from']['x'], edge['from']['y']
                    x2, y2 = edge['to']['x'], edge['to']['y']
                    
                    # Add obstacle line
                    fig.add_trace(go.Scatter(
                        x=[x1, x2], y=[y1, y2],
                        mode='lines',
                        line=dict(color='#424242', width=3),
                        name='Obstacle',
                        hoverinfo='skip',
                        showlegend=True if not obstacles else False
                    ))
                    
                    # Mark center point
                    obstacles.append(((x1 + x2) / 2, (y1 + y2) / 2))
            
            if obstacles:
                obs_x, obs_y = zip(*obstacles)
                fig.add_trace(go.Scatter(
                    x=obs_x, y=obs_y,
                    mode='markers',
                    marker=dict(
                        symbol='x',
                        size=12,
                        color='#424242',
                        line=dict(width=2)
                    ),
                    name='Obstacle Center',
                    hoverinfo='skip',
                    showlegend=False
                ))
        
        # ===== TUNNELS (if available) =====
        if 'tunnels' in grid:
            for tunnel in grid['tunnels']:
                x1, y1 = tunnel['entrance']['x'], tunnel['entrance']['y']
                x2, y2 = tunnel['exit']['x'], tunnel['exit']['y']
                
                # Add tunnel connection (dashed line)
                fig.add_trace(go.Scatter(
                    x=[x1, x2], y=[y1, y2],
                    mode='lines',
                    line=dict(
                        color='#AB47BC',
                        width=2,
                        dash='dash'
                    ),
                    name='Tunnel',
                    hoverinfo='text',
                    hovertext=f"Tunnel: ({x1},{y1}) ↔ ({x2},{y2})",
                    showlegend=True
                ))
                
                # Add tunnel markers
                fig.add_trace(go.Scatter(
                    x=[x1, x2], y=[y1, y2],
                    mode='markers',
                    marker=dict(
                        symbol='diamond',
                        size=10,
                        color='#AB47BC',
                        line=dict(width=1, color='white')
                    ),
                    name='Tunnel Entrance/Exit',
                    hoverinfo='text',
                    hovertext=[f"Entrance ({x1},{y1})", f"Exit ({x2},{y2})"],
                    showlegend=False
                ))
        
        # ===== VISITED NODES =====
        if visited_positions:
            visited_x = [pos['x'] for pos in visited_positions]
            visited_y = [pos['y'] for pos in visited_positions]
            
            fig.add_trace(go.Scatter(
                x=visited_x, y=visited_y,
                mode='markers',
                marker=dict(
                    symbol='square',
                    size=8,
                    color='#E0E0E0',
                    opacity=0.6
                ),
                name='Visited Nodes',
                hoverinfo='text',
                hovertext=[f"Visited ({x},{y})" for x, y in zip(visited_x, visited_y)],
                showlegend=True
            ))
        
        # ===== FRONTIER NODES =====
        if frontier_positions:
            frontier_x = [pos['x'] for pos in frontier_positions]
            frontier_y = [pos['y'] for pos in frontier_positions]
            
            fig.add_trace(go.Scatter(
                x=frontier_x, y=frontier_y,
                mode='markers',
                marker=dict(
                    symbol='circle',
                    size=10,
                    color='#B3E5FC',
                    opacity=0.7,
                    line=dict(width=1, color='black')
                ),
                name='Frontier Nodes',
                hoverinfo='text',
                hovertext=[f"Frontier ({x},{y})" for x, y in zip(frontier_x, frontier_y)],
                showlegend=True
            ))
        
        # ===== PATH =====
        if path_positions:
            path_x = [pos['x'] for pos in path_positions]
            path_y = [pos['y'] for pos in path_positions]
            
            # Path line
            fig.add_trace(go.Scatter(
                x=path_x, y=path_y,
                mode='lines+markers',
                line=dict(
                    color='#4CAF50',
                    width=3
                ),
                marker=dict(
                    size=8,
                    color='#4CAF50',
                    symbol='circle'
                ),
                name='Delivery Path',
                hoverinfo='text',
                hovertext=[f"Step {i}: ({x},{y})" for i, (x, y) in enumerate(zip(path_x, path_y))],
                showlegend=True
            ))
            
            # Start and end markers
            if len(path_positions) >= 2:
                fig.add_trace(go.Scatter(
                    x=[path_x[0], path_x[-1]],
                    y=[path_y[0], path_y[-1]],
                    mode='markers',
                    marker=dict(
                        symbol=['triangle-right', 'star'],
                        size=15,
                        color=['#FFA726', '#42A5F5'],
                        line=dict(width=2, color='black')
                    ),
                    name='Start/End',
                    hovertext=['Start', 'End'],
                    showlegend=False
                ))
        
        # ===== STORES =====
        if 'stores' in grid and grid['stores']:
            store_x = [s['x'] for s in grid['stores']]
            store_y = [s['y'] for s in grid['stores']]
            
            fig.add_trace(go.Scatter(
                x=store_x, y=store_y,
                mode='markers+text',
                marker=dict(
                    symbol='square',
                    size=15,
                    color='#FFA726',
                    line=dict(width=2, color='black')
                ),
                text=[f"S{i+1}" for i in range(len(store_x))],
                textposition="top center",
                name='Stores',
                hoverinfo='text',
                hovertext=[f"Store {i+1} at ({x},{y})" for i, (x, y) in enumerate(zip(store_x, store_y))],
                showlegend=True
            ))
        
        # ===== CUSTOMERS =====
        if 'customers' in grid and grid['customers']:
            customer_x = [c['x'] for c in grid['customers']]
            customer_y = [c['y'] for c in grid['customers']]
            
            fig.add_trace(go.Scatter(
                x=customer_x, y=customer_y,
                mode='markers+text',
                marker=dict(
                    symbol='circle',
                    size=13,
                    color='#42A5F5',
                    line=dict(width=2, color='black')
                ),
                text=[f"C{i+1}" for i in range(len(customer_x))],
                textposition="top center",
                name='Customers',
                hoverinfo='text',
                hovertext=[f"Customer {i+1} at ({x},{y})" for i, (x, y) in enumerate(zip(customer_x, customer_y))],
                showlegend=True
            ))
        
        # ===== LAYOUT =====
        fig.update_layout(
            title=dict(
                text="Delivery Grid Visualization",
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                range=[-0.5, width + 0.5],
                showgrid=False,
                zeroline=False,
                showline=True,
                mirror=True,
                tickmode='linear',
                tick0=0,
                dtick=1,
                title="X Coordinate"
            ),
            yaxis=dict(
                range=[-0.5, height + 0.5],
                showgrid=False,
                zeroline=False,
                showline=True,
                mirror=True,
                tickmode='linear',
                tick0=0,
                dtick=1,
                scaleanchor="x",
                scaleratio=1,
                title="Y Coordinate"
            ),
            plot_bgcolor='white',
            width=700,
            height=700,
            hovermode='closest',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02,
                bgcolor='rgba(255, 255, 255, 0.8)'
            ),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    @staticmethod
    def create_algorithm_comparison_chart(comparison_data: List[Dict]) -> go.Figure:
        """
        Create algorithm comparison chart
        
        Args:
            comparison_data: List of algorithm comparison results
            
        Returns:
            Plotly Figure object
        """
        if not comparison_data:
            return go.Figure()
        
        # Convert to DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Filter successful searches
        successful_df = df[df['success']].copy()
        
        if successful_df.empty:
            # Create empty chart with message
            fig = go.Figure()
            fig.update_layout(
                title="No successful searches to compare",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[dict(
                    text="Run successful searches first",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )]
            )
            return fig
        
        # Create grouped bar chart
        fig = go.Figure()
        
        # Add bars for each metric
        colors = ['#1E88E5', '#43A047', '#FB8C00', '#E53935']
        
        metrics = [
            ('cost', 'Path Cost', colors[0]),
            ('nodes_expanded', 'Nodes Expanded', colors[1]),
            ('execution_time_ms', 'Time (ms)', colors[2]),
            ('path_length', 'Path Length', colors[3])
        ]
        
        for i, (metric, name, color) in enumerate(metrics):
            if metric in successful_df.columns:
                fig.add_trace(go.Bar(
                    name=name,
                    x=successful_df['algorithm'],
                    y=successful_df[metric],
                    marker_color=color,
                    opacity=0.8,
                    text=successful_df[metric].round(2),
                    textposition='auto',
                    hovertemplate=f"<b>%{{x}}</b><br>{name}: %{{y:.2f}}<extra></extra>"
                ))
        
        fig.update_layout(
            title=dict(
                text="Algorithm Performance Comparison",
                x=0.5,
                xanchor='center'
            ),
            barmode='group',
            xaxis=dict(
                title="Algorithm",
                tickangle=-45
            ),
            yaxis=dict(
                title="Value"
            ),
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_performance_radar_chart(algorithm_stats: Dict[str, Dict]) -> go.Figure:
        """
        Create radar chart for algorithm performance
        
        Args:
            algorithm_stats: Dictionary of algorithm statistics
            
        Returns:
            Plotly Figure object
        """
        if not algorithm_stats:
            return go.Figure()
        
        fig = go.Figure()
        
        # Normalize data for radar chart
        algorithms = list(algorithm_stats.keys())
        
        # Define metrics to show (lower is better for all)
        metrics = ['avg_cost', 'avg_nodes', 'avg_time_ms']
        metric_names = ['Cost', 'Nodes', 'Time (ms)']
        
        for algo in algorithms:
            stats = algorithm_stats[algo]
            values = []
            
            for metric in metrics:
                if metric in stats:
                    values.append(stats[metric])
                else:
                    values.append(0)
            
            # Add trace for this algorithm
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metric_names,
                fill='toself',
                name=algo,
                hovertemplate="<b>%{theta}</b>: %{r:.2f}<extra></extra>"
            ))
        
        fig.update_layout(
            title=dict(
                text="Algorithm Performance Radar Chart",
                x=0.5,
                xanchor='center'
            ),
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([max(v) for v in [
                        [algorithm_stats[algo].get(metric, 0) for metric in metrics]
                        for algo in algorithms
                    ] if v]) * 1.1]
                )
            ),
            showlegend=True,
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_search_progress_chart(search_history: List[Dict]) -> go.Figure:
        """
        Create search progress over time chart
        
        Args:
            search_history: List of search results
            
        Returns:
            Plotly Figure object
        """
        if not search_history:
            return go.Figure()
        
        # Convert to DataFrame
        df = pd.DataFrame(search_history)
        
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            return go.Figure()
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create line chart
        fig = go.Figure()
        
        # Separate by algorithm
        algorithms = df['algorithm'].unique()
        
        for algo in algorithms:
            algo_df = df[df['algorithm'] == algo]
            
            # Success rate over time
            algo_df['success_rate'] = algo_df['success'].expanding().mean()
            
            fig.add_trace(go.Scatter(
                x=algo_df['timestamp'],
                y=algo_df['success_rate'],
                mode='lines+markers',
                name=f"{algo} Success Rate",
                line=dict(width=2),
                marker=dict(size=6),
                hovertemplate="<b>%{x}</b><br>Success Rate: %{y:.2%}<extra></extra>"
            ))
        
        fig.update_layout(
            title=dict(
                text="Search Success Rate Over Time",
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="Time",
                tickformat='%H:%M'
            ),
            yaxis=dict(
                title="Success Rate",
                tickformat='.0%'
            ),
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_cost_distribution_chart(search_results: List[Dict]) -> go.Figure:
        """
        Create cost distribution histogram
        
        Args:
            search_results: List of search results
            
        Returns:
            Plotly Figure object
        """
        if not search_results:
            return go.Figure()
        
        # Filter successful searches with cost data
        costs = []
        algorithms = []
        
        for result in search_results:
            if result.get('success') and 'cost' in result:
                costs.append(result['cost'])
                algorithms.append(result.get('algorithm', 'Unknown'))
        
        if not costs:
            return go.Figure()
        
        # Create histogram
        fig = px.histogram(
            x=costs,
            color=algorithms,
            nbins=20,
            title="Path Cost Distribution",
            labels={'x': 'Path Cost', 'color': 'Algorithm'},
            opacity=0.7
        )
        
        fig.update_layout(
            height=400,
            bargap=0.1,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_heatmap_grid(grid_data: Dict, heatmap_values: Dict) -> go.Figure:
        """
        Create heatmap overlay on grid
        
        Args:
            grid_data: Grid data
            heatmap_values: Dictionary of position -> value for heatmap
            
        Returns:
            Plotly Figure object
        """
        if not grid_data or 'grid' not in grid_data:
            return go.Figure()
        
        grid = grid_data['grid']
        width = grid.get('width', 10)
        height = grid.get('height', 10)
        
        # Create heatmap matrix
        heatmap_matrix = np.zeros((height, width))
        
        for (x, y), value in heatmap_values.items():
            if 0 <= x < width and 0 <= y < height:
                heatmap_matrix[y, x] = value
        
        # Create heatmap figure
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_matrix,
            colorscale='Viridis',
            showscale=True,
            hoverinfo='z',
            hovertemplate='Position: (%{x},%{y})<br>Value: %{z:.2f}<extra></extra>'
        ))
        
        # Overlay grid
        fig.update_xaxes(
            range=[-0.5, width - 0.5],
            tickmode='linear',
            tick0=0,
            dtick=1,
            constrain='domain'
        )
        
        fig.update_yaxes(
            range=[-0.5, height - 0.5],
            tickmode='linear',
            tick0=0,
            dtick=1,
            scaleanchor="x",
            scaleratio=1
        )
        
        fig.update_layout(
            title=dict(
                text="Search Heatmap",
                x=0.5,
                xanchor='center'
            ),
            width=600,
            height=600,
            xaxis=dict(title="X"),
            yaxis=dict(title="Y"),
            plot_bgcolor='white'
        )
        
        return fig
    
    @staticmethod
    def render_algorithm_stats_table(algorithm_stats: Dict[str, Dict]) -> None:
        """
        Render algorithm statistics table
        
        Args:
            algorithm_stats: Dictionary of algorithm statistics
        """
        if not algorithm_stats:
            st.info("No algorithm statistics available")
            return
        
        # Prepare table data
        table_data = []
        
        for algo, stats in algorithm_stats.items():
            table_data.append({
                "Algorithm": algo,
                "Total Searches": stats.get('total_searches', 0),
                "Success Rate": f"{stats.get('success_rate', 0):.1%}",
                "Avg Cost": f"{stats.get('avg_cost', 0):.2f}",
                "Avg Nodes": f"{stats.get('avg_nodes', 0):.0f}",
                "Avg Time (ms)": f"{stats.get('avg_time_ms', 0):.1f}"
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(table_data)
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Success Rate": st.column_config.ProgressColumn(
                    "Success Rate",
                    help="Percentage of successful searches",
                    format="%.1f%%",
                    min_value=0,
                    max_value=1
                )
            }
        )