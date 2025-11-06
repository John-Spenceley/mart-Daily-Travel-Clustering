
from math import radians, sin, cos, asin, sqrt
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def nearest_unvisited(start_idx: int, points: List[Dict[str, Any]], visited: set) -> int:
    best_idx, best_dist = None, float("inf")
    s = points[start_idx]
    for i, p in enumerate(points):
        if i in visited or i == start_idx:
            continue
        d = haversine_km(s["lat"], s["lng"], p["lat"], p["lng"])
        if d < best_dist:
            best_idx, best_dist = i, d
    return best_idx

def cluster_by_radius(points: List[Dict[str, Any]], radius_km: float) -> List[List[int]]:
    remaining = set(range(len(points)))
    clusters: List[List[int]] = []
    while remaining:
        seed = remaining.pop()
        cluster = [seed]
        to_check = list(remaining)
        for i in to_check:
            d = haversine_km(points[seed]["lat"], points[seed]["lng"], points[i]["lat"], points[i]["lng"])
            if d <= radius_km:
                cluster.append(i)
                remaining.remove(i)
        clusters.append(cluster)
    return clusters

def order_cluster_greedy(points: List[Dict[str, Any]], idxs: List[int], start_from: Tuple[float, float] | None = None) -> List[int]:
    if not idxs:
        return []
    if start_from is None:
        current = idxs[0]
    else:
        best_idx, best_dist = None, float("inf")
        for i in idxs:
            d = haversine_km(start_from[0], start_from[1], points[i]["lat"], points[i]["lng"])
            if d < best_dist:
                best_idx, best_dist = i, d
        current = best_idx
    visited = {current}
    ordered = [current]
    while len(visited) < len(idxs):
        nxt = nearest_unvisited(current, points, visited)
        visited.add(nxt)
        ordered.append(nxt)
        current = nxt
    return ordered

def estimate_leg_minutes(a: Dict[str, Any], b: Dict[str, Any], mode: str = "walk") -> int:
    km = haversine_km(a["lat"], a["lng"], b["lat"], b["lng"])
    speed_kmh = 4.5 if mode == "walk" else 18 if mode == "transit" else 35 if mode == "drive" else 4.5
    minutes = int((km / speed_kmh) * 60) + 5
    return max(5, minutes)

def make_days_schedule(points: List[Dict[str, Any]], clusters: List[List[int]],
                       start_time_str: str, end_time_str: str, transport_mode: str = "walk"):
    day_plans = []
    day_idx = 1
    start_time = datetime.strptime(start_time_str, "%H:%M")
    end_time = datetime.strptime(end_time_str, "%H:%M")
    window_minutes = int((end_time - start_time).total_seconds() / 60)

    for cluster in clusters:
        max_d = 0.0
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                a, b = points[cluster[i]], points[cluster[j]]
                max_d = max(max_d, haversine_km(a["lat"], a["lng"], b["lat"], b["lng"]))

        ordered = cluster
        idx_ptr = 0
        while idx_ptr < len(ordered):
            minutes_used = 0
            items = []
            current_time = start_time

            first = points[ordered[idx_ptr]]
            items.append({
                "title": first["title"], "lat": first["lat"], "lng": first["lng"],
                "duration_min": first.get("duration_min", 60),
                "start": current_time.strftime("%H:%M"),
                "end": (current_time + timedelta(minutes=first.get("duration_min", 60))).strftime("%H:%M"),
                "travel_min": 0, "distance_km": 0.0
            })
            minutes_used += first.get("duration_min", 60)
            current_time += timedelta(minutes=first.get("duration_min", 60))
            idx_ptr += 1

            while idx_ptr < len(ordered):
                prev = points[ordered[idx_ptr - 1]]
                nxt = points[ordered[idx_ptr]]
                travel = estimate_leg_minutes(prev, nxt, transport_mode)
                dur = nxt.get("duration_min", 60)
                if minutes_used + travel + dur > window_minutes:
                    break
                km = haversine_km(prev["lat"], prev["lng"], nxt["lat"], nxt["lng"])
                current_time += timedelta(minutes=travel)
                start_str = current_time.strftime("%H:%M")
                end_str = (current_time + timedelta(minutes=dur)).strftime("%H:%M")

                items.append({
                    "title": nxt["title"], "lat": nxt["lat"], "lng": nxt["lng"],
                    "duration_min": dur, "start": start_str, "end": end_str,
                    "travel_min": travel, "distance_km": round(km, 2)
                })
                minutes_used += travel + dur
                current_time += timedelta(minutes=dur)
                idx_ptr += 1

            day_plans.append({
                "day": day_idx,
                "summary": {"within_km": round(max_d, 2), "stops": len(items)},
                "items": items
            })
            day_idx += 1

    return day_plans

def cluster_itinerary(pois: List[Dict[str, Any]], hotel: Dict[str, Any] | None = None,
                      radius_km: float = 1.2, start_time: str = "09:00", end_time: str = "19:00",
                      transport_mode: str = "walk"):
    clusters = cluster_by_radius(pois, radius_km)
    ordered_clusters = []
    for c in clusters:
        ordered = order_cluster_greedy(pois, c, (hotel["lat"], hotel["lng"]) if hotel else None)
        ordered_clusters.append(ordered)
    return make_days_schedule(pois, ordered_clusters, start_time, end_time, transport_mode)
