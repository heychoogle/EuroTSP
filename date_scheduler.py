import datetime
from api_helper import get_flight_details

def schedule_itinerary(start_date, optimal_city_route, optimal_city_route_iata, leg_modes, days_per_city) -> dict:
    """
    Schedules flights/trains such that days_per_city[i] = full days spent in city i AFTER arrival.
    The first city is the home city (departure), so 0 full days there is fine.
    """
    itinerary_dict = {}

    departure_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    departure_date = departure_datetime.date()

    n = len(optimal_city_route)

    for i in range(n - 1):
        city = optimal_city_route[i]
        next_city = optimal_city_route[i + 1]

        # Current leg departs today
        itinerary_dict[f'{i}'] = {
            "origin_city": city,
            "dest_city": next_city,
            "origin_iata": optimal_city_route_iata[i],
            "dest_iata": optimal_city_route_iata[i + 1],
            "departure_date": departure_date.strftime("%Y-%m-%d"),
            "mode": leg_modes[i]
        }

        # Print current leg
        print(f"Depart {city} on {departure_date}, heading to {next_city} via {leg_modes[i]}")

        # Stay full days in next city after arriving
        full_days_in_next_city = days_per_city[i + 1]  # i+1 = arrival city
        next_departure_date = departure_date + datetime.timedelta(days=1 + full_days_in_next_city)
        if full_days_in_next_city > 0:
            print(f"Remain in {next_city} for {full_days_in_next_city} full day(s), until {next_departure_date}")

        # Update departure_date for next iteration
        departure_date = next_departure_date

    return itinerary_dict


def get_bookable_itinerary(itinerary_dict, train_corridors):
    """
    Returns bookable details per leg.
    Uses train corridor data if leg is a train, otherwise fetches flight details.
    """
    from api_helper import get_flight_details
    
    bookable_legs = {}
    
    for leg_id, leg_data in itinerary_dict.items():
        origin = leg_data['origin_iata']
        dest = leg_data['dest_iata']
        date = leg_data['departure_date'] 
        mode = leg_data['mode']
        
        if mode == "train":
            corridor = train_corridors.get((leg_data['origin_city'], leg_data['dest_city'])) \
                       or train_corridors.get((leg_data['dest_city'], leg_data['origin_city']))
            price = sum(corridor["fare"]) / 2
            duration = sum(corridor["time"]) / 2
            bookable_legs[leg_id] = {
                'origin': origin,
                'dest': dest,
                'date': date,          
                'mode': 'train',
                'price': price,         
                'duration': duration,   
                'segments': [{
                    "from": origin,
                    "to": dest,
                    "departure": date,
                    "arrival": date 
                }]
            }
            print(f"Train leg: {origin} → {dest}, cost £{price:.2f}, time {duration:.2f}h")
        else:
            # Flight leg
            print(f"\nFetching flights for {origin} → {dest} on {date}...")
            flight_details = get_flight_details(origin, dest, date)
            if flight_details:
                bookable_legs[leg_id] = {
                    'origin': origin,
                    'dest': dest,
                    'date': date,            
                    'mode': 'flight',
                    'price': flight_details.get('price', 0),
                    'duration': flight_details.get('duration', 0),
                    'segments': flight_details.get('segments', [])
                }
            else:
                bookable_legs[leg_id] = None
    
    return bookable_legs

