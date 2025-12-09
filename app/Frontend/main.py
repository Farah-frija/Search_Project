import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
from datetime import datetime
import time
import sys
import os

# ============================================
# CRITICAL: Add project root to Python path
# ============================================

# Get the absolute path to the project root
# Get absolute path to current file
current_dir = os.path.dirname(os.path.abspath(__file__))


# Go up 3 levels to project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))


# Add project root to sys.path
sys.path.insert(0, project_root)



from components.grid_visualizer import GridVisualizer


# Page configuration
st.set_page_config(
    page_title="Delivery Route Planner",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
    }
    .stButton button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
    }
    .algorithm-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.875rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .success-badge {
        background-color: #4CAF50;
        color: white;
    }
    .warning-badge {
        background-color: #FF9800;
        color: white;
    }
    .error-badge {
        background-color: #F44336;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL =  "http://localhost:8000/api/v1"

# Initialize session state
if 'current_grid' not in st.session_state:
    st.session_state.current_grid = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'performance_data' not in st.session_state:
    st.session_state.performance_data = []
if 'show_costs' not in st.session_state:
    st.session_state.show_costs = False

# Title
st.markdown('<h1 class="main-header">🚚 AI Delivery Route Planner</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/delivery.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Go to",
        ["🏠 Dashboard", "🔍 Search Visualization", "📊 Performance Analysis"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Grid"):
            st.session_state.current_grid = None
            st.rerun()
    
    with col2:
        if st.button("📊 Compare All"):
            if st.session_state.current_grid:
                st.session_state.page = "compare"
                st.rerun()
        # ADD THIS TOGGLE IN SIDEBAR:
    st.markdown("---")
    st.markdown("### Display Options")
    
    if st.button("💰 Toggle Edge Costs", use_container_width=True):
        st.session_state.show_costs = not st.session_state.show_costs
        #st.rerun()
    
    if st.session_state.show_costs:
        st.success("Edge costs: ON")
    else:
        st.info("Edge costs: OFF")
    
    st.markdown("---")
    st.markdown("### Current Grid")
    if st.session_state.current_grid:
        grid_info = st.session_state.current_grid
        st.markdown(f"**Size:** {grid_info['grid']['width']}×{grid_info['grid']['height']}")
        st.markdown(f"**Stores:** {len(grid_info['grid']['stores'])}")
        st.markdown(f"**Customers:** {len(grid_info['grid']['customers'])}")
        st.markdown(f"**Tunnels:** {len(grid_info['grid']['tunnels'])}")
    else:
        st.info("No grid loaded")
def show_dashboard():
    """Dashboard page"""
    st.markdown('<h2 class="sub-header">Dashboard Overview</h2>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 Grid Management", "⚡ Quick Search", "📈 Recent Activity"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Generate New Grid")
            
            with st.form("grid_generator"):
                col1, col2 = st.columns(2)
                with col1:
                    width = st.slider("Width", 5, 30, 10)
                    min_stores = st.slider("Min Stores", 1, 10, 2)
                    min_customers = st.slider("Min Customers", 1, 20, 5)
                    obstacle_density = st.slider("Obstacle Density", 0.0, 0.5, 0.15)
                
                with col2:
                    height = st.slider("Height", 5, 30, 10)
                    max_stores = st.slider("Max Stores", min_stores, 10, 4)
                    max_customers = st.slider("Max Customers", min_customers, 20, 8)
                    tunnel_density = st.slider("Tunnel Density", 0.0, 1.0, 0.2)
                
                generate_button = st.form_submit_button("🎲 Generate Random Grid")
                
                if generate_button:
                    with st.spinner("Generating grid..."):
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/grid/generate",
                                json={
                                    "width": width,
                                    "height": height,
                                    "min_stores": min_stores,
                                    "max_stores": max_stores,
                                    "min_customers": min_customers,
                                    "max_customers": max_customers,
                                    "obstacle_density": obstacle_density,
                                    "tunnel_density": tunnel_density
                                }
                            )
                            
                            if response.status_code == 200:
                                grid_data = response.json()
                                st.session_state.current_grid = grid_data
                                st.success("✅ Grid generated successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to generate grid: {response.text}")
                                
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
       
    
    with tab2:
        if st.session_state.current_grid:
            grid = st.session_state.current_grid
            
            st.markdown("### Quick Path Search")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                stores = grid['grid']['stores']
                store_options = {f"Store at ({s['x']},{s['y']})": s for s in stores}
                selected_store_label = st.selectbox("Select Store", list(store_options.keys()))
                selected_store = store_options[selected_store_label]
            
            with col2:
                customers = grid['grid']['customers']
                customer_options = {f"Customer at ({c['x']},{c['y']})": c for c in customers}
                selected_customer_label = st.selectbox("Select Customer", list(customer_options.keys()))
                selected_customer = customer_options[selected_customer_label]
            
            with col3:
                algorithm = st.selectbox(
                    "Algorithm",
                    ["BFS", "DFS", "UCS", "Greedy", "A*"],
                    index=4
                )
                
                algorithm_map = {
                    "BFS": "bf",
                    "DFS": "df",
                    "UCS": "uc",
                    "Greedy": "gr1",
                    "A*": "as1"
                }
            
            if st.button("🔍 Find Path", type="primary"):
                with st.spinner("Searching for path..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/search",
                            json={
                                "grid_id": grid['grid_id'],
                                "store_position": selected_store,
                                "customer_position": selected_customer,
                                "algorithm": algorithm_map[algorithm]
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.search_results.append({
                                **result,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            if result["success"]:
                                st.success(f"✅ Path found! Cost: {result['total_cost']}")
                                
                                # Show path visualization
                                visualizer = GridVisualizer(grid['grid'],show_costs=st.session_state.show_costs)
                                fig = visualizer.plot_path(result['positions'])
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("❌ No path found")
                        else:
                            st.error(f"Search failed: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("Generate or load a grid first")
    
    with tab3:
        st.markdown("### Recent Search Activity")
        
        if st.session_state.search_results:
            # Create dataframe for display
            df_data = []
            for i, result in enumerate(reversed(st.session_state.search_results[-5:])):
                df_data.append({
                    "ID": i + 1,
                    "Algorithm": result.get("algorithm", "Unknown"),
                    "Cost": result.get("total_cost", "N/A"),
                    "Nodes": result.get("nodes_expanded", 0),
                    "Time (ms)": result.get("execution_time_ms", 0),
                    "Success": "✅" if result.get("success") else "❌"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Clear button
            if st.button("Clear History"):
                st.session_state.search_results = []
                st.rerun()
        else:
            st.info("No search history yet")

def show_search_visualization():
    """Interactive search visualization page"""
    st.markdown('<h2 class="sub-header">Interactive Search Visualization</h2>', unsafe_allow_html=True)
    
    if not st.session_state.current_grid:
        st.warning("Please generate or load a grid first from the Dashboard")
        return
    
    grid = st.session_state.current_grid
    
    # Two columns layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Grid visualization
        visualizer = GridVisualizer(grid['grid'],show_costs=st.session_state.show_costs)
        fig = visualizer.create_interactive_plot()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Search Configuration")
        
        # Store and customer selection
        stores = grid['grid']['stores']
        customers = grid['grid']['customers']
        
        store_idx = st.selectbox(
            "Select Store",
            range(len(stores)),
            format_func=lambda i: f"({stores[i]['x']},{stores[i]['y']})"
        )
        
        customer_idx = st.selectbox(
            "Select Customer",
            range(len(customers)),
            format_func=lambda i: f"({customers[i]['x']},{customers[i]['y']})"
        )
        
        # Algorithm selection
        st.markdown("#### Algorithm Settings")
        
        algorithm = st.selectbox(
            "Search Algorithm",
            ["Breadth-First (BF)", "Depth-First (DF)", "Uniform Cost (UC)", 
             "Greedy (GR1) (manhattan)", "Greedy (GR2) (diagonal)", "A* (AS1) (manhattan)", "A* (AS2) (diagonal)"],
            index=6
        )
        
        algorithm_map = {
            "Breadth-First (BF)": "bf",
            "Depth-First (DF)": "df",
            "Uniform Cost (UC)": "uc",
            "Greedy (GR1) (manhattan)": "gr1",
            "Greedy (GR2) (diagonal)": "gr2",
            "A* (AS1) (manhattan)": "as1",
            "A* (AS2) (diagonal)": "as2"
        }
        

        
        # Visualization options
        st.markdown("#### Visualization Options")
        
        #show_visited = st.checkbox("Show Visited Nodes", True)
        #show_frontier = st.checkbox("Show Frontier Nodes", False)
        #animate = st.checkbox("Animate Search", False)
        
        #if animate:
            #speed = st.slider("Animation Speed", 0.1, 2.0, 0.5)
        
        # Search button
        if st.button("▶️ Run Search", type="primary", use_container_width=True):
            with st.spinner("Running search..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/search",
                        json={
                            "grid_id": grid['grid_id'],
                            "store_position": stores[store_idx],
                            "customer_position": customers[customer_idx],
                            "algorithm": algorithm_map[algorithm],
                            #"heuristic": heuristic_map[heuristic],
                            #"animate": animate
                        }
                    )
                    print(response.json())
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Store result
                        st.session_state.search_results.append({
                            **result,
                            "algorithm": algorithm,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Display results
                        if result["success"]:
                            
                            st.success(f"✅ Path Found!")
                            
                            # Metrics cards
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Cost", f"{result['total_cost']:.2f}")
                            with col2:
                                st.metric("Path Length", len(result['path']))
                            with col3:
                                st.metric("Nodes Expanded", result['nodes_expanded'])
                            
                            # Path details
                            with st.expander("Path Details"):
                                st.write("**Actions:**", " → ".join(result['path']))
                                
                                # Convert to DataFrame for visualization
                                path_df = pd.DataFrame([
                                    {"Step": i, "X": pos['x'], "Y": pos['y']}
                                    for i, pos in enumerate(result['positions'])
                                ])
                                st.dataframe(path_df)
                            
                            # Update visualization with path
                            fig = visualizer.plot_path(result['positions'])
                            st.plotly_chart(fig, use_container_width=True)
                            
                        else:
                            st.error("❌ No path found between selected points")
                            
                    else:
                        st.error(f"Search failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        


def show_performance_analysis():
    """Performance analysis page"""
    st.markdown('<h2 class="sub-header">Performance Analysis</h2>', unsafe_allow_html=True)
    
    tab2, tab3 = st.tabs(["📊 Delivery Planning", "🔍 Detailed Metrics"])
    
    
    with tab2:
        st.markdown("### Delivery Planning Analysis")
        
        if st.session_state.current_grid:
            grid = st.session_state.current_grid
            
            st.markdown(f"**Grid:** {grid['grid']['width']}×{grid['grid']['height']}")
            st.markdown(f"**Stores:** {len(grid['grid']['stores'])}")
            st.markdown(f"**Customers:** {len(grid['grid']['customers'])}")
            
            # Assignment strategy selection
            strategy = st.selectbox(
                "Assignment Strategy",
                ["Pure Cost", "Balanced"],
                index=1,
                help="Pure Cost: Minimize total delivery cost\nBalanced: Balance load across stores with cost awareness"
            )
            
            strategy_map = {
                "Pure Cost": "pure_cost",
                "Balanced": "balanced"
            }
            
            max_load_diff = st.slider(
                "Maximum Load Difference", 
                1, 5, 2,
                help="Maximum allowed difference in number of customers between stores (only for Balanced strategy)"
            )
            
            if st.button("📦 Plan Deliveries", type="primary"):
                with st.spinner("Analyzing all strategies and planning deliveries..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/delivery/plan2",
                            json={
                                "grid_id": grid['grid_id'],
                                "assignment_strategy": strategy_map[strategy],
                                "max_load_diff": max_load_diff
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            if result.get("success"):
                                # Store result in session state
                                st.session_state.plan_result = result
                                st.session_state.selected_strategy = result['best_overall_strategy']
                                st.success("✅ Comprehensive delivery analysis completed!")
                            else:
                                st.error("Analysis failed")
                                
                        else:
                            st.error(f"Planning failed: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # Display results if we have them
            if 'plan_result' in st.session_state:
                result = st.session_state.plan_result
                
                # Overall Best Strategy
                st.markdown("---")
                st.markdown(f"### 🏆 Best Overall Strategy: **{result['best_overall_strategy']}**")
                
                # Top-level metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Grid Stores", result['grid_metrics']['stores_count'])
                with col2:
                    st.metric("Grid Customers", result['grid_metrics']['customers_count'])
                with col3:
                    total_pairs = result['grid_metrics']['total_possible_pairs']
                    st.metric("Possible Pairs", total_pairs)
                with col4:
                    st.metric("Assignment Strategy", strategy)
                
                # Strategy Comparison Table
                st.markdown("### 📊 Strategy Comparison Table")
                
                # Create comparison DataFrame from the response
                comparison_data = []
                for strat_data in result['strategy_comparison']:
                    summary = strat_data['summary']
                    
                    # Calculate load imbalance
                    loads = list(strat_data['store_loads'].values())
                    if loads:
                        load_values = [load['load'] for load in loads]
                        load_imbalance = max(load_values) - min(load_values)
                    else:
                        load_imbalance = 0
                    
                    comparison_data.append({
                        "Strategy": strat_data['strategy'],
                        "Total Cost": summary['total_cost'],
                        "Avg Cost/Delivery": summary['average_cost_per_delivery'],
                        "Avg Time (ms)": summary['average_time_ms'],
                        "Avg Nodes": summary['average_nodes_expanded'],
                        "Success Rate": (summary['successful_paths']/summary['total_assignments']*100) if summary['total_assignments'] > 0 else 0,
                        "Load Imbalance": load_imbalance,
                        "Failed Paths": summary['failed_paths']
                    })
                
                df_comparison = pd.DataFrame(comparison_data)
                
                # Highlight the best strategy
                def highlight_best(row):
                    if row['Strategy'] == result['best_overall_strategy']:
                        return ['background-color: #90EE90'] * len(row)
                    return [''] * len(row)
                
                # Format the display DataFrame
                display_df = df_comparison.copy()
                display_df['Total Cost'] = display_df['Total Cost'].apply(lambda x: f"{x:.2f}")
                display_df['Avg Cost/Delivery'] = display_df['Avg Cost/Delivery'].apply(lambda x: f"{x:.2f}")
                display_df['Avg Time (ms)'] = display_df['Avg Time (ms)'].apply(lambda x: f"{x:.2f}")
                display_df['Avg Nodes'] = display_df['Avg Nodes'].apply(lambda x: f"{x:.0f}")
                display_df['Success Rate'] = display_df['Success Rate'].apply(lambda x: f"{x:.1f}%")
                
                # Apply highlighting
                styled_df = display_df.style.apply(highlight_best, axis=1)
                
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=(len(df_comparison) + 1) * 35
                )
                
                # Strategy Selection for Detailed View
                st.markdown("---")
                st.markdown("### 🔍 Detailed Strategy Analysis")
                
                # Use session state to remember selected strategy
                if 'selected_strategy' not in st.session_state:
                    st.session_state.selected_strategy = result['best_overall_strategy']
                
                strategy_options = [s["Strategy"] for s in comparison_data]
                
                # Handle case where best strategy might not be in the list
                if st.session_state.selected_strategy not in strategy_options:
                    st.session_state.selected_strategy = strategy_options[0]
                
                selected_strategy = st.selectbox(
                    "Select Strategy to View Details",
                    strategy_options,
                    index=strategy_options.index(st.session_state.selected_strategy),
                    key="strategy_selector"
                )
                
                # Update session state when selection changes
                if selected_strategy != st.session_state.selected_strategy:
                    st.session_state.selected_strategy = selected_strategy
                    # Force a rerun to update the display
                    st.rerun()
                
                # Get selected strategy data
                selected_data = next(s for s in result['strategy_comparison'] if s['strategy'] == selected_strategy)
                
                # Display selected strategy metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Cost", f"{selected_data['summary']['total_cost']:.2f}")
                with col2:
                    st.metric("Average Time", f"{selected_data['summary']['average_time_ms']:.2f}ms")
                with col3:
                    success_rate = (selected_data['summary']['successful_paths']/selected_data['summary']['total_assignments']*100) if selected_data['summary']['total_assignments'] > 0 else 0
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                with col4:
                    # Calculate load imbalance for this strategy
                    loads = list(selected_data['store_loads'].values())
                    if loads:
                        load_values = [load['load'] for load in loads]
                        load_imbalance = max(load_values) - min(load_values)
                    else:
                        load_imbalance = 0
                    st.metric("Load Imbalance", load_imbalance)
                
                # Store Loads Visualization
                st.markdown("#### 📦 Store Load Distribution")
                loads_df = pd.DataFrame([
                    {
                        "Store": store_key,
                        "Load": load_data['load'],
                        "Percentage": f"{load_data['percentage']:.1f}%"
                    }
                    for store_key, load_data in selected_data['store_loads'].items()
                ])
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    fig_loads = px.bar(
                        loads_df,
                        x="Store",
                        y="Load",
                        title=f"Store Load Distribution - {selected_strategy}",
                        text="Load",
                        color="Load",
                        color_continuous_scale="viridis"
                    )
                    fig_loads.update_layout(yaxis_title="Number of Customers")
                    st.plotly_chart(fig_loads, use_container_width=True)
                
                with col2:
                    st.dataframe(loads_df[['Store', 'Load', 'Percentage']], hide_index=True)
                
                # Detailed Assignments by Store
                st.markdown("#### 📍 Store Assignments")
                
                stores = list(selected_data['store_assignments'].keys())
                store_tabs = st.tabs(stores)
                
                for i, store_key in enumerate(stores):
                    with store_tabs[i]:
                        store_info = selected_data['store_assignments'][store_key]
                        
                        if store_info['store_position']:
                            st.write(f"**📍 Store Position:** ({store_info['store_position']['x']}, {store_info['store_position']['y']})")
                        st.write(f"**👥 Customers Assigned:** {store_info['customer_count']}")
                        st.write(f"**💰 Total Store Cost:** {store_info['total_store_cost']:.2f}")
                        
                        if store_info['customer_count'] > 0:
                            st.write(f"**📊 Avg Cost per Customer:** {store_info['total_store_cost']/store_info['customer_count']:.2f}")
                        
                        if store_info['customers']:
                            # Create a table of customers
                            customers_data = []
                            for cust in store_info['customers']:
                                customers_data.append({
                                    "Customer": f"Customer {cust['customer_idx']}",
                                    "Position": f"({cust['position']['x']}, {cust['position']['y']})",
                                    "Cost": cust['path_cost'],
                                    "Path Length": cust['path_length'],
                                    "Time (ms)": f"{cust['time_ms']:.2f}",
                                    "Nodes": cust['nodes_expanded']
                                })
                            
                            customers_df = pd.DataFrame(customers_data)
                            st.dataframe(customers_df, use_container_width=True, hide_index=True)
                            
                            # Show path visualizations
                            st.markdown("#### 🔍 Path Visualizations")
                            
                            for cust_idx, cust in enumerate(store_info['customers']):
                                with st.expander(f"📊 View Path for Customer {cust['customer_idx']}"):
                                    # Display metrics
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.write(f"**Cost:** {cust['path_cost']:.2f}")
                                    with col2:
                                        st.write(f"**Path Length:** {cust['path_length']} steps")
                                    with col3:
                                        st.write(f"**Time:** {cust['time_ms']:.2f} ms")
                                    with col4:
                                        st.write(f"**Nodes Expanded:** {cust['nodes_expanded']}")
                                    
                                    # Visualize the path on the grid
                                    if cust.get('path_actions'):
                                        # Create a path visualization
                                        st.write(f"**Path Actions:** `{cust['path_actions']}`")
                                        
                                        # Show path on the grid
                                        if st.session_state.current_grid:
                                            # Get grid data
                                            grid_data = st.session_state.current_grid['grid']
                                            
                                            # Create a simplified grid visualization
                                            visualizer = GridVisualizer(grid_data,show_costs=st.session_state.show_costs)
                                            
                                            # Get store position
                                            store_pos = store_info['store_position']
                                            
                                            # Get customer position
                                            customer_pos = cust['position']
                                            
                                            # Create positions for the path
                                            # For now, just show store and customer positions
                                            # You could parse the path_actions to show full path
                                            path_positions = [
                                                {"x": store_pos['x'], "y": store_pos['y']},
                                                {"x": customer_pos['x'], "y": customer_pos['y']}
                                            ]
                                            
                                            # Create custom markers for this specific path
                                            fig = visualizer.create_interactive_plot()
                                            
                                            # Add store marker
                                            fig.add_trace(go.Scatter(
                                                x=[store_pos['x']],
                                                y=[store_pos['y']],
                                                mode='markers',
                                                marker=dict(
                                                    symbol='square',
                                                    size=20,
                                                    color='blue',
                                                    line=dict(width=2, color='white')
                                                ),
                                                name=f"Store {store_key.replace('store_', '')}",
                                                showlegend=True
                                            ))
                                            
                                            # Add customer marker
                                            fig.add_trace(go.Scatter(
                                                x=[customer_pos['x']],
                                                y=[customer_pos['y']],
                                                mode='markers',
                                                marker=dict(
                                                    symbol='circle',
                                                    size=20,
                                                    color='green',
                                                    line=dict(width=2, color='white')
                                                ),
                                                name=f"Customer {cust['customer_idx']}",
                                                showlegend=True
                                            ))
                                            
                                            # Try to parse and show the path if possible
                                            if cust['path_actions'] and cust['path_actions'] != "NO_PATH":
                                                actions = cust['path_actions'].split(',')
                                                current_x, current_y = store_pos['x'], store_pos['y']
                                                path_x, path_y = [current_x], [current_y]
                                                
                                                for action in actions:
                                                    if action == 'right':
                                                        current_x += 1
                                                    elif action == 'left':
                                                        current_x -= 1
                                                    elif action == 'up':
                                                        current_y += 1
                                                    elif action == 'down':
                                                        current_y -= 1
                                                    path_x.append(current_x)
                                                    path_y.append(current_y)
                                                
                                                # Add path line
                                                fig.add_trace(go.Scatter(
                                                    x=path_x,
                                                    y=path_y,
                                                    mode='lines+markers',
                                                    line=dict(width=3, color='red'),
                                                    marker=dict(size=8, color='orange'),
                                                    name=f"Path to Customer {cust['customer_idx']}",
                                                    showlegend=True
                                                ))
                                            
                                            # Update layout for better visualization
                                            fig.update_layout(
                                                title=f"Path from {store_key} to Customer {cust['customer_idx']}",
                                                showlegend=True,
                                                width=500,
                                                height=500
                                            )
                                            
                                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No customers assigned to this store")
                
                # Strategy Performance Analysis (Simplified)
                st.markdown("---")
                st.markdown("### 📈 Strategy Performance Comparison")
                
                # Create comparison DataFrame for analysis
                analysis_df = df_comparison.copy()
                
                # Create side-by-side comparison charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Cost comparison chart
                    fig_cost = go.Figure()
                    fig_cost.add_trace(go.Bar(
                        x=analysis_df['Strategy'],
                        y=analysis_df['Total Cost'],
                        marker_color=['#4CAF50' if s == result['best_overall_strategy'] else '#2196F3' for s in analysis_df['Strategy']],
                        text=[f"{c:.1f}" for c in analysis_df['Total Cost']],
                        textposition='auto',
                        name="Total Cost"
                    ))
                    
                    fig_cost.update_layout(
                        title="Total Cost by Strategy (Lower is Better)",
                        xaxis_title="Strategy",
                        yaxis_title="Total Cost",
                        showlegend=False
                    )
                    st.plotly_chart(fig_cost, use_container_width=True)
                
                with col2:
                    # Time comparison chart
                    fig_time = go.Figure()
                    fig_time.add_trace(go.Bar(
                        x=analysis_df['Strategy'],
                        y=analysis_df['Avg Time (ms)'],
                        marker_color=['#4CAF50' if s == result['best_overall_strategy'] else '#FF9800' for s in analysis_df['Strategy']],
                        text=[f"{t:.1f}ms" for t in analysis_df['Avg Time (ms)']],
                        textposition='auto',
                        name="Avg Time"
                    ))
                    
                    fig_time.update_layout(
                        title="Average Time by Strategy (Lower is Better)",
                        xaxis_title="Strategy",
                        yaxis_title="Average Time (ms)",
                        showlegend=False
                    )
                    st.plotly_chart(fig_time, use_container_width=True)
                
                # Combined metrics chart
                st.markdown("#### Performance Metrics Overview")
                
                # Create a grouped bar chart for key metrics
                fig_combined = go.Figure()
                
                # Normalize metrics for better comparison
                metrics_to_show = ['Total Cost', 'Avg Time (ms)', 'Avg Nodes']
                
                for metric in metrics_to_show:
                    max_val = analysis_df[metric].max()
                    min_val = analysis_df[metric].min()
                    if max_val > min_val:
                        normalized = (analysis_df[metric] - min_val) / (max_val - min_val)
                    else:
                        normalized = [0.5] * len(analysis_df)
                    
                    fig_combined.add_trace(go.Bar(
                        name=metric,
                        x=analysis_df['Strategy'],
                        y=normalized,
                        text=[f"{v:.1f}" for v in analysis_df[metric]],
                        textposition='auto'
                    ))
                
                fig_combined.update_layout(
                    barmode='group',
                    title="Normalized Performance Metrics (Lower is Better)",
                    xaxis_title="Strategy",
                    yaxis_title="Normalized Value",
                    showlegend=True
                )
                st.plotly_chart(fig_combined, use_container_width=True)
                
                # Summary insights
                st.markdown("#### 💡 Key Insights")
                
                # Find best in each category
                best_cost = analysis_df.loc[analysis_df['Total Cost'].idxmin()]
                best_time = analysis_df.loc[analysis_df['Avg Time (ms)'].idxmin()]
                #best_success = analysis_df.loc[analysis_df['Success Rate'].idxmax()]
                
                insight_cols = st.columns(2)
                with insight_cols[0]:
                    st.metric(
                        "Most Cost-Effective",
                        best_cost['Strategy'],
                        delta=f"Cost: {best_cost['Total Cost']:.1f}"
                    )
                with insight_cols[1]:
                    st.metric(
                        "Fastest",
                        best_time['Strategy'],
                        delta=f"Time: {best_time['Avg Time (ms)']:.1f}ms"
                    )

                
                # Download options
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Download Analysis Report"):
                        # Create a downloadable report
                        report = {
                            'timestamp': datetime.now().isoformat(),
                            'grid_id': grid['grid_id'],
                            'assignment_strategy': strategy,
                            'best_strategy': result['best_overall_strategy'],
                            'strategy_comparison': analysis_df.to_dict('records'),
                            'selected_strategy_details': selected_data
                        }
                        
                        # Convert to JSON for download
                        json_str = json.dumps(report, indent=2, default=str)
                        st.download_button(
                            label="Download JSON Report",
                            data=json_str,
                            file_name=f"delivery_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
                with col2:
                    if st.button("🔄 Run New Analysis"):
                        # Clear previous results
                        if 'plan_result' in st.session_state:
                            del st.session_state.plan_result
                        if 'selected_strategy' in st.session_state:
                            del st.session_state.selected_strategy
                        st.rerun()
                            
            else:
                st.info("Generate or load a grid first")
                
            # Quick explanation of strategies
            with st.expander("📖 About Search Strategies"):
                st.markdown("""
                **Search Strategies Explained:**
                
                | Strategy | Description | Best For |
                |----------|-------------|----------|
                | **BF** | Breadth-First Search | Finding shortest path in steps |
                | **DF** | Depth-First Search | Exploring deep branches |
                | **ID** | Iterative Deepening | Memory-efficient shortest path |
                | **UC** | Uniform Cost Search | Finding cheapest path |
                | **GR1/GR2** | Greedy Search | Quick approximate solutions |
                | **AS1/AS2** | A* Search | Optimal balance of speed & accuracy |
                
                **Performance Indicators:**
                - **Total Cost**: Sum of all path costs (lower is better)
                - **Avg Time**: Average computation time per path
                - **Success Rate**: Percentage of paths found
                - **Load Imbalance**: Difference between most/least loaded stores
                """)
    
    with tab3:
        st.markdown("### Detailed Metrics Explorer")
        
        if st.session_state.search_results:
            # Convert to DataFrame
            metrics_df = pd.DataFrame([
                {
                    "Algorithm": r.get("algorithm", "Unknown"),
                    "Cost": r.get("total_cost", 0),
                    "Nodes": r.get("nodes_expanded", 0),
                    "Time (ms)": r.get("execution_time_ms", 0),
                    "Success": r.get("success", False),
                    "Timestamp": r.get("timestamp", "")
                }
                for r in st.session_state.search_results
            ])
            
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                selected_algorithms = st.multiselect(
                    "Filter by Algorithm",
                    metrics_df["Algorithm"].unique(),
                    default=metrics_df["Algorithm"].unique()
                )
            
            with col2:
                success_filter = st.selectbox(
                    "Success Filter",
                    ["All", "Successful Only", "Failed Only"]
                )
            
            # Apply filters
            filtered_df = metrics_df[metrics_df["Algorithm"].isin(selected_algorithms)]
            if success_filter == "Successful Only":
                filtered_df = filtered_df[filtered_df["Success"]]
            elif success_filter == "Failed Only":
                filtered_df = filtered_df[~filtered_df["Success"]]
            
            # Display metrics
            st.dataframe(filtered_df, use_container_width=True)
            
            # Statistics
            if not filtered_df.empty:
                st.markdown("#### Statistics")
                
                stats_cols = st.columns(4)
                metrics_to_show = ["Cost", "Nodes", "Time (ms)"]
                
                for i, metric in enumerate(metrics_to_show):
                    if metric in filtered_df.columns:
                        with stats_cols[i]:
                            st.metric(
                                f"Avg {metric}",
                                f"{filtered_df[metric].mean():.2f}",
                                f"±{filtered_df[metric].std():.2f}"
                            )
        else:
            st.info("No search data available")

def show_configuration():
    """Configuration page"""
    st.markdown('<h2 class="sub-header">System Configuration</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["⚙️ API Settings", "🎨 Visualization", "💾 Data Management"])
    
    with tab1:
        st.markdown("### API Configuration")
        
        api_url = st.text_input(
            "API Base URL",
            value=st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")
        )
        
        if st.button("Test Connection"):
            try:
                response = requests.get(f"{api_url}/health")
                if response.status_code == 200:
                    st.success("✅ API is reachable")
                else:
                    st.error(f"❌ API returned status {response.status_code}")
            except Exception as e:
                st.error(f"❌ Cannot connect to API: {str(e)}")
        
        st.markdown("---")
        st.markdown("### Cache Settings")
        
        cache_enabled = st.checkbox("Enable Search Cache", True)
        cache_ttl = st.number_input("Cache TTL (seconds)", 60, 3600, 300)
        
        if st.button("Clear Cache"):
            st.session_state.search_results = []
            st.session_state.performance_data = []
            st.success("Cache cleared!")
    
    with tab2:
        st.markdown("### Visualization Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "Color Theme",
                ["Light", "Dark", "Blue", "Green", "Red"],
                index=0
            )
            
            grid_size = st.slider("Grid Cell Size", 20, 100, 40)
            show_labels = st.checkbox("Show Coordinate Labels", True)
        
        with col2:
            animation_speed = st.slider("Default Animation Speed", 0.1, 2.0, 0.5)
            highlight_path = st.checkbox("Highlight Path", True)
            show_obstacles = st.checkbox("Show Obstacles", True)
        
        if st.button("Apply Visualization Settings"):
            st.success("Settings applied (Note: Some settings require page refresh)")
    
    with tab3:
        st.markdown("### Data Management")
        
        # Export data
        if st.button("📥 Export All Data"):
            export_data = {
                "grids": [st.session_state.current_grid] if st.session_state.current_grid else [],
                "search_results": st.session_state.search_results,
                "performance_data": st.session_state.performance_data,
                "exported_at": datetime.now().isoformat()
            }
            
            st.download_button(
                label="Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"delivery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Import data
        uploaded_file = st.file_uploader("Import JSON Data", type=["json"])
        if uploaded_file is not None:
            try:
                import_data = json.load(uploaded_file)
                
                if "grids" in import_data and import_data["grids"]:
                    st.session_state.current_grid = import_data["grids"][0]
                
                if "search_results" in import_data:
                    st.session_state.search_results = import_data["search_results"]
                
                if "performance_data" in import_data:
                    st.session_state.performance_data = import_data["performance_data"]
                
                st.success("✅ Data imported successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error importing data: {str(e)}")
        
        st.markdown("---")
        st.markdown("### Reset Data")
        
        if st.button("🔄 Reset All Data", type="secondary"):
            st.session_state.clear()
            st.rerun()


# Main content based on selected page
if page == "🏠 Dashboard":
    show_dashboard()
elif page == "🔍 Search Visualization":
    show_search_visualization()
elif page == "📊 Performance Analysis":
    show_performance_analysis()



if __name__ == "__main__":
    # This would be run as: streamlit run app/frontend/main.py
    pass