import numpy as np
from geopy.distance import distance, geodesic
from geopy import Point as GeoPoint
import json


def _read_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
    return data


def read_parameters_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    parameters = {item['parameter']: item['value'] for item in data}
    descriptions = {
        item['parameter']: {
            "description": item['description'],
            **({"choices": item['choices']} if 'choices' in item else {}),
        }
        for item in data
    }
    return parameters, descriptions


def _dist_matrix(locations):
    assert len(locations) > 1, "At least two points are required"
    m = len(locations)
    dist_matrix = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            loc1, loc2 = locations[i], locations[j]
            dist_matrix[i, j] = geodesic(loc1, loc2).miles
    return dist_matrix


def _generate_random_point(center, radius):
    r = radius * np.sqrt(np.random.rand())
    theta = np.random.uniform(0, 2 * np.pi)
    origin = GeoPoint(center)
    destination = distance(miles=r).destination(
        point=origin, bearing=np.degrees(theta)
    )
    return destination.latitude, destination.longitude


def extract_routes(x_matrix: np.array) -> list:
    """
    Extracts the routes followed by each vehicle based on the decision matrix.

    :param x_matrix: Binary decision matrix
    :return: List of routes (each route is a list of customer indices)
    """
    num_vehicles = np.sum(x_matrix[0] == 1)
    first_visits = np.where(x_matrix[0] == 1)[0]
    routes = [[0, int(v)] for v in first_visits]
    for vehicle in range(num_vehicles):
        route_terminated = False
        while not route_terminated:
            start = routes[vehicle][-1]
            next_customer = np.where(x_matrix[start] == 1)[0]
            if next_customer == 0:
                routes[vehicle].append(0)
                route_terminated = True
            else:
                routes[vehicle].append(int(next_customer))
    return routes
