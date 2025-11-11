# route_utils.py
from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Tuple

House = Dict[str, object]

def haversine_km(a: House, b: House) -> float:
    R = 6371.0
    dlat = radians(float(b["lat"]) - float(a["lat"]))
    dlon = radians(float(b["lon"]) - float(a["lon"]))
    A = sin(dlat/2)**2 + cos(radians(float(a["lat"]))) * cos(radians(float(b["lat"]))) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(A), sqrt(1 - A))
    return R * c

def build_distance_matrix(items: List[House]) -> List[List[float]]:
    n = len(items)
    D = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            d = haversine_km(items[i], items[j])
            D[i][j] = D[j][i] = d
    return D

def route_length_open(D: List[List[float]], route: List[int]) -> float:
    return sum(D[route[i]][route[i+1]] for i in range(len(route)-1))

def nearest_neighbor_open(D: List[List[float]], start: int) -> List[int]:
    n = len(D)
    unv = set(range(n))
    route = [start]
    unv.remove(start)
    cur = start
    while unv:
        nxt = min(unv, key=lambda j: D[cur][j])
        route.append(nxt)
        unv.remove(nxt)
        cur = nxt
    return route

def two_opt_open_fixed_ends(route: List[int], D: List[List[float]]) -> List[int]:
    best = route[:]
    best_len = route_length_open(D, best)
    n = len(best)
    if n < 4:
        return best
    improved = True
    while improved:
        improved = False
        for i in range(1, n-2):
            for k in range(i+1, n-1):
                cand = best[:i] + best[i:k+1][::-1] + best[k+1:]
                L = route_length_open(D, cand)
                if L + 1e-12 < best_len:
                    best, best_len = cand, L
                    improved = True
    return best

def optimize_open_route(houses: List[House], start_name: str, end_name: str) -> Tuple[List[House], float]:
    """Return ordered houses (open route start->end) and straight-line distance in km."""
    name_to_idx = {h["name"]: i for i, h in enumerate(houses)}
    if start_name not in name_to_idx or end_name not in name_to_idx:
        raise ValueError("Start or end not found in houses list.")

    D = build_distance_matrix(houses)
    s = name_to_idx[start_name]
    e = name_to_idx[end_name]

    route = nearest_neighbor_open(D, s)
    if route[-1] != e:  # force end at e
        route = [i for i in route if i != e] + [e]
    route = two_opt_open_fixed_ends(route, D)

    ordered = [houses[i] for i in route]
    dist = route_length_open(D, route)
    return ordered, dist

def google_maps_url(points: List[House]) -> str:
    if len(points) < 2:
        return ""
    origin = f'{points[0]["lat"]},{points[0]["lon"]}'
    dest = f'{points[-1]["lat"]},{points[-1]["lon"]}'
    waypoints = "|".join(f'{p["lat"]},{p["lon"]}' for p in points[1:-1])
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}"
    if waypoints:
        url += f"&waypoints={waypoints}"
    return url
