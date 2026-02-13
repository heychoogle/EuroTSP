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