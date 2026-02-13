import json
import os
from datetime import datetime, timedelta

def load_cached_matrix(cache_file='flight_matrix_cache.json', max_age_days=365):
    """Load matrix from cache if it exists and is recent enough"""
    if not os.path.exists(cache_file):
        return None
    
    with open(cache_file, 'r') as f:
        cache = json.load(f)
    
    # Check if cache is too old
    cache_time = datetime.fromisoformat(cache['timestamp'])
    if datetime.now() - cache_time > timedelta(days=max_age_days):
        print(f"Cache is {(datetime.now() - cache_time).days} days old, rebuilding...")
        return None
    
    print(f"Using cached matrix from {cache['timestamp']}")
    return cache

def save_matrix_cache(matrix_data, cache_file='flight_matrix_cache.json') -> None:
    """Save matrix data to cache file"""
    with open(cache_file, 'w') as f:
        json.dump(matrix_data, f, indent=2)
    print(f"Matrix cached to {cache_file}")

def filter_matrix_by_cities(full_matrix_data, selected_cities) -> dict:
    """
    Extract a submatrix containing only the selected cities.
    
    Args:
        full_matrix_data: Complete matrix data with all cities
        selected_cities: List of city names user wants to visit
    
    Returns:
        Filtered matrix data with only selected cities
    """
    all_cities = full_matrix_data['cities']
    iata_codes = full_matrix_data['iata_codes']
    
    # Get indices of selected cities in the full matrix
    indices = [all_cities.index(city) for city in selected_cities]
    
    # Extract submatrices
    cost_matrix = [[full_matrix_data['cost_matrix'][i][j] for j in indices] for i in indices]
    time_matrix = [[full_matrix_data['time_matrix'][i][j] for j in indices] for i in indices]
    
    # Extract IATA codes for selected cities
    selected_iata_codes = {city: iata_codes[city] for city in selected_cities}
    
    return {
        'cities': selected_cities,
        'iata_codes': selected_iata_codes,
        'cost_matrix': cost_matrix,
        'time_matrix': time_matrix,
        'timestamp': full_matrix_data['timestamp'],
        'reference_date': full_matrix_data['reference_date']
    }

# eventually we will move this to its own JSON file
def load_surface_corridors() -> dict:
    surface_corridors = {
        ("London", "Paris"):        {"fare": (50, 80),      "time": (4, 5),     "mode": "train"},
        ("London", "Amsterdam"):    {"fare": (70, 100),     "time": (4, 5.5),   "mode": "train"},
        ("Paris", "Amsterdam"):     {"fare": (30, 50),      "time": (3.5, 3.5), "mode": "train"},
        ("Paris", "Barcelona"):     {"fare": (100, 130),    "time": (7, 8),     "mode": "train"},
        ("Berlin", "Prague"):       {"fare": (20, 40),      "time": (4, 5.5),   "mode": "train"},
        ("Berlin", "Warsaw"):       {"fare": (30, 40),      "time": (5, 5.4),   "mode": "train"},
        ("Berlin", "Copenhagen"):   {"fare": (40, 60),      "time": (7, 8.5),   "mode": "train"},
        ("Vienna", "Budapest"):     {"fare": (10, 20),      "time": (2, 3),     "mode": "train"},
        ("Vienna", "Prague"):       {"fare": (15, 25),      "time": (4, 4.5),   "mode": "train"},
        ("Vienna", "Zagreb"):       {"fare": (20, 25),      "time": (5, 6),     "mode": "coach"},
        ("Belgrade", "Budapest"):   {"fare": (20, 25),      "time": (6, 6),     "mode": "coach"},
        ("Sofia", "Bucharest"):     {"fare": (10, 20),      "time": (6.5, 7),   "mode": "coach"},
        ("Sofia", "Athens"):        {"fare": (50, 60),      "time": (11, 12),   "mode": "coach"},
        ("Istanbul", "Sofia"):      {"fare": (30, 40),      "time": (8, 10),    "mode": "coach"},
        ("Istanbul", "Bucharest"):  {"fare": (35, 45),      "time": (11, 11.5), "mode": "coach"},
        ("Zagreb", "Budapest"):     {"fare": (15, 25),      "time": (4, 5),     "mode": "coach"},
        ("Zagreb", "Belgrade"):     {"fare": (15, 25),      "time": (5, 6),     "mode": "coach"},
        ("Prague", "Warsaw"):       {"fare": (15, 25),      "time": (8, 10),    "mode": "coach"}
    }
    return surface_corridors