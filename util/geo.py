import math

def haversine_dist(p1, p2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2  = map(math.radians, [p1[0], p1[1], p2[0], p2[1]])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km

def euclidian_dist(p1, p2):
    return math.sqrt(sum((a-b)**2 for a,b in zip(p1, p2)))

def latlong_to_3d(loc):
    radius = 6367
    lat, lon = math.radians(loc[0]), math.radians(loc[1])
    return (
        radius*math.cos(lon)*math.cos(lat),
        radius*math.sin(lon)*math.cos(lat),
        radius*math.sin(lat)
    )

def latlong_from_3d(loc):
    lat = math.atan2(loc[2], math.sqrt(loc[0]**2 + loc[1]**2))
    lon = math.atan2(loc[1], loc[0])
    return math.degrees(lat), math.degrees(lon)

def mean_latlong(*locs):
    locs_3d = [latlong_to_3d(loc) for loc in locs]
    center = [
        sum(loc_3d[i] for loc_3d in locs_3d) / len(locs_3d)
        for i in range(3)
    ]
    return latlong_from_3d(center)
