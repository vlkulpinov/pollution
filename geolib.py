__author__ = 'vlkulpinov'

import math

TILE_SIZE = 256

def num2deg(xtile, ytile, zoom):
    """ Get coordinates of NW point in tile
    :param xtile: x-coord
    :param ytile: y-coord
    :param zoom: zoom coefficient
    :return: pair lat, lon
    """

    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)


def get_pixel_coord(xtile, ytile, zoom, h, w):
    """ Get coordinates of (h, w) point in tile
    :param xtile: x-coord of tile
    :param ytile: y-coord of tile
    :param zoom: zoom coefficient
    :param h: pixel height
    :param w: pixel width
    :return: pair lat, lon
    """

    return num2deg(xtile + (h + 0.5) / TILE_SIZE,
                   ytile + (w + 0.5) / TILE_SIZE, zoom)


def points2distance(p1,  p2):
    """ Get geo distance between two points
    :param p1: pair lon, lat
    :param p2: pair lon, lat
    :return: distance in metres
    """
    if p1 == p2:
        return 0.0

    a = 6378137
    e2 = 2.0 / 298.257223563
    degree_coef = math.pi / 180.0

    lambda_rad = (p1[1] - p2[1]) * degree_coef
    phi_rad = (p1[0] - p2[0]) * degree_coef
    phi_mean = (p1[0] + p2[0]) / 2.0 * degree_coef

    rho = (a * (1.0 - e2)) / (1.0 - e2 * (math.sin(phi_mean) ** 2)) ** 1.5
    nu = a / math.sqrt(1.0 - e2 * (math.sin(phi_mean) ** 2))

    fz = math.sqrt(math.sin(phi_rad / 2.0) ** 2
        + math.cos(p2[0] * degree_coef) * math.cos(p1[0] * degree_coef)
        * math.sin(lambda_rad / 2.0) ** 2)
    fz = 2.0 * math.asin(fz)

    fAlpha = math.cos(p2[0] * degree_coef) * math.sin(lambda_rad) / math.sin(fz)
    fAlpha = math.asin(fAlpha)

    fR = (rho * nu) / ((rho * math.sin(fAlpha) ** 2) + (nu * math.cos(fAlpha) ** 2))

    return fz * fR


#print points2distance((55.75439938, 37.62102012), (55.74396411, 37.63490473))
#print num2deg(1234 + 1/256, 642 + 1.0/256, 11)