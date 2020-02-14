# Haversine formula (optimized)
# https://stackoverflow.com/questions/41336756/find-the-closest-latitude-and-longitude
# https://en.wikipedia.org/wiki/Haversine_formula

from math import cos, asin, sqrt

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))

def closest(geoloc, p):
    return min(geoloc.keys(), key=lambda ip: distance(p['lat'],p['lon'],geoloc[ip]['lat'],geoloc[ip]['lon']))