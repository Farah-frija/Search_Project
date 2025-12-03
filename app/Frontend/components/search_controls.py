# app/frontend/components/search_controls.py
import streamlit as st
from typing import Dict, List, Tuple, Optional, Callable
import pandas as pd

class SearchControls:
    """Search controls component for delivery route planning"""
    
    # Available algorithms with descriptions
    ALGORITHMS = {
        "BF": {
            "name": "Breadth-First Search",
            "description": "Explores all neighbors first. Guarantees shortest path with uniform costs.",
            "optimal": True,
            "complete": True,
            "complexity": "O(b^d)"
        },
        "DF": {
            "name": "Depth-First Search",
            "description": "Explores as deep as possible first. Memory efficient but not optimal.",
            "optimal": False,
            "complete": True,
            "complexity": "O(b^m)"
        },
        "ID": {
            "name": "Iterative Deepening",
            "description": "Combines benefits of BFS and DFS. Optimal and memory efficient.",
            "optimal": True,
            "complete": True,
            "complexity": "O(b^d)"
        },
        "UC": {
            "name": "Uniform Cost Search",
            "description": "Finds cheapest path first using actual costs. Optimal for variable costs.",
            "optimal": True,
            "complete": True,
            "complexity": "O(b^(C*/ε))"
        },
        "GR1": {
            "name": "Greedy Search (Manhattan)",
            "description": "Uses heuristic to guide search. Fast but not always optimal.",
            "optimal": False,
            "complete": False,
            "complexity": "O(b^m)"
        },
        "GR2": {
            "name": "Greedy Search (Diagonal)",
            "description": "Alternative heuristic using diagonal distance.",
            "optimal": False,
            "complete": False,
            "complexity": "O(b^m)"
        },
        "AS1": {
            "name": "A* Search (Manhattan)",
            "description": "Optimal heuristic search using Manhattan distance.",
            "optimal": True,
            "complete": True,
            "complexity": "O(b^d)"
        },
        "AS2": {
            "name": "A* Search (Diagonal)",
            "description": "Optimal heuristic search using diagonal distance.",
            "optimal": True,
            "complete": True,
            "complexity": "O(b^d)"
        }
    }
    
    # Available heuristics
    HEURISTICS = {
        "manhattan": "Manhattan Distance (|dx| + |dy|)",
        "euclidean": "Euclidean Distance (sqrt(dx² + dy²))",
        "diagonal": "Diagonal Distance (max(|dx|, |dy|))",
        "zero": "Zero Heuristic (always 0)"
    }
    
    @staticmethod
    def render_algorithm_selection(selected_algo: str = "AS1") -> str:
        """
        Render algorithm selection widget
        
        Args:
            selected_algo: Default selected algorithm
            
        Returns:
            Selected algorithm code
        """
        st.markdown("### Search Algorithm")
        
        # Create algorithm options with descriptions
        algo_options = []
        for algo_code, algo_info in SearchControls.ALGORITHMS.items():
            display_text = f"{algo_info['name']} ({algo_code})"
            if algo_info['optimal']:
                display_text += " ⭐"
            algo_options.append((algo_code, display_text))
        
        # Sort options (optimal first, then by name)
        algo_options.sort(key=lambda x: (not SearchControls.ALGORITHMS[x[0]]['optimal'], x[1]))
        
        # Create selection
        selected_display = st.selectbox(
            "Select algorithm",
            options=[opt[1] for opt in algo_options],
            index=[opt[0] for opt in algo_options].index(selected_algo) if selected_algo in [opt[0] for opt in algo_options] else 0,
            help="Choose the search algorithm to use"
        )
        
        # Get selected algorithm code
        selected_code = None
        for algo_code, display_text in algo_options:
            if display_text == selected_display:
                selected_code = algo_code
                break
        
        # Show algorithm info
        if selected_code:
            algo_info = SearchControls.ALGORITHMS[selected_code]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Optimal", "✅" if algo_info['optimal'] else "❌")
            with col2:
                st.metric("Complete", "✅" if algo_info['complete'] else "❌")
            with col3:
                st.metric("Complexity", algo_info['complexity'])
            
            st.info(algo_info['description'])
        
        return selected_code
    
    @staticmethod
    def render_heuristic_selection(selected_heuristic: str = "manhattan") -> str:
        """
        Render heuristic selection widget (for informed searches)
        
        Returns:
            Selected heuristic name
        """
        st.markdown("### Heuristic Function")
        
        selected = st.selectbox(
            "Select heuristic",
            options=list(SearchControls.HEURISTICS.keys()),
            format_func=lambda x: SearchControls.HEURISTICS[x],
            index=list(SearchControls.HEURISTICS.keys()).index(selected_heuristic) if selected_heuristic in SearchControls.HEURISTICS else 0,
            help="Heuristic function for informed search algorithms"
        )
        
        return selected
    
    @staticmethod
    def render_search_settings() -> Dict:
        """
        Render advanced search settings
        
        Returns:
            Dictionary of search settings
        """
        st.markdown("### Advanced Settings")
        
        settings = {}
        
        with st.expander("Search Configuration"):
            col1, col2 = st.columns(2)
            
            with col1:
                settings['timeout'] = st.number_input(
                    "Timeout (seconds)",
                    min_value=1,
                    max_value=300,
                    value=30,
                    help="Maximum time for search to run"
                )
                
                settings['show_visited'] = st.checkbox(
                    "Show visited nodes",
                    value=True,
                    help="Highlight visited nodes during visualization"
                )
            
            with col2:
                settings['show_frontier'] = st.checkbox(
                    "Show frontier nodes",
                    value=False,
                    help="Highlight frontier nodes during visualization"
                )
                
                settings['animate_search'] = st.checkbox(
                    "Animate search",
                    value=False,
                    help="Show step-by-step search animation"
                )
        
        return settings
    
    @staticmethod
    def render_algorithm_comparison() -> List[str]:
        """
        Render algorithm comparison selection
        
        Returns:
            List of selected algorithm codes for comparison
        """
        st.markdown("### Compare Multiple Algorithms")
        
        algo_options = []
        for algo_code, algo_info in SearchControls.ALGORITHMS.items():
            algo_options.append({
                "code": algo_code,
                "name": algo_info['name'],
                "optimal": algo_info['optimal']
            })
        
        # Create multiselect
        selected_names = st.multiselect(
            "Select algorithms to compare",
            options=[f"{algo['name']} ({algo['code']})" for algo in algo_options],
            default=[f"{algo['name']} ({algo['code']})" for algo in algo_options if algo['code'] in ["BF", "UC", "AS1"]],
            help="Select multiple algorithms to compare their performance"
        )
        
        # Extract algorithm codes
        selected_codes = []
        for name in selected_names:
            for algo in algo_options:
                if f"{algo['name']} ({algo['code']})" == name:
                    selected_codes.append(algo['code'])
                    break
        
        return selected_codes
    
    @staticmethod
    def render_position_selection(grid_data: Dict, label: str = "Select Position") -> Optional[Dict]:
        """
        Render position selection widget
        
        Args:
            grid_data: Grid data containing stores/customers
            label: Widget label
            
        Returns:
            Selected position dictionary or None
        """
        if not grid_data or 'grid' not in grid_data:
            return None
        
        grid = grid_data['grid']
        
        # Combine stores and customers
        positions = []
        
        # Add stores
        for i, store in enumerate(grid.get('stores', [])):
            positions.append({
                "type": "store",
                "index": i,
                "x": store['x'],
                "y": store['y'],
                "label": f"Store {i+1} ({store['x']},{store['y']})"
            })
        
        # Add customers
        for i, customer in enumerate(grid.get('customers', [])):
            positions.append({
                "type": "customer",
                "index": i,
                "x": customer['x'],
                "y": customer['y'],
                "label": f"Customer {i+1} ({customer['x']},{customer['y']})"
            })
        
        if not positions:
            return None
        
        # Create selection
        selected_label = st.selectbox(
            label,
            options=[p['label'] for p in positions],
            index=0
        )
        
        # Find selected position
        for pos in positions:
            if pos['label'] == selected_label:
                return {
                    "x": pos['x'],
                    "y": pos['y'],
                    "type": pos['type'],
                    "index": pos['index']
                }
        
        return None
    
    @staticmethod
    def render_store_customer_selection(grid_data: Dict) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Render store and customer selection
        
        Returns:
            Tuple of (store_position, customer_position)
        """
        col1, col2 = st.columns(2)
        
        with col1:
            store_pos = SearchControls.render_position_selection(
                grid_data,
                label="Select Store"
            )
        
        with col2:
            customer_pos = SearchControls.render_position_selection(
                grid_data,
                label="Select Customer"
            )
        
        return store_pos, customer_pos
    
    @staticmethod
    def render_search_button() -> bool:
        """
        Render search button
        
        Returns:
            True if search button was clicked
        """
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            search_clicked = st.button(
                "🔍 Start Search",
                type="primary",
                use_container_width=True,
                help="Click to start the search algorithm"
            )
        
        return search_clicked
    
    @staticmethod
    def render_search_results(results: Dict) -> None:
        """
        Render search results
        
        Args:
            results: Search results dictionary
        """
        if not results:
            return
        
        st.markdown("### Search Results")
        
        if results.get('success'):
            # Success results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Cost",
                    f"{results.get('cost', 0):.2f}",
                    help="Total cost of the found path"
                )
            
            with col2:
                st.metric(
                    "Path Length",
                    len(results.get('path', [])),
                    help="Number of steps in the path"
                )
            
            with col3:
                st.metric(
                    "Nodes Expanded",
                    results.get('nodes_expanded', 0),
                    help="Number of nodes explored during search"
                )
            
            # Path details
            with st.expander("Path Details"):
                if results.get('path'):
                    st.write("**Actions:**")
                    
                    # Display path in a more readable format
                    path_text = ""
                    for i, action in enumerate(results['path']):
                        if i > 0:
                            path_text += " → "
                        path_text += f"{action}"
                    
                    st.code(path_text, language=None)
                    
                    # Show step-by-step
                    st.write("**Step-by-step:**")
                    steps_df = pd.DataFrame([
                        {"Step": i, "Action": action}
                        for i, action in enumerate(results['path'])
                    ])
                    st.dataframe(steps_df, use_container_width=True, hide_index=True)
            
            # Execution info
            with st.expander("Execution Information"):
                info_cols = st.columns(2)
                with info_cols[0]:
                    st.write(f"**Algorithm:** {results.get('algorithm', 'Unknown')}")
                    st.write(f"**Heuristic:** {results.get('heuristic', 'N/A')}")
                
                with info_cols[1]:
                    if results.get('execution_time_ms'):
                        st.write(f"**Time:** {results.get('execution_time_ms'):.1f} ms")
                    if results.get('memory_peak_mb'):
                        st.write(f"**Memory:** {results.get('memory_peak_mb'):.1f} MB")
        
        else:
            # No path found
            st.error("❌ No path found")
            
            if results.get('nodes_expanded'):
                st.info(f"Explored {results.get('nodes_expanded')} nodes before determining no path exists")
            
            # Possible reasons
            with st.expander("Possible Reasons"):
                st.write("""
                - **Obstacles** block all possible paths
                - **Grid boundaries** prevent movement
                - **Algorithm limitations** for specific configurations
                - **Timeout** before finding a path
                """)
    
    @staticmethod
    def get_algorithm_info(algo_code: str) -> Dict:
        """
        Get algorithm information
        
        Args:
            algo_code: Algorithm code
            
        Returns:
            Algorithm information dictionary
        """
        return SearchControls.ALGORITHMS.get(algo_code, {})
    
    @staticmethod
    def get_all_algorithms() -> List[str]:
        """
        Get list of all algorithm codes
        
        Returns:
            List of algorithm codes
        """
        return list(SearchControls.ALGORITHMS.keys())