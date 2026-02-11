from tsp_optimiser import main as run_tsp
from date_scheduler import schedule_itinerary, get_bookable_itinerary
from parse_itinerary import print_pretty_itinerary
import json
import uuid

start_date = "2026-05-11"

selected_cities = ["London", "Paris", "Amsterdam", "Berlin", "Prague", "Vienna", "Budapest"]
days_per_city   = [0,              1,            1,       1,         1,        2,         1]
time_weight = 1

# Run TSP to get optimal route (with city filter)
route_data = run_tsp(time_weight=time_weight, selected_cities=selected_cities)

# Schedule with dates
itinerary = schedule_itinerary(
    start_date,
    route_data['cities'],
    route_data['iata_codes'],
    route_data['modes'],
    days_per_city
)

# Get bookable flights
bookable = get_bookable_itinerary(itinerary, route_data['train_corridors'])
bookable_filename = f'{uuid.uuid4()}'
with open(f'itineraries/{bookable_filename}.json', 'w') as f:
    json.dump(bookable, f, indent=2)

# Format and display
print_pretty_itinerary(f'itineraries/{bookable_filename}.json')