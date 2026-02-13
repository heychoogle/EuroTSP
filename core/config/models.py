from pydantic import BaseModel
from typing import List
from datetime import date

class ItineraryRequest(BaseModel):
    selected_cities: List[str] = [] # array of cities to be visited (not including the return to the depot city)
    days_per_city: List[int] = []   # array of ful days to spent in each city where 1 day = 1 full day not travelling, INCLUDING 0 for the return to the depot city
    time_weight: int # value assigned to each unit of time for the purposes of 
    start_date: date # date on which travels should begin e.g. 'travel from depot city to city 1 on this date'