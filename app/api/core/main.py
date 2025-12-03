# InteractiveConsole.py
import sys
import os
import time
import random
from typing import List, Tuple, Set, Dict, Optional, Any
import json

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

try:
    from DataStructure.Position import Position
    from DataStructure.Grid import Grid
    from DataStructure.DeliveryState import DeliveryState
    from Search.Generic_search import GenericSearch
    from Search.Delivery_problem import DeliveryProblem
    from Search.Heuristics import HEURISTICS
    from GridGenerator.gridGenerator import GridGenerator
    from Parsers.InputParser import parse_input_with_stores
    from Delivery.Delivery_planner import DeliveryPlanner
    from Delivery.Delivery_Search import DeliverySearch
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    print("Some features may be limited.")

class InteractiveConsole:
    """FULLY INTERACTIVE CONSOLE WITH COMPLETE USER CONTROL"""
    
    # Unicode symbols
    SYMBOLS = {
        'store': '🏪', 'customer': '🏠', 'empty': '·', 'obstacle': '█',
        'path': '●', 'tunnel': '🚇', 'agent': '🚚', 'visited': '○',
        'frontier': '□', 'current': '🌟', 'start': '🚀', 'goal': '🎯',
    }
    
    # Color codes
    COLORS = {
        'reset': '\033[0m', 'red': '\033[91m', 'green': '\033[92m',
        'yellow': '\033[93m', 'blue': '\033[94m', 'magenta': '\033[95m',
        'cyan': '\033[96m', 'white': '\033[97m', 'gray': '\033[90m',
        'orange': '\033[38;5;214m', 'purple': '\033[38;5;129m',
        'pink': '\033[38;5;205m', 'brown': '\033[38;5;130m',
    }
    
    # Search strategies
    STRATEGIES = ["BF", "DF", "ID", "UC", "GR1", "GR2", "AS1", "AS2"]
    
    def __init__(self):
        self.grid = None
        self.current_state = None
        self.search_history = []
        self.user_settings = self.load_default_settings()
        self.running = True
        self.selected_store = None
        self.selected_customer = None
        
    def load_default_settings(self):
        """Default user settings"""
        return {
            # Grid display
            'show_coordinates': True,
            'show_legend': True,
            'show_traffic': False,
            'color_mode': 'full',
            'symbol_mode': 'unicode',  # 'unicode' or 'ascii'
            
            # Search settings
            'default_strategy': 'AS1',
            'default_heuristic': 'manhattan',
            'animate_search': False,
            'animation_speed': 0.1,
            'show_search_stats': True,
            
            # Grid generation
            'grid_width': 8,
            'grid_height': 8,
            'min_stores': 2,
            'max_stores': 3,
            'min_customers': 4,
            'max_customers': 6,
            'obstacle_density': 0.15,
            'tunnel_density': 0.2,
            'min_traffic': 1,
            'max_traffic': 4,
            
            # Visualization
            'highlight_path': True,
            'show_visited': True,
            'show_frontier': False,
            'compress_display': False,
        }
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def color_text(self, text, color_name):
        """Add color to text"""
        if self.user_settings['color_mode'] == 'none':
            return text
        return f"{self.COLORS.get(color_name, '')}{text}{self.COLORS['reset']}"
    
    def get_symbol(self, symbol_name):
        """Get symbol based on user preference"""
        if self.user_settings['symbol_mode'] == 'ascii':
            ascii_map = {
                'store': 'S', 'customer': 'C', 'empty': '.', 'obstacle': '#',
                'path': '*', 'tunnel': 'T', 'agent': 'A', 'visited': 'o',
                'frontier': '?', 'current': '@', 'start': '>', 'goal': '!',
            }
            return ascii_map.get(symbol_name, '?')
        return self.SYMBOLS.get(symbol_name, '?')
    
    def display_header(self, title):
        """Display beautiful header"""
        print("\n" + "="*80)
        print(f"{self.color_text(' ' * 10 + title.upper(), 'cyan')}")
        print("="*80)
    
    def display_menu(self, menu_items, title="MAIN MENU"):
        """Display interactive menu"""
        self.clear_screen()
        self.display_header(title)
        
        for i, (key, description) in enumerate(menu_items.items(), 1):
            print(f"{self.color_text(f'[{i}]', 'yellow')} {description}")
        
        print(f"{self.color_text('[0]', 'red')} Exit")
        print("\n" + "-"*80)
        
        choice = input(f"{self.color_text('Your choice', 'green')}: ").strip()
        
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return 'exit'
            if 1 <= choice_num <= len(menu_items):
                return list(menu_items.keys())[choice_num - 1]
        except ValueError:
            pass
        
        # Try to match by key
        if choice in menu_items:
            return choice
        
        return None
    
    def generate_random_grid(self):
        """Generate grid with user parameters"""
        print("\n" + "="*80)
        print(f"{self.color_text(' GRID GENERATION SETTINGS ', 'yellow')}")
        print("="*80)
        
        # Get user input for each parameter
        settings = self.user_settings.copy()
        
        print(f"\nCurrent settings:")
        print(f"  Size: {settings['grid_width']}x{settings['grid_height']}")
        print(f"  Stores: {settings['min_stores']}-{settings['max_stores']}")
        print(f"  Customers: {settings['min_customers']}-{settings['max_customers']}")
        print(f"  Obstacles: {settings['obstacle_density']*100:.1f}%")
        print(f"  Tunnel probability: {settings['tunnel_density']*100:.1f}%")
        print(f"  Traffic cost range: {settings['min_traffic']}-{settings['max_traffic']}")
        
        print(f"\n{self.color_text('[1]', 'yellow')} Use current settings")
        print(f"{self.color_text('[2]', 'yellow')} Customize settings")
        print(f"{self.color_text('[3]', 'yellow')} Quick presets")
        
        choice = input(f"\n{self.color_text('Choice', 'green')}: ").strip()
        
        if choice == '2':
            # Customize everything
            settings['grid_width'] = self.get_int_input("Grid width", 5, 30, settings['grid_width'])
            settings['grid_height'] = self.get_int_input("Grid height", 5, 30, settings['grid_height'])
            settings['min_stores'] = self.get_int_input("Minimum stores", 1, 10, settings['min_stores'])
            settings['max_stores'] = self.get_int_input("Maximum stores", settings['min_stores'], 10, settings['max_stores'])
            settings['min_customers'] = self.get_int_input("Minimum customers", 1, 20, settings['min_customers'])
            settings['max_customers'] = self.get_int_input("Maximum customers", settings['min_customers'], 20, settings['max_customers'])
            settings['obstacle_density'] = self.get_float_input("Obstacle density (0-1)", 0, 0.5, settings['obstacle_density'])
            settings['tunnel_density'] = self.get_float_input("Tunnel probability (0-1)", 0, 1, settings['tunnel_density'])
            settings['min_traffic'] = self.get_int_input("Minimum traffic cost", 1, 10, settings['min_traffic'])
            settings['max_traffic'] = self.get_int_input("Maximum traffic cost", settings['min_traffic'], 10, settings['max_traffic'])
        
        elif choice == '3':
            # Quick presets
            print(f"\n{self.color_text('[1]', 'yellow')} Easy (few obstacles, no tunnels)")
            print(f"{self.color_text('[2]', 'yellow')} Medium (balanced)")
            print(f"{self.color_text('[3]', 'yellow')} Hard (many obstacles and tunnels)")
            print(f"{self.color_text('[4]', 'yellow')} Maze-like (many obstacles)")
            print(f"{self.color_text('[5]', 'yellow')} Tunnel network (many tunnels)")
            
            preset = input(f"\n{self.color_text('Preset choice', 'green')}: ").strip()
            
            if preset == '1':
                settings.update({
                    'obstacle_density': 0.05,
                    'tunnel_density': 0.0,
                    'min_traffic': 1,
                    'max_traffic': 2,
                })
            elif preset == '2':
                settings.update({
                    'obstacle_density': 0.15,
                    'tunnel_density': 0.2,
                    'min_traffic': 1,
                    'max_traffic': 4,
                })
            elif preset == '3':
                settings.update({
                    'obstacle_density': 0.3,
                    'tunnel_density': 0.4,
                    'min_traffic': 2,
                    'max_traffic': 5,
                })
            elif preset == '4':
                settings.update({
                    'obstacle_density': 0.4,
                    'tunnel_density': 0.1,
                    'min_traffic': 1,
                    'max_traffic': 3,
                })
            elif preset == '5':
                settings.update({
                    'obstacle_density': 0.1,
                    'tunnel_density': 0.5,
                    'min_traffic': 3,
                    'max_traffic': 6,
                })
        
        # Save settings
        self.user_settings.update(settings)
        
        # Generate grid
        print(f"\n{self.color_text('Generating grid...', 'cyan')}")
        
        generator = GridGenerator()
        init_str, traffic_str, stores = generator.generate_grid(
            min_m=settings['grid_width'],
            max_m=settings['grid_width'],
            min_n=settings['grid_height'],
            max_n=settings['grid_height'],
            min_stores=settings['min_stores'],
            max_stores=settings['max_stores'],
            min_customers=settings['min_customers'],
            max_customers=settings['max_customers'],
            min_tunnels=1 if settings['tunnel_density'] > 0 else 0,
            max_tunnel_prob=settings['tunnel_density'],
            min_obstacle_prob=settings['obstacle_density'],
            max_obstacle_prob=settings['obstacle_density'],
            min_traffic=settings['min_traffic'],
            max_traffic=settings['max_traffic']
        )
        
        self.grid = parse_input_with_stores(init_str, traffic_str, stores)
        
        print(f"{self.color_text('✓ Grid generated successfully!', 'green')}")
        print(f"  Size: {self.grid.m}x{self.grid.n}")
        print(f"  Stores: {len(self.grid.stores)}")
        print(f"  Customers: {len(self.grid.customers)}")
        print(f"  Tunnels: {len(self.grid.tunnels)//2}")
        
        input(f"\n{self.color_text('Press Enter to continue...', 'gray')}")
    
    def get_int_input(self, prompt, min_val, max_val, default):
        """Get integer input with validation"""
        while True:
            try:
                value = input(f"{prompt} [{min_val}-{max_val}, default={default}]: ").strip()
                if not value:
                    return default
                value = int(value)
                if min_val <= value <= max_val:
                    return value
                print(f"Please enter a value between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")
    
    def get_float_input(self, prompt, min_val, max_val, default):
        """Get float input with validation"""
        while True:
            try:
                value = input(f"{prompt} [{min_val}-{max_val}, default={default}]: ").strip()
                if not value:
                    return default
                value = float(value)
                if min_val <= value <= max_val:
                    return value
                print(f"Please enter a value between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")
    
    def visualize_grid(self, path=None, visited=None, frontier=None, current_pos=None):
        """Visualize the grid with all user settings"""
        if not self.grid:
            print(f"{self.color_text('No grid loaded!', 'red')}")
            return
        
        self.clear_screen()
        self.display_header("GRID VISUALIZATION")
        
        # Display legend if enabled
        if self.user_settings['show_legend']:
            print(f"\n{self.color_text('LEGEND:', 'yellow')}")
            symbols = [
                (self.get_symbol('store'), 'Store'),
                (self.get_symbol('customer'), 'Customer'),
                (self.get_symbol('tunnel'), 'Tunnel'),
                (self.get_symbol('obstacle'), 'Obstacle (blocked)'),
                (self.get_symbol('agent'), 'Delivery Agent'),
                (self.get_symbol('path'), 'Delivery Path'),
                (self.color_text(self.get_symbol('visited'), 'gray'), 'Visited'),
                (self.color_text(self.get_symbol('frontier'), 'blue'), 'Frontier'),
            ]
            
            for i in range(0, len(symbols), 4):
                row = symbols[i:i+4]
                print("  " + "  ".join(f"{sym} {desc:15}" for sym, desc in row))
        
        # Grid statistics
        print(f"\n{self.color_text('GRID STATISTICS:', 'yellow')}")
        print(f"  Size: {self.grid.m} × {self.grid.n}")
        print(f"  Stores: {len(self.grid.stores)}")
        print(f"  Customers: {len(self.grid.customers)}")
        print(f"  Tunnels: {len(self.grid.tunnels)//2}")
        
        # Count obstacles
        obstacles = sum(1 for cost in self.grid.traffic.values() if cost == 0)
        total_edges = len(self.grid.traffic)
        if total_edges > 0:
            obstacle_percent = (obstacles / total_edges) * 100
            print(f"  Obstacles: {obstacles} ({obstacle_percent:.1f}% of edges)")
        
        # Display coordinates if enabled
        if self.user_settings['show_coordinates']:
            print("\n" + " " * 4 + " ".join(f"{i:2}" for i in range(self.grid.n)))
        
        print()
        
        # Create and display grid
        for i in range(self.grid.m):
            # Row coordinate
            if self.user_settings['show_coordinates']:
                print(f"{i:2} ", end="")
            
            for j in range(self.grid.n):
                pos = Position(i, j)
                symbol = self.get_cell_symbol(pos, path, visited, frontier, current_pos)
                print(symbol + " ", end="")
            
            # Display traffic costs for this row if enabled
            if self.user_settings['show_traffic'] and not self.user_settings['compress_display']:
                self.display_row_traffic(i)
            
            print()
        
        # Display selected elements
        if self.selected_store:
            print(f"\n{self.color_text('Selected Store:', 'yellow')} {self.selected_store}")
        if self.selected_customer:
            print(f"{self.color_text('Selected Customer:', 'yellow')} {self.selected_customer}")
        
        print()
    
    def get_cell_symbol(self, pos, path, visited, frontier, current_pos):
        """Get the appropriate symbol for a cell"""
        # Priority order matters!
        
        # 1. Current position (highest priority)
        if current_pos and pos == current_pos:
            return self.color_text(self.get_symbol('agent'), 'green')
        
        # 2. Start position
        if self.selected_store and pos == self.selected_store:
            return self.color_text(self.get_symbol('start'), 'yellow')
        
        # 3. Goal position
        if self.selected_customer and pos == self.selected_customer:
            return self.color_text(self.get_symbol('goal'), 'red')
        
        # 4. Path
        if path and pos in path:
            return self.color_text(self.get_symbol('path'), 'green')
        
        # 5. Stores
        if pos in self.grid.stores:
            return self.color_text(self.get_symbol('store'), 'yellow')
        
        # 6. Customers
        if pos in self.grid.customers:
            return self.color_text(self.get_symbol('customer'), 'cyan')
        
        # 7. Tunnel entrances/exits
        if pos in self.grid.tunnels:
            return self.color_text(self.get_symbol('tunnel'), 'magenta')
        
        # 8. Visited nodes
        if visited and pos in visited and self.user_settings['show_visited']:
            return self.color_text(self.get_symbol('visited'), 'gray')
        
        # 9. Frontier nodes
        if frontier and pos in frontier and self.user_settings['show_frontier']:
            return self.color_text(self.get_symbol('frontier'), 'blue')
        
        # 10. Check if cell has obstacle edges (visual hint)
        has_obstacle = False
        for neighbor in self.get_neighbors(pos):
            if self.grid.is_blocked(pos, neighbor):
                has_obstacle = True
                break
        
        if has_obstacle:
            return self.color_text(self.get_symbol('empty'), 'dark_gray')
        
        # 11. Default empty cell
        return self.color_text(self.get_symbol('empty'), 'white')
    
    def display_row_traffic(self, row):
        """Display traffic costs for a row"""
        if row >= self.grid.m - 1:
            return
        
        print("   ", end="")
        for col in range(self.grid.n):
            pos1 = Position(row, col)
            pos2 = Position(row + 1, col)
            
            if (0 <= pos2.x < self.grid.m) and (0 <= pos2.y < self.grid.n):
                traffic = self.grid.get_traffic_level(pos1, pos2)
                if traffic is not None:
                    if traffic == 0:
                        color = 'red'
                    elif traffic == 1:
                        color = 'green'
                    elif traffic == 2:
                        color = 'yellow'
                    elif traffic == 3:
                        color = 'orange'
                    else:
                        color = 'red'
                    
                    symbol = '↕'  # Vertical
                    print(self.color_text(symbol, color) + f"{traffic} ", end="")
                else:
                    print("   ", end="")
            else:
                print("   ", end="")
    
    def get_neighbors(self, pos):
        """Get valid neighbor positions"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_pos = Position(pos.x + dx, pos.y + dy)
            if 0 <= new_pos.x < self.grid.m and 0 <= new_pos.y < self.grid.n:
                neighbors.append(new_pos)
        return neighbors
    
    def select_elements(self):
        """Let user select store and customer"""
        if not self.grid:
            print(f"{self.color_text('No grid loaded!', 'red')}")
            return
        
        self.clear_screen()
        self.display_header("SELECT ELEMENTS")
        
        # Display stores
        print(f"\n{self.color_text('AVAILABLE STORES:', 'yellow')}")
        for i, store in enumerate(self.grid.stores):
            print(f"  {self.color_text(f'[{i+1}]', 'green')} Position {store}")
        
        # Display customers
        print(f"\n{self.color_text('AVAILABLE CUSTOMERS:', 'yellow')}")
        for i, customer in enumerate(self.grid.customers):
            print(f"  {self.color_text(f'[{i+1}]', 'cyan')} Position {customer}")
        
        print(f"\n{self.color_text('[R]', 'yellow')} Random selection")
        print(f"{self.color_text('[C]', 'yellow')} Clear selection")
        
        # Select store
        store_choice = input(f"\n{self.color_text('Select store (number or coordinates x,y)', 'green')}: ").strip()
        
        if store_choice.upper() == 'R':
            self.selected_store = random.choice(self.grid.stores)
            print(f"Randomly selected store: {self.selected_store}")
        elif store_choice.upper() == 'C':
            self.selected_store = None
            print("Cleared store selection")
        elif ',' in store_choice:
            try:
                x, y = map(int, store_choice.split(','))
                pos = Position(x, y)
                if pos in self.grid.stores:
                    self.selected_store = pos
                    print(f"Selected store at {pos}")
                else:
                    print(f"No store at position {pos}")
            except ValueError:
                print("Invalid format. Use 'x,y'")
        else:
            try:
                idx = int(store_choice) - 1
                if 0 <= idx < len(self.grid.stores):
                    self.selected_store = self.grid.stores[idx]
                    print(f"Selected store: {self.selected_store}")
                else:
                    print("Invalid store number")
            except ValueError:
                print("Invalid input")
        
        # Select customer
        customer_choice = input(f"\n{self.color_text('Select customer (number or coordinates x,y)', 'green')}: ").strip()
        
        if customer_choice.upper() == 'R':
            self.selected_customer = random.choice(self.grid.customers)
            print(f"Randomly selected customer: {self.selected_customer}")
        elif customer_choice.upper() == 'C':
            self.selected_customer = None
            print("Cleared customer selection")
        elif ',' in customer_choice:
            try:
                x, y = map(int, customer_choice.split(','))
                pos = Position(x, y)
                if pos in self.grid.customers:
                    self.selected_customer = pos
                    print(f"Selected customer at {pos}")
                else:
                    print(f"No customer at position {pos}")
            except ValueError:
                print("Invalid format. Use 'x,y'")
        else:
            try:
                idx = int(customer_choice) - 1
                if 0 <= idx < len(self.grid.customers):
                    self.selected_customer = self.grid.customers[idx]
                    print(f"Selected customer: {self.selected_customer}")
                else:
                    print("Invalid customer number")
            except ValueError:
                print("Invalid input")
        
        input(f"\n{self.color_text('Press Enter to continue...', 'gray')}")
    
    def run_search(self):
        """Run search algorithm with visualization"""
        if not self.grid or not self.selected_store or not self.selected_customer:
            print(f"{self.color_text('Need both store and customer selected!', 'red')}")
            input(f"{self.color_text('Press Enter to continue...', 'gray')}")
            return
        
        self.clear_screen()
        self.display_header("SEARCH ALGORITHM")
        
        # Select search strategy
        print(f"\n{self.color_text('AVAILABLE STRATEGIES:', 'yellow')}")
        for i, strategy in enumerate(self.STRATEGIES, 1):
            desc = {
                'BF': 'Breadth-First Search',
                'DF': 'Depth-First Search',
                'ID': 'Iterative Deepening',
                'UC': 'Uniform Cost Search',
                'GR1': 'Greedy Search (h1)',
                'GR2': 'Greedy Search (h2)',
                'AS1': 'A* Search (h1)',
                'AS2': 'A* Search (h2)',
            }.get(strategy, strategy)
            
            if strategy == self.user_settings['default_strategy']:
                print(f"  {self.color_text(f'[{i}]', 'green')} {strategy}: {desc} {self.color_text('[DEFAULT]', 'yellow')}")
            else:
                print(f"  {self.color_text(f'[{i}]', 'green')} {strategy}: {desc}")
        
        print(f"\n{self.color_text('[A]', 'yellow')} Run ALL strategies")
        print(f"{self.color_text('[C]', 'yellow')} Configure search settings")
        
        choice = input(f"\n{self.color_text('Select strategy', 'green')}: ").strip().upper()
        
        strategies_to_run = []
        
        if choice == 'A':
            strategies_to_run = self.STRATEGIES
        elif choice == 'C':
            self.configure_search_settings()
            return
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.STRATEGIES):
                    strategies_to_run = [self.STRATEGIES[idx]]
                else:
                    print("Invalid strategy number")
                    return
            except ValueError:
                # Try direct strategy name
                if choice in self.STRATEGIES:
                    strategies_to_run = [choice]
                else:
                    print("Invalid input")
                    return
        
        # Run selected strategies
        results = {}
        for strategy in strategies_to_run:
            print(f"\n{'-'*60}")
            print(f"{self.color_text(f'Running {strategy}...', 'cyan')}")
            
            problem = DeliveryProblem(self.grid, self.selected_store, self.selected_customer)
            search = GenericSearch(problem, strategy=strategy)
            
            # Animate search if enabled
            if self.user_settings['animate_search']:
                path, cost, nodes = self.animate_search(search, problem)
            else:
                path, cost, nodes = search.solve()
            
            # Store results
            results[strategy] = {
                'path': path,
                'cost': cost,
                'nodes_expanded': nodes,
                'found': path is not None
            }
            
            # Display result
            if path:
                print(f"{self.color_text('✓ Path found!', 'green')}")
                print(f"  Cost: {cost}")
                print(f"  Path length: {len(path)} steps")
                print(f"  Nodes expanded: {nodes}")
                
                # Show path summary
                if len(path) <= 10:
                    print(f"  Path: {' → '.join(path)}")
                else:
                    print(f"  Path (first 5): {' → '.join(path[:5])}...")
            else:
                print(f"{self.color_text('✗ No path found', 'red')}")
                print(f"  Nodes expanded: {nodes}")
        
        # Compare results if multiple strategies
        if len(results) > 1:
            self.display_comparison(results)
        
        # Visualize the best path
        if any(r['found'] for r in results.values()):
            best_strategy = min(
                (s for s, r in results.items() if r['found']),
                key=lambda s: results[s]['cost']
            )
            
            print(f"\n{self.color_text('Best path found by:', 'yellow')} {best_strategy}")
            
            # Convert path to positions for visualization
            path_positions = self.path_to_positions(results[best_strategy]['path'])
            
            # Show visualization
            self.visualize_grid(
                path=path_positions,
                current_pos=self.selected_store
            )
            
            print(f"\n{self.color_text('Path details:', 'yellow')}")
            print(f"  Strategy: {best_strategy}")
            print(f"  Total cost: {results[best_strategy]['cost']}")
            print(f"  Steps: {len(results[best_strategy]['path'])}")
            print(f"  Nodes expanded: {results[best_strategy]['nodes_expanded']}")
        
        input(f"\n{self.color_text('Press Enter to continue...', 'gray')}")
    
    def animate_search(self, search, problem):
        """Animate the search process"""
        print(f"{self.color_text('Animating search...', 'cyan')}")
        print(f"  Animation speed: {self.user_settings['animation_speed']}s per step")
        
        # This is a simplified animation - you'd need to modify GenericSearch
        # to provide callbacks for visited/frontier nodes
        print(f"{self.color_text('(Animation would go here)', 'gray')}")
        
        # For now, just run normally
        return search.solve()
    
    def path_to_positions(self, actions):
        """Convert action sequence to positions"""
        if not actions or not self.selected_store:
            return []
        
        positions = [self.selected_store]
        current = self.selected_store
        
        for action in actions:
            if action == "up":
                current = Position(current.x, current.y - 1)
            elif action == "down":
                current = Position(current.x, current.y + 1)
            elif action == "left":
                current = Position(current.x - 1, current.y)
            elif action == "right":
                current = Position(current.x + 1, current.y)
            elif action == "tunnel":
                if current in self.grid.tunnels:
                    current = self.grid.tunnels[current]
            
            positions.append(current)
        
        return positions
    
    def display_comparison(self, results):
        """Display comparison table of all strategies"""
        print(f"\n{self.color_text('='*60, 'cyan')}")
        print(f"{self.color_text('SEARCH STRATEGIES COMPARISON', 'yellow')}")
        print(f"{self.color_text('='*60, 'cyan')}")
        
        print(self.color_text(f"\n{'Strategy':<8} {'Found':<8} {'Cost':<10} {'Steps':<10} {'Nodes':<12} {'Time':<10}", 'yellow'))
        
        for strategy in self.STRATEGIES:
            if strategy in results:
                r = results[strategy]
                if r['found']:
                    found = "✓"
                    cost = f"{r['cost']:.1f}"
                    steps = len(r['path'])
                else:
                    found = "✗"
                    cost = "∞"
                    steps = "N/A"
                
                print(f"{strategy:<8} {found:<8} {cost:<10} {str(steps):<10} {r['nodes_expanded']:<12} {'N/A':<10}")
    
    def configure_search_settings(self):
        """Configure search settings"""
        self.clear_screen()
        self.display_header("SEARCH SETTINGS")
        
        print(f"\n{self.color_text('CURRENT SETTINGS:', 'yellow')}")
        for key, value in self.user_settings.items():
            if 'search' in key or 'animate' in key:
                print(f"  {key}: {value}")
        
        print(f"\n{self.color_text('[1]', 'yellow')} Change default strategy")
        print(f"{self.color_text('[2]', 'yellow')} Toggle animation")
        print(f"{self.color_text('[3]', 'yellow')} Change animation speed")
        print(f"{self.color_text('[4]', 'yellow')} Toggle search statistics")
        print(f"{self.color_text('[5]', 'yellow')} Reset to defaults")
        
        choice = input(f"\n{self.color_text('Choice', 'green')}: ").strip()
        
        if choice == '1':
            print(f"\nAvailable strategies: {', '.join(self.STRATEGIES)}")
            new_strat = input(f"New default strategy: ").strip().upper()
            if new_strat in self.STRATEGIES:
                self.user_settings['default_strategy'] = new_strat
                print(f"Default strategy changed to {new_strat}")
        
        elif choice == '2':
            self.user_settings['animate_search'] = not self.user_settings['animate_search']
            status = "ON" if self.user_settings['animate_search'] else "OFF"
            print(f"Search animation turned {status}")
        
        elif choice == '3':
            speed = self.get_float_input("Animation speed (seconds)", 0.01, 5.0, 
                                       self.user_settings['animation_speed'])
            self.user_settings['animation_speed'] = speed
        
        elif choice == '4':
            self.user_settings['show_search_stats'] = not self.user_settings['show_search_stats']
            status = "ON" if self.user_settings['show_search_stats'] else "OFF"
            print(f"Search statistics turned {status}")
        
        elif choice == '5':
            defaults = self.load_default_settings()
            # Only reset search-related settings
            for key in ['default_strategy', 'default_heuristic', 'animate_search', 
                       'animation_speed', 'show_search_stats']:
                self.user_settings[key] = defaults[key]
            print("Search settings reset to defaults")
        
        input(f"\n{self.color_text('Press Enter to continue...', 'gray')}")
    
    def configure_visualization(self):
        """Configure visualization settings"""
        self.clear_screen()
        self.display_header("VISUALIZATION SETTINGS")
        
        print(f"\n{self.color_text('CURRENT VISUALIZATION SETTINGS:', 'yellow')}")
        settings_to_show = ['color_mode', 'symbol_mode', 'show_coordinates', 
                           'show_legend', 'show_traffic', 'highlight_path',
                           'show_visited', 'show_frontier', 'compress_display']
        
        for key in settings_to_show:
            value = self.user_settings[key]
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n{self.color_text('[1]', 'yellow')} Toggle color mode")
        print(f"{self.color_text('[2]', 'yellow')} Toggle symbols (Unicode/ASCII)")
        print(f"{self.color_text('[3]', 'yellow')} Toggle coordinates")
        print(f"{self.color_text('[4]', 'yellow')} Toggle legend")
        print(f"{self.color_text('[5]', 'yellow')} Toggle traffic display")
        print(f"{self.color_text('[6]', 'yellow')} Toggle path highlighting")
        print(f"{self.color_text('[7]', 'yellow')} Toggle visited nodes")
        print(f"{self.color_text('[8]', 'yellow')} Toggle frontier nodes")
        print(f"{self.color_text('[9]', 'yellow')} Toggle compressed display")
        print(f"{self.color_text('[0]', 'yellow')} Reset all visualization settings")
        
        choice = input(f"\n{self.color_text('Choice', 'green')}: ").strip()
        
        toggle_map = {
            '1': ('color_mode', ['full', 'limited', 'none']),
            '2': ('symbol_mode', ['unicode', 'ascii']),
            '3': ('show_coordinates', None),
            '4': ('show_legend', None),
            '5': ('show_traffic', None),
            '6': ('highlight_path', None),
            '7': ('show_visited', None),
            '8': ('show_frontier', None),
            '9': ('compress_display', None),
        }
        
        if choice == '0':
            defaults = self.load_default_settings()
            for key in settings_to_show:
                self.user_settings[key] = defaults[key]
            print("All visualization settings reset to defaults")
        
        elif choice in toggle_map:
            key, options = toggle_map[choice]
            if options:
                # Cycle through options
                current = self.user_settings[key]
                current_idx = options.index(current)
                next_idx = (current_idx + 1) % len(options)
                self.user_settings[key] = options[next_idx]
                print(f"{key} changed to {options[next_idx]}")
            else:
                # Simple toggle
                self.user_settings[key] = not self.user_settings[key]
                status = "ON" if self.user_settings[key] else "OFF"
                print(f"{key.replace('_', ' ').title()} turned {status}")
        
        input(f"\n{self.color_text('Press Enter to continue...', 'gray')}")
    
    def run_delivery_planner(self):
        """Run the full delivery planner"""
        if not self.grid:
            print(f"{self.color_text('No grid loaded!', 'red')}")
            input(f"{self.color_text('Press Enter to continue...', 'gray')}")
            return
        
        print(f"\n{self.color_text('Running delivery planner...', 'cyan')}")
        
        try:
            planner = DeliveryPlanner(self.grid)
            analysis = planner.plan()
            
            # Display results
            self.clear_screen()
            self.display_header("DELIVERY PLANNER RESULTS")
            
            print(f"\n{self.color_text('GRID SUMMARY:', 'yellow')}")
            print(f"  Stores: {analysis['grid_info']['store_count']}")
            print(f"  Customers: {analysis['grid_info']['customer_count']}")
            
            # Show assignments for each strategy
            if 'assignments_by_strategy' in analysis:
                print(f"\n{self.color_text('ASSIGNMENTS BY STRATEGY:', 'yellow')}")
                
                for strategy in self.STRATEGIES[:3]:  # Show first 3 for brevity
                    if strategy in analysis['assignments_by_strategy']:
                        data = analysis['assignments_by_strategy'][strategy]
                        
                        print(f"\n{self.color_text(strategy, 'cyan')}:")
                        
                        # Pure cost
                        pure = data['pure_cost']
                        print(f"  Pure cost assignment:")
                        print(f"    Total cost: {pure['total_cost']}")
                        print(f"    Store loads: {pure['store_loads']}")
                        
                        # Balanced
                        balanced = data['balanced']
                        print(f"  Balanced assignment:")
                        print(f"    Total cost: {balanced['total_cost']}")
                        print(f"    Store loads: {balanced['store_loads']}")
            
            # Show sample delivery paths
            print(f"\n{self.color_text('SAMPLE DELIVERY PATHS:', 'yellow')}")
            if 'pairwise_analysis' in analysis:
                # Show first store-customer pair
                for pair_key, pair_data in list(analysis['pairwise_analysis'].items())[:2]:
                    store = pair_data['store']
                    customer = pair_data['customer']
                    print(f"\n  {store} → {customer}:")
                    
                    # Find best strategy
                    best_strat = None
                    best_cost = float('inf')
                    
                    for strategy, metrics in pair_data['metrics_by_strategy'].items():
                        if metrics['path_found'] and metrics['cost'] < best_cost:
                            best_cost = metrics['cost']
                            best_strat = strategy
                    
                    if best_strat:
                        print(f"    Best: {best_strat} with cost {best_cost}")
        
        except Exception as e:
            print(f"{self.color_text(f'Error running planner: {e}', 'red')}")
        
        input(f"\n{self.color_text('Press Enter to continue...', 'gray')}")
    
    def save_grid(self):
        """Save current grid to file"""
        if not self.grid:
            print(f"{self.color_text('No grid to save!', 'red')}")
            return
        
        filename = input(f"{self.color_text('Filename to save (default: grid.json)', 'green')}: ").strip()
        if not filename:
            filename = "grid.json"
        
        try:
            # Convert grid to serializable format
            grid_data = {
                'm': self.grid.m,
                'n': self.grid.n,
                'stores': [(pos.x, pos.y) for pos in self.grid.stores],
                'customers': [(pos.x, pos.y) for pos in self.grid.customers],
                'traffic': {},
                'tunnels': [],
                'user_settings': self.user_settings,
            }
            
            # Convert traffic edges
            for edge, cost in self.grid.traffic.items():
                key = f"{edge.pos1.x},{edge.pos1.y}-{edge.pos2.x},{edge.pos2.y}"
                grid_data['traffic'][key] = cost
            
            # Convert tunnels
            seen = set()
            for entrance, exit_pos in self.grid.tunnels.items():
                pair = tuple(sorted([(entrance.x, entrance.y), (exit_pos.x, exit_pos.y)]))
                if pair not in seen:
                    grid_data['tunnels'].append(pair)
                    seen.add(pair)
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(grid_data, f, indent=2)
            
            print(f"{self.color_text(f'Grid saved to {filename}', 'green')}")
            
        except Exception as e:
            print(f"{self.color_text(f'Error saving grid: {e}', 'red')}")
        
        input(f"\n{self.color_text('Press Enter to continue...', 'gray')}")
    
    def load_grid(self):
        """Load grid from file"""
        filename = input(f"{self.color_text('Filename to load', 'green')}: ").strip()
        
        if not os.path.exists(filename):
            print(f"{self.color_text(f'File {filename} not found!', 'red')}")
            return
        
        try:
            with open(filename, 'r') as f:
                grid_data = json.load(f)
            
            # Create grid
            self.grid = Grid(grid_data['m'], grid_data['n'])
            
            # Add stores
            for x, y in grid_data['stores']:
                self.grid.add_store(Position(x, y))
            
            # Add customers
            for x, y in grid_data['customers']:
                self.grid.add_customer(Position(x, y))
            
            # Add traffic
            for edge_str, cost in grid_data['traffic'].items():
                pos1_str, pos2_str = edge_str.split('-')
                x1, y1 = map(int, pos1_str.split(','))
                x2, y2 = map(int, pos2_str.split(','))
                self.grid.set_traffic(Position(x1, y1), Position(x2, y2), cost)
            
            # Add tunnels
            for (x1, y1), (x2, y2) in grid_data['tunnels']:
                self.grid.add_tunnel(Position(x1, y1), Position(x2, y2))
            
            # Load user settings if available
            if 'user_settings' in grid_data:
                self.user_settings.update(grid_data['user_settings'])
            
            print(f"{self.color_text(f'Grid loaded from {filename}', 'green')}")
            print(f"  Size: {self.grid.m}x{self.grid.n}")
            print(f"  Stores: {len(self.grid.stores)}")
            print(f"  Customers: {len(self.grid.customers)}")
            
        except Exception as e:
            print(f"{self.color_text(f'Error loading grid: {e}', 'red')}")
        
        input(f"\n{self.color_text('Press Enter to continue...', 'gray')}")
    
    def run(self):
        """Main interactive loop"""
        self.clear_screen()
        
        print(f"{self.color_text('='*80, 'cyan')}")
        print(f"{self.color_text(' ' * 25 + 'INTERACTIVE DELIVERY VISUALIZER', 'yellow')}")
        print(f"{self.color_text(' ' * 20 + 'FULL USER CONTROL - EVERYTHING TUNABLE', 'cyan')}")
        print(f"{self.color_text('='*80, 'cyan')}")
        
        time.sleep(1.5)
        
        while self.running:
            # Main menu
            menu_items = {
                'generate': 'Generate New Random Grid',
                'visualize': 'Visualize Current Grid',
                'select': 'Select Store & Customer',
                'search': 'Run Search Algorithm',
                'planner': 'Run Delivery Planner',
                'settings': 'Configure Visualization Settings',
                'search_settings': 'Configure Search Settings',
                'save': 'Save Current Grid',
                'load': 'Load Grid from File',
                'demo': 'Run Full Demo',
            }
            
            choice = self.display_menu(menu_items, "MAIN CONTROL PANEL")
            
            if choice == 'exit':
                self.running = False
                print(f"\n{self.color_text('Goodbye!', 'cyan')}")
            
            elif choice == 'generate':
                self.generate_random_grid()
            
            elif choice == 'visualize':
                if self.grid:
                    self.visualize_grid()
                    input(f"\n{self.color_text('Press Enter to continue...', 'gray')}")
                else:
                    print(f"{self.color_text('No grid loaded! Generate one first.', 'red')}")
                    time.sleep(1.5)
            
            elif choice == 'select':
                self.select_elements()
            
            elif choice == 'search':
                self.run_search()
            
            elif choice == 'planner':
                self.run_delivery_planner()
            
            elif choice == 'settings':
                self.configure_visualization()
            
            elif choice == 'search_settings':
                self.configure_search_settings()
            
            elif choice == 'save':
                self.save_grid()
            
            elif choice == 'load':
                self.load_grid()
            
            elif choice == 'demo':
                self.run_demo()
            
            else:
                print(f"{self.color_text('Invalid choice!', 'red')}")
                time.sleep(1)
    
    def run_demo(self):
        """Run a complete demo"""
        self.clear_screen()
        self.display_header("FULL DEMO MODE")
        
        print(f"\n{self.color_text('Running complete demonstration...', 'cyan')}")
        print(f"This will:")
        print(f"  1. Generate a random grid")
        print(f"  2. Visualize it")
        print(f"  3. Select random store and customer")
        print(f"  4. Run multiple search algorithms")
        print(f"  5. Show delivery planning")
        
        input(f"\n{self.color_text('Press Enter to start demo...', 'green')}")
        
        # Step 1: Generate grid
        print(f"\n{self.color_text('Step 1: Generating random grid...', 'yellow')}")
        self.user_settings.update({
            'grid_width': 10,
            'grid_height': 10,
            'min_stores': 3,
            'max_stores': 3,
            'min_customers': 5,
            'max_customers': 5,
            'obstacle_density': 0.1,
            'tunnel_density': 0.3,
        })
        self.generate_random_grid()
        
        # Step 2: Visualize
        print(f"\n{self.color_text('Step 2: Visualizing grid...', 'yellow')}")
        self.visualize_grid()
        time.sleep(2)
        
        # Step 3: Select elements
        print(f"\n{self.color_text('Step 3: Selecting random store and customer...', 'yellow')}")
        self.selected_store = random.choice(self.grid.stores)
        self.selected_customer = random.choice(self.grid.customers)
        print(f"Selected: Store at {self.selected_store}, Customer at {self.selected_customer}")
        time.sleep(1.5)
        
        # Step 4: Run searches
        print(f"\n{self.color_text('Step 4: Running search algorithms...', 'yellow')}")
        self.user_settings['animate_search'] = False
        strategies = ['BF', 'UC', 'GR1', 'AS1']
        
        for strategy in strategies:
            print(f"\n  Running {strategy}...")
            problem = DeliveryProblem(self.grid, self.selected_store, self.selected_customer)
            search = GenericSearch(problem, strategy=strategy)
            path, cost, nodes = search.solve()
            
            if path:
                print(f"    ✓ Found path with cost {cost} ({nodes} nodes)")
            else:
                print(f"    ✗ No path found ({nodes} nodes)")
            
            time.sleep(0.5)
        
        # Step 5: Show path
        print(f"\n{self.color_text('Step 5: Visualizing best path...', 'yellow')}")
        problem = DeliveryProblem(self.grid, self.selected_store, self.selected_customer)
        search = GenericSearch(problem, strategy='AS1')
        path, cost, nodes = search.solve()
        
        if path:
            path_positions = self.path_to_positions(path)
            self.visualize_grid(path=path_positions)
            print(f"\nBest path found by A*:")
            print(f"  Cost: {cost}")
            print(f"  Steps: {len(path)}")
            print(f"  Path: {' → '.join(path[:5])}..." if len(path) > 5 else f"Path: {' → '.join(path)}")
        else:
            print(f"{self.color_text('No path found!', 'red')}")
        
        input(f"\n{self.color_text('Demo complete! Press Enter to continue...', 'green')}")


def main():
    """Main entry point"""
    try:
        visualizer = InteractiveConsole()
        visualizer.run()
    except KeyboardInterrupt:
        print(f"\n\n{ConsoleVisualizer.COLORS['cyan']}Program interrupted by user{ConsoleVisualizer.COLORS['reset']}")
    except Exception as e:
        print(f"\n\n{ConsoleVisualizer.COLORS['red']}Unexpected error: {e}{ConsoleVisualizer.COLORS['reset']}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()