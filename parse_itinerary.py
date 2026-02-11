import json
from datetime import date, datetime

def print_pretty_itinerary(itinerary_json: str):
	with open(itinerary_json, 'r') as f:
		bookable_itinerary = json.load(f)

	print('\n')

	total_cost = sum([bookable_itinerary[leg]["price"] for leg in bookable_itinerary])
	print(f'Total Cost: £{total_cost:.2f}')

	total_time = sum([bookable_itinerary[leg]["duration"] for leg in bookable_itinerary])
	total_time_hours = total_time // 1
	total_time_minutes = (total_time - total_time_hours) * 60
	print(f'Total Travel Time: {total_time_hours:.0f}h {total_time_minutes:.0f}m')

	start_date = [bookable_itinerary[leg]["date"] for leg in bookable_itinerary][0]
	end_date =	 [bookable_itinerary[leg]["date"] for leg in bookable_itinerary][-1]
	duration = (
		(datetime.strptime(end_date, "%Y-%m-%d").date()) 
		- 
		(datetime.strptime(start_date, "%Y-%m-%d").date()) 
	).days
	print(f'Trip duration: {start_date} to {end_date} ({duration} days)')

	print('-----')

	for leg in bookable_itinerary:
		cur_leg = bookable_itinerary[leg]
		dest = cur_leg['dest']
		segments = cur_leg['segments']

		flights = [f'{(segment["from"])} ->' for segment in segments]
		print(f'Leg {int(leg)+1} ({' '.join(flight for flight in flights)} {dest})')

		date = cur_leg["date"]
		print(f'Date: {date}')

		leg_duration = cur_leg["duration"]
		price = cur_leg["price"]
		leg_duration_hours = leg_duration // 1
		leg_duration_minutes = (leg_duration - leg_duration_hours) * 60
		mode = cur_leg.get("mode", "flight")  # fallback to flight if missing
		if mode == "train":
			mode_label = "Train"
		elif mode == "flight":
			mode_label = "Direct Flight" if len(segments) == 1 else f"{len(segments)} Flights"
		else:
			mode_label = mode.capitalize()

		print(f'Duration: {leg_duration_hours:.0f}h {leg_duration_minutes:.0f}m | {mode_label}')

		for segment in segments:
			departure_time = segment["departure"]
			arrival_time = segment["arrival"]
			print(f'Depart: {departure_time} | Arrive: {arrival_time} {(f'({segment["from"]} -> {segment["to"]})') if len(segments) > 1 else ""}')

		print(f'Cost: £{price:.2f}')
		print('\n')

# print_pretty_itinerary('bookable_itinerary.json')