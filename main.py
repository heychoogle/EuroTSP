from core.tsp.route_optimiser import main as run_tsp
from core.itinerary_handler.schedule import schedule_itinerary
from core.itinerary_handler.bookable import get_bookable_itinerary
from core.itinerary_handler.parse import print_pretty_itinerary
from core.fs.save_itinerary import save_itinerary_json, save_pretty_itinerary

start_date = "2026-05-11"

# selected_cities = ["London", "Paris", "Amsterdam", "Berlin", "Prague", "Vienna", "Budapest"]
# days_per_city   = [0,              1,            1,       1,         1,        2,         1,        0]
selected_cities = ["Berlin", "Prague"]
days_per_city = [0, 1, 0]
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
bookable_json = save_itinerary_json(bookable)

# Format and display
print_pretty_itinerary(bookable_json)
save_pretty_itinerary(bookable_json)