import requests
import re
from core.config.config import AMADEUS_API_KEY, AMADEUS_API_SECRET
import numpy as np
import time
from datetime import datetime, timedelta

MAX_RETRIES = 5

# Token management
_token = None
_token_expiry = None

def get_access_token():
	"""Get a valid access token, refreshing if necessary"""
	global _token, _token_expiry
	
	# Check if we have a valid token
	if _token and _token_expiry and datetime.now() < _token_expiry:
		return _token
	
	# Token expired or doesn't exist, get a new one
	print("Fetching new access token...")
	url = "https://test.api.amadeus.com/v1/security/oauth2/token"
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	data = {
		"grant_type": "client_credentials",
		"client_id": AMADEUS_API_KEY,
		"client_secret": AMADEUS_API_SECRET
	}
	
	response = requests.post(url, headers=headers, data=data)
	
	if response.status_code != 200:
		raise Exception(f"Failed to get access token: {response.text}")
	
	token_data = response.json()
	_token = token_data['access_token']
	# Set expiry to 5 minutes before actual expiry for safety
	_token_expiry = datetime.now() + timedelta(seconds=token_data['expires_in'] - 300)
	
	print(f"New token obtained, expires at {_token_expiry}")
	return _token

def get_flight_cost_time(origin_iata: str, dest_iata: str, departure_date: str, max_retries: int = MAX_RETRIES):
	# First try: Direct flights only
	result = _fetch_flight(origin_iata, dest_iata, departure_date, non_stop=True, max_retries=max_retries)
	
	if result is None:
		# No direct flight available, try with connections
		print(f"  No direct flight, trying with connections...")
		result = _fetch_flight(origin_iata, dest_iata, departure_date, non_stop=False, max_retries=max_retries)
	
	if result is None:
		return (float('inf'), float('inf'))
	
	# For backward compatibility with TSP (which expects tuple)
	return (result['price'], result['duration'])

def get_flight_details(origin_iata: str, dest_iata: str, departure_date: str, max_retries: int = MAX_RETRIES):
	"""Returns full flight details including times and segments"""
	result = _fetch_flight(origin_iata, dest_iata, departure_date, non_stop=True, max_retries=max_retries)
	
	if result is None:
		print(f"  No direct flight, trying with connections...")
		result = _fetch_flight(origin_iata, dest_iata, departure_date, non_stop=False, max_retries=max_retries)
	
	if result is None:
		return None
	
	return result

def _fetch_flight(origin_iata: str, dest_iata: str, departure_date: str, non_stop: bool, max_retries: int = MAX_RETRIES):
	"""Internal helper to fetch flight with or without nonStop parameter"""
	non_stop_param = "&nonStop=true" if non_stop else ""
	url = f'https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={origin_iata}&destinationLocationCode={dest_iata}&departureDate={departure_date}&adults=1&max=1&currencyCode=GBP{non_stop_param}'

	for attempt in range(max_retries):
		try:
			# Get fresh token for each request
			token = get_access_token()
			headers = {'Authorization': f'Bearer {token}'}
			
			response = requests.get(url, headers=headers)
			
			# Check for auth errors (token might have expired mid-request)
			if response.status_code == 401:
				print(f'  Token expired, refreshing...')
				global _token, _token_expiry
				_token = None
				_token_expiry = None
				if attempt < max_retries - 1:
					time.sleep(1)
					continue
			
			if response.status_code == 500:
				print(f'  Attempt {attempt + 1}/{max_retries} failed (500 error)')
				if attempt < max_retries - 1:
					time.sleep(1)
					continue
				else:
					return None
			
			data = response.json()
			
			if not data.get('data'):
				return None
			
			print(f'  Got flight data for {origin_iata}->{dest_iata}')
			flight = data['data'][0]
			itinerary = flight['itineraries'][0]
			segments = itinerary['segments']
			
			# Extract flight details
			price = float(flight['price']['total'])
			duration_iso = itinerary['duration']
			duration_hours = parse_duration(duration_iso)
			
			# Get departure from first segment, arrival from last segment
			departure_time = segments[0]['departure']['at'].split('T')[1][:5]
			arrival_time = segments[-1]['arrival']['at'].split('T')[1][:5]
			stops = len(segments) - 1
			
			# Build segment details
			segment_details = []
			for seg in segments:
				segment_details.append({
					'from': seg['departure']['iataCode'],
					'to': seg['arrival']['iataCode'],
					'departure': seg['departure']['at'].split('T')[1][:5],
					'arrival': seg['arrival']['at'].split('T')[1][:5]
				})
			
			return {
				'price': price,
				'duration': duration_hours,
				'departure_time': departure_time,
				'arrival_time': arrival_time,
				'stops': stops,
				'segments': segment_details
			}
			
		except Exception as e:
			print(f'  Attempt {attempt + 1}/{max_retries} failed: {e}')
			if attempt < max_retries - 1:
				time.sleep(1)
				continue
			else:
				return None
	
	return None

def parse_duration(iso_duration):
	match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', iso_duration)
	hours = int(match.group(1)) if match.group(1) else 0
	minutes = int(match.group(2)) if match.group(2) else 0
	return hours + (minutes / 60)

def create_matrix(departure_date: str):
	cities = [
		'London', 'Dublin', 'Lisbon', 'Barcelona', 'Paris', 'Amsterdam',
		'Rome', 'Copenhagen', 'Berlin', 'Prague', 'Vienna', 'Zagreb',
		'Budapest', 'Warsaw', 'Belgrade', 'Athens', 'Sofia', 'Bucharest',
		'Istanbul'
	]
	iata_codes = {
		'London': 'LHR',
		'Dublin': 'DUB',
		'Lisbon': 'LIS',
		'Barcelona': 'BCN',
		'Paris': 'CDG',
		'Amsterdam': 'AMS',
		'Rome': 'FCO',
		'Copenhagen': 'CPH',
		'Berlin': 'BER',
		'Prague': 'PRG',
		'Vienna': 'VIE',
		'Zagreb': 'ZAG',
		'Budapest': 'BUD',
		'Warsaw': 'WAW',
		'Belgrade': 'BEG',
		'Athens': 'ATH',
		'Sofia': 'SOF',
		'Bucharest': 'OTP',
		'Istanbul': 'IST'
	}
	
	n = len(cities)
	cost_matrix = np.zeros((n, n))
	time_matrix = np.zeros((n, n))
	
	for i, origin_city in enumerate(cities):
		for j, dest_city in enumerate(cities):
			if i == j:
				continue
			
			origin_iata = iata_codes[origin_city]
			dest_iata = iata_codes[dest_city]
			print(f'Fetching {origin_iata} -> {dest_iata}')
			
			try:
				cost, time_hours = get_flight_cost_time(origin_iata, dest_iata, departure_date)
				cost_matrix[i][j] = cost
				time_matrix[i][j] = time_hours
				time.sleep(0.3)
			except Exception as e:
				print(f'Error fetching {origin_iata} -> {dest_iata}: {e}')
				cost_matrix[i][j] = float('inf')
				time_matrix[i][j] = float('inf')
	
	# Return data in cacheable format
	return {
		'cities': cities,
		'iata_codes': iata_codes,
		'cost_matrix': cost_matrix.tolist(),
		'time_matrix': time_matrix.tolist(),
		'timestamp': datetime.now().isoformat(),
		'reference_date': departure_date
	}