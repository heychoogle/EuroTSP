from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from matrix_utils import load_cached_matrix, save_matrix_cache, filter_matrix_by_cities
from api_helper import create_matrix
import math

def create_data_model(time_weight_arg, selected_cities=None):
    """Stores the data for the problem with multi-modal (train + flight) logic."""
    matrix_data = load_cached_matrix()

    if matrix_data is None:
        # Cache miss or stale, rebuild
        matrix_data = create_matrix("2026-05-12")
        save_matrix_cache(matrix_data)

    # Filter matrix if user selected specific cities
    if selected_cities is not None:
        matrix_data = filter_matrix_by_cities(matrix_data, selected_cities)

    cost_matrix = matrix_data['cost_matrix']
    time_matrix = matrix_data['time_matrix']
    cities = matrix_data['cities']

    # Train corridor dictionary with realistic fares/times
    train_corridors = {
        ("London", "Paris"): {"fare": (50, 80), "time": (2.5, 2.75)},
        ("Paris", "Amsterdam"): {"fare": (30, 50), "time": (3.5, 3.5)},
        ("Berlin", "Prague"): {"fare": (20, 40), "time": (4, 5)},
        ("Vienna", "Budapest"): {"fare": (10, 20), "time": (2, 3)},
        ("Prague", "Vienna"): {"fare": (15, 25), "time": (4, 4.5)}
    }

    # Combined weight: cost + (time_weight * time)
    time_weight = time_weight_arg
    distance_matrix = []
    mode_matrix = []

    for i, origin in enumerate(cities):
        row = []
        mode_row = []
        for j, dest in enumerate(cities):
            if i == j:
                weight = 0
                mode = None
            elif (origin, dest) in train_corridors or (dest, origin) in train_corridors:
                corridor = train_corridors.get((origin, dest)) or train_corridors.get((dest, origin))
                fare = sum(corridor["fare"]) / 2
                travel_time = sum(corridor["time"]) / 2
                weight = fare + (time_weight * travel_time)
                mode = "train"
            else:
                # Default to flight
                fare = cost_matrix[i][j]
                travel_time = time_matrix[i][j]
                weight = fare + (time_weight * travel_time)
                mode = "flight"

            if math.isinf(weight):
                weight = 10**9

            row.append(int(weight))  # OR-Tools requires integers
            mode_row.append(mode)
        distance_matrix.append(row)
        mode_matrix.append(mode_row)

    matrix_data['distance_matrix'] = distance_matrix
    matrix_data['mode_matrix'] = mode_matrix
    matrix_data['train_corridors'] = train_corridors  # for printing costs/times
    matrix_data['num_vehicles'] = 1
    matrix_data['depot'] = 0

    return matrix_data


def print_solution(manager, routing, solution, data):
    """Prints solution on console with correct train/flight costs and returns route data including modes."""
    print('\n=== OPTIMAL ROUTE ===')
    index = routing.Start(0)
    cities = data['cities']
    distance_matrix = data['distance_matrix']
    mode_matrix = data['mode_matrix']
    train_corridors = data.get('train_corridors', {})

    route_cost = 0
    route_time = 0
    route = []
    route_modes = []  # <-- add mode list

    while not routing.IsEnd(index):
        city_index = manager.IndexToNode(index)
        route.append(cities[city_index])
        previous_index = index
        index = solution.Value(routing.NextVar(index))

        from_idx = manager.IndexToNode(previous_index)
        to_idx = manager.IndexToNode(index)

        mode = mode_matrix[from_idx][to_idx]
        route_modes.append(mode)  # <-- store mode for this leg

        if mode == "train":
            corridor = train_corridors.get((cities[from_idx], cities[to_idx])) \
                       or train_corridors.get((cities[to_idx], cities[from_idx]))
            fare = sum(corridor["fare"]) / 2
            travel_time = sum(corridor["time"]) / 2
        elif mode == "flight":
            fare = data['cost_matrix'][from_idx][to_idx]
            travel_time = data['time_matrix'][from_idx][to_idx]
        else:
            fare = 0
            travel_time = 0

        route_cost += fare
        route_time += travel_time
        print(f'{cities[from_idx]} -> {cities[to_idx]} via {mode}, cost £{fare:.2f}, time {travel_time:.2f}h')

    print(f'\nTotal cost: £{route_cost:.2f}')
    print(f'Total time: {route_time:.2f} hours')
    print(f'Route order: {" → ".join(route)}')

    # Return route data including modes
    route_cities = route[:]
    route_iata = [data['iata_codes'][city] for city in route_cities]

    return {
        'cities': route_cities,
        'iata_codes': route_iata,
        'modes': route_modes,
        'total_cost': route_cost,
        'total_time': route_time,
        'train_corridors': train_corridors
    }


def main(time_weight, selected_cities):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(time_weight, selected_cities)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'],
        data['depot']
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        route_data = print_solution(manager, routing, solution, data)#
        return route_data
    else:
        print('No solution found!')
        return None