from core.integrations.amadeus_api_helper import get_flight_details

def get_bookable_itinerary(itinerary_dict, train_corridors):
    """
    Returns bookable details per leg.
    Uses train corridor data if leg is a train, otherwise fetches flight details.
    """
    
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

    bookable_itinerary = {}
    bookable_itinerary['bookable_legs'] = bookable_legs

    metadata = {}
    metadata['end_date'] = bookable_legs[next(reversed(bookable_legs))]['date']
    metadata['start_date'] = bookable_legs[0]['date']

    metadata['total_cost'] = sum([ leg['price'] for leg in bookable_legs.values() if isinstance(leg, dict) ])
    metadata['total_duration'] = sum([ leg['duration'] for leg in bookable_legs.values() if isinstance(leg, dict) ])

    bookable_itinerary['metadata'] = metadata
    
    return bookable_itinerary

