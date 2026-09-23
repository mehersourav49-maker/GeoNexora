def classify(score: float):
    return "Critical" if score >= .8 else "High" if score >= .6 else "Moderate" if score >= .35 else "Low"

def polygon_from_center(lat: float, lon: float, d: float = .025):
    return [[lon-d,lat-d],[lon+d,lat-d],[lon+d,lat+d],[lon-d,lat+d],[lon-d,lat-d]]
