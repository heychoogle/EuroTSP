import datetime

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
        itinerary_dict[i] = {
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

    print('\n')
    return itinerary_dict