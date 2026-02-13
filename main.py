from core.route_optimiser.tsp import main as run_tsp
from core.itinerary_handler.schedule import schedule_itinerary
from core.itinerary_handler.bookable import get_bookable_itinerary
from core.fs.save_itinerary import save_itinerary_json, save_pretty_itinerary
from core.config.models import ItineraryRequest

from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/calculate_itinerary")
async def calculate_itinerary(itinerary_request: ItineraryRequest) -> dict:
    selected_cities = itinerary_request.selected_cities
    days_per_city = itinerary_request.days_per_city
    time_weight = itinerary_request.time_weight
    start_date = itinerary_request.start_date

    # selected_cities = ["London", "Paris", "Amsterdam", "Berlin", "Prague", "Vienna", "Budapest"]
    # days_per_city   = [0,              1,            1,       1,         1,        2,         1,        0]

    # Run TSP to get optimal route (with city filter)
    route_data = run_tsp(time_weight=time_weight, selected_cities=selected_cities)
    if not route_data:
        raise HTTPException(
            status_code=500,
            detail="Error occurred during optimal route calculation"
        )

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
    save_pretty_itinerary(bookable_json)

    return bookable
    # # Format and display
    # print_pretty_itinerary(bookable_json)
    