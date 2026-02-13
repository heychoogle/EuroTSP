from uuid import uuid4
from pathlib import Path
import os
import json
import io
from contextlib import redirect_stdout

from core.itinerary_handler.parse import print_pretty_itinerary

output_dir = Path(__file__).resolve().parents[2] / "output" / "itineraries"

def save_itinerary_json(itinerary: dict) -> str:
	
	unique_id = f'{uuid4()}'[:8]
	filename = f'bookable_itinerary_{unique_id}.json'
	itinerary_filepath = f'{output_dir}/json'

	try:
		if not os.path.exists(itinerary_filepath):
			os.makedirs(itinerary_filepath)
		with open(f'{itinerary_filepath}/{filename}', 'w') as f:
			json.dump(itinerary, f, indent=2)
	except Exception as e:
		print(f'Failed to write file: {e}')

	return f'{itinerary_filepath}/{filename}'

def save_pretty_itinerary(itinerary_json_file: str) -> str:

    itinerary_json_file = Path(itinerary_json_file)

    # Extract UUID from filename
    # bookable_itinerary_<uuid>.json
    unique_id = itinerary_json_file.stem.replace("bookable_itinerary_", "")

    # Capture printed output
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print_pretty_itinerary(itinerary_json_file)

    # Create pretty output directory
    pretty_dir = output_dir / "pretty"
    pretty_dir.mkdir(parents=True, exist_ok=True)

    pretty_filename = f"pretty_itinerary_{unique_id}.txt"
    pretty_filepath = pretty_dir / pretty_filename

    with pretty_filepath.open("w") as f:
        f.write(buffer.getvalue())

    return pretty_filepath