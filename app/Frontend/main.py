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

# Title
st.markdown('<h1 class="main-header">🚚 AI Delivery Route Planner</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/delivery.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Go to",
        ["🏠 Dashboard", "🔍 Search Visualization", "📊 Performance Analysis", "⚙️ Configuration"],
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
                                visualizer = GridVisualizer(grid['grid'])
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
        visualizer = GridVisualizer(grid['grid'])
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
             "Greedy (GR1)", "Greedy (GR2)", "A* (AS1)", "A* (AS2)"],
            index=6
        )
        
        algorithm_map = {
            "Breadth-First (BF)": "bf",
            "Depth-First (DF)": "df",
            "Uniform Cost (UC)": "uc",
            "Greedy (GR1)": "gr1",
            "Greedy (GR2)": "gr2",
            "A* (AS1)": "as1",
            "A* (AS2)": "as2"
        }
        
        heuristic = st.selectbox(
            "Heuristic (for informed search)",
            ["Manhattan", "Euclidean", "Diagonal", "Zero"],
            index=0
        )
        
        heuristic_map = {
            "Manhattan": "manhattan",
            "Euclidean": "euclidean",
            "Diagonal": "diagonal",
            "Zero": "zero"
        }
        
        # Visualization options
        st.markdown("#### Visualization Options")
        
        show_visited = st.checkbox("Show Visited Nodes", True)
        show_frontier = st.checkbox("Show Frontier Nodes", False)
        animate = st.checkbox("Animate Search", False)
        
        if animate:
            speed = st.slider("Animation Speed", 0.1, 2.0, 0.5)
        
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
                            "heuristic": heuristic_map[heuristic],
                            "animate": animate
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
        
        # Compare algorithms button
        if st.button("📊 Compare All Algorithms", use_container_width=True):
            with st.spinner("Comparing algorithms..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/search/compare",
                        params={
                            "grid_id": grid['grid_id'],
                            "store_position": stores[store_idx],
                            "customer_position": customers[customer_idx]
                        }
                    )
                    
                    if response.status_code == 200:
                        comparison = response.json()
                        st.session_state.performance_data = comparison["comparison"]
                        
                        # Show comparison chart
                        st.markdown("### Algorithm Comparison")
                        
                        df = pd.DataFrame(comparison["comparison"])
                        fig = px.bar(
                            df[df["success"]],
                            x="algorithm",
                            y="total_cost",
                            color="execution_time_ms",
                            title="Algorithm Performance Comparison",
                            labels={
                                "algorithm": "Algorithm",
                                "total_cost": "Path Cost",
                                "execution_time_ms": "Execution Time (ms)"
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    else:
                        st.error(f"Comparison failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def show_performance_analysis():
    """Performance analysis page"""
    st.markdown('<h2 class="sub-header">Performance Analysis</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Algorithm Benchmarks", "📊 Delivery Planning", "🔍 Detailed Metrics"])
    
    with tab1:
        st.markdown("### Algorithm Performance Comparison")
        
        if st.session_state.performance_data:
            df = pd.DataFrame(st.session_state.performance_data)
            
            # Filter successful searches
            successful = df[df["success"]]
            
            if not successful.empty:
                # Create comparison chart
                fig = go.Figure()
                
                # Add bars for each metric
                fig.add_trace(go.Bar(
                    name="Path Cost",
                    x=successful["algorithm"],
                    y=successful["total_cost"],
                    marker_color='indianred'
                ))
                
                fig.add_trace(go.Bar(
                    name="Nodes Expanded",
                    x=successful["algorithm"],
                    y=successful["nodes_expanded"],
                    marker_color='lightsalmon'
                ))
                
                fig.add_trace(go.Bar(
                    name="Execution Time (ms)",
                    x=successful["algorithm"],
                    y=successful["execution_time_ms"],
                    marker_color='lightblue'
                ))
                
                fig.update_layout(
                    barmode='group',
                    title="Algorithm Performance Metrics",
                    xaxis_title="Algorithm",
                    yaxis_title="Value",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    best_cost = successful.loc[successful["total_cost"].idxmin()]
                    st.metric(
                        "Best Cost",
                        f"{best_cost['total_cost']:.2f}",
                        best_cost["algorithm"]
                    )
                
                with col2:
                    fastest = successful.loc[successful["execution_time_ms"].idxmin()]
                    st.metric(
                        "Fastest",
                        f"{fastest['execution_time_ms']:.1f} ms",
                        fastest["algorithm"]
                    )
                
                with col3:
                    most_efficient = successful.loc[successful["nodes_expanded"].idxmin()]
                    st.metric(
                        "Most Efficient",
                        f"{most_efficient['nodes_expanded']:,}",
                        most_efficient["algorithm"]
                    )
            else:
                st.info("No successful searches to compare")
        else:
            st.info("Run some searches first to see performance data")
        
        # Run benchmark button
        if st.button("🏃 Run New Benchmark"):
            if st.session_state.current_grid:
                st.info("Use the 'Compare All Algorithms' button in the Search Visualization tab")
            else:
                st.warning("Generate a grid first")
    
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
                ["Pure Cost", "Balanced", "Hybrid"],
                index=1
            )
            
            strategy_map = {
                "Pure Cost": "pure_cost",
                "Balanced": "balanced",
                "Hybrid": "hybrid"
            }
            
            max_load_diff = st.slider("Maximum Load Difference", 1, 5, 2)
            
            if st.button("📦 Plan Deliveries"):
                with st.spinner("Planning deliveries..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/delivery/plan",
                            json={
                                "grid_id": grid['grid_id'],
                                "assignment_strategy": strategy_map[strategy],
                                "max_load_diff": max_load_diff
                            }
                        )
                        
                        if response.status_code == 200:
                            plan = response.json()
                            
                            # Display assignments
                            st.success("✅ Delivery plan created!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Cost", f"{plan['total_cost']:.2f}")
                            with col2:
                                avg_load = sum(plan['store_loads'].values()) / len(plan['store_loads'])
                                st.metric("Average Store Load", f"{avg_load:.1f}")
                            
                            # Store loads visualization
                            loads_df = pd.DataFrame({
                                "Store": list(plan['store_loads'].keys()),
                                "Load": list(plan['store_loads'].values())
                            })
                            
                            fig = px.bar(
                                loads_df,
                                x="Store",
                                y="Load",
                                title="Store Load Distribution",
                                color="Load",
                                color_continuous_scale="Blues"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Assignment details
                            with st.expander("Assignment Details"):
                                for store, customers in plan['assignments'].items():
                                    st.write(f"**{store}** → Customers: {customers}")
                                    
                        else:
                            st.error(f"Planning failed: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.info("Generate or load a grid first")
    
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
elif page == "⚙️ Configuration":
    show_configuration()


if __name__ == "__main__":
    # This would be run as: streamlit run app/frontend/main.py
    pass