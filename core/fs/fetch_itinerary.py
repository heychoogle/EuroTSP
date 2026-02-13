import json

def fetch_itinerary(itinerary_id: str) -> dict:

	itinerary_filepath = f'output/itineraries/json/bookable_itinerary_{itinerary_id}.json'

	try:
		with open(itinerary_filepath, 'r') as f:
			itinerary_json = json.load(f)
	except Exception:
		itinerary_json = {}

	return itinerary_json