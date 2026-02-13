# EuroTSP

EuroTSP is a multi-modal European route optimization engine designed to compute the most cost-effective and/or time-efficient travel sequence across multiple cities, weighted based on cost/time preference. The system combines flights and train data and leverages TSP-based constraint solving (via Google OR Tools) to generate structured, bookable itineraries from heterogeneous datasets.

---

## Data Flow 
- The client calls the **API** with selected cities, days per city, time weighting, and a trip start date
- The **Matrix Utils Service** loads and filters the prediction matrix for the requested cities.
- The **Route Optimiser Service** solves a weighted TSP using this matrix to compute the optimal visit order
- The **Itinerary Handler Service** schedules each leg according to the start date and requested stay durations
   - This scheduled route is also resolved into real, bookable flights or trains by this service
- A structured JSON itinerary is returned to the client

---

## Stack
- Python  
   - Google OR-Tools  
   - NumPy  
   - Requests
   - Uvicorn & FastAPI
- Amadeus Flights API
- Docker Compose  

---

## Services

### **API**
- Publishes the `/calculate_itinerary` POST endpoint
- Takes an `ItineraryRequest` JSON model as a request body
- Synchronously calls subsequent services to generate different components of the optimised route
- Returns a JSONified bookable itinerary

<details>
  <summary>ItineraryRequest Model</summary>

  ```python
   class ItineraryRequest(BaseModel):
       # array of cities to be visited (not including the return to the city of origin at the end)
       selected_cities: List[str] = [] 
       # array of full days spent not travelling per city (including 0 at the end for return to city of origin)
       days_per_city: List[int] = []   
       # value assigned to each unit of time for cost/time matrix weighting
       time_weight: int
       # date on which travels should begin e.g. travel from depot city to city 1 on this date
       start_date: date 
   ```
</details>

<details>
  <summary>Example /calculate_itinerary POST request</summary>

  ```bash
   curl -X POST http://localhost:8000/calculate_itinerary \
        -H "Content-Type: application/json" \
        -d '{
              "selected_cities": ["Berlin", "Prague"],
              "days_per_city": [0, 1, 0],
              "time_weight": 1,
              "start_date": "2026-05-11"
            }'
   ```
</details>

<details>
  <summary>Example /calculate_itinerary response</summary>

   ```json
   {
     "bookable_legs": {
       "0": {
         "date": "2026-05-11",
         "dest": "PRG",
         "duration": 4.5,
         "mode": "train",
         "origin": "BER",
         "price": 30.0,
         "segments": [
           {
             "arrival": "2026-05-11",
             "departure": "2026-05-11",
             "from": "BER",
             "to": "PRG"
           }
         ]
       },
       "1": {
         "date": "2026-05-13",
         "dest": "BER",

         "duration": 4.5,
         "mode": "train",
         "origin": "PRG",
         "price": 30.0,
         "segments": [
           {
             "arrival": "2026-05-13",
             "departure": "2026-05-13",
             "from": "PRG",
             "to": "BER"
           }
         ]
       }
     },
     "metadata": {
       "end_date": "2026-05-13",
       "start_date": "2026-05-11",
       "total_cost": 60.0,
       "total_duration": 9.0
     }
   }
   ```
</details>

#

### **Matrix Utils Service**
   - Saves updated flight data matrix / loads active flight data matrix into the Route Optimiser.
   - Applies a filter to the flight data matrix to only load rows/columns relevant to selected cities, reducing data throughput for the Route Optimiser service.

#

### **Route Optimiser Service**  
   - Computes the (predicted) optimal sequence of cities using **Traveling Salesperson Problem (TSP)** algorithms (using Google OR-Tools) with weighted cost-time matrices. 
      - The flight data matrix serves as a 'prediction' that moving from city X to city Y is cheaper than city X to city Z, so for cities X, Y, Z, it predicts X→Y is cheaper than X→Z.
   - Produces a preliminary route based on that prediction matrix including modes of transport (flight/train) and IATA codes.

#

### **Itinerary Handler Service** 

   #### **Itinerary Scheduler**  
   - Converts preliminary optimised routes into **date-constrained itineraries**.  
   - Allocates days per city and applies scheduling rules to produce a realistic travel plan.  
   - Outputs a structured itinerary ready for booking.

   #### **Bookable Itinerary Service**  
   - Maps scheduled itinerary legs to **real-world flights and trains** using available corridor data or fetching flights.  
   - Ensures each segment is bookable and respects travel constraints.  
   - Returns a fully actionable, structured travel plan in JSON format.

---

## Current Features
- Multi-modal route optimisation across flights and trains.  
- Weighted cost-time TSP solver for flexible prioritization.
- Date-constrained per-node scheduling to produce realistic itineraries.  
- Mapping of abstract routes to bookable flights and train segments.    

## Future Features / Challenges in Development
- Potential Rail (ticketing) API access (thus far, none exist that are open to the public)
   - Many exist to tell you, "a train exists from A to B at Y time", but none that provide accurate ticketing/cost data. Many carriers also have extremely spotty coverage of this.
- Worldwide functionality
   - Theoretically, this will work right now - but computing a matrix for 19 destinations is already a large amount of our free Amadeus API quota and we can't really go much higher.
- New Flight API integrations
   - Amadeus shuts down in July 2026 for free consumers; a new API will definitely need to be found.

---
