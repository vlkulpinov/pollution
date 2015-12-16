__author__ = 'vlkulpinov'

import geolib
from PIL import Image
import json
import os
import sqlite3

import numpy as np

import logging

STANDARD_ALPHA = 255
PATH_TILES = 'tiles'

logging.basicConfig(format = u'%(filename)s# %(levelname)-8s [%(asctime)s]  %(message)s', level=logging.DEBUG)
#eco_monitoring = json.load(open('monitoring_coordinates.json', 'r'))


def convert_color(pollution):
    # logging.debug(pollution)

    red = 30 + (pollution - 0.18) / (0.32 - 0.18) * 225
    green = 225 - (pollution - 0.18) / (0.32 - 0.18) * 225

    # if pollution >= 0.27:
    #     logging.debug(pollution)

    if 0.18 <= pollution <= 0.32:
        return (int(red), int(green), 0, STANDARD_ALPHA)
    return (255, 0, 0, STANDARD_ALPHA)


def save_tile(img, x, y, z):
    cur_dir = '%s/%s' % (PATH_TILES, z)
    if not os.path.exists(cur_dir):
        os.makedirs(cur_dir)

    cur_dir = '%s/%s' % (cur_dir, x)
    if not os.path.exists(cur_dir):
        os.makedirs(cur_dir)

    cur_dir = '%s/%s.png' % (cur_dir, y)
    img.save(cur_dir)
    return cur_dir


def get_color_intensity(dist):
    return int(255 * (dist / 300))


def get_path_tile(x, y, z):
    return '%s/%s/%s/%s.png' % (PATH_TILES, x, y, z)


def get_point_color(p, monitor_data):
    pollution = 0
    sum_dist = 0

    for monitor_record in monitor_data:
        cur_dist = geolib.points2distance(monitor_record['point'], p)
        sum_dist += cur_dist

    coef_sum = 0
    for monitor_record in monitor_data:
        cur_dist = geolib.points2distance(monitor_record['point'], p)
        # if cur_dist <= 1000:
        #    logging.info(np.exp(-(cur_dist / sum_dist) * 10))
        # logging.info(p)
        # logging.info(cur_dist)
        pollution += monitor_record['value'] * np.exp(-(cur_dist / sum_dist) * 10)
        coef_sum += np.exp(-(cur_dist / sum_dist) * 10)

    # logging.info(coef_sum)
    pollution /= coef_sum

    return convert_color(pollution)


def render_tile(x, y, z, monitor_data):

    logging.info('%s %s %s' % (x, y, z))
    img = Image.new('RGBA', (geolib.TILE_SIZE, geolib.TILE_SIZE))
    for h in range(0, img.size[0], 4):
        for w in range(0, img.size[1], 4):
            color = get_point_color(geolib.get_pixel_coord(x, y, z, h, w), monitor_data)
            for dh in range(4):
                for dw in range(4):
                    img.load()[h + dh, w + dw] = color

    return save_tile(img, x, y, z)


def load_renderer(render_param_file):
    with open(render_param_file, 'r') as f:
        config = json.load(f)

    db = sqlite3.connect('eco.db')
    c = db.cursor()

    monitor_data = []
    for i in c.execute(
            """select monitor_geo.lat, monitor_geo.lon, monitor_data_co.dump_value
            from monitor
            join monitor_geo on monitor.id=monitor_geo.monitor_id
            join monitor_data_co on monitor.id=monitor_data_co.monitor_id
            where monitor_data_co.dump_value is not null
            group by monitor.id
            having max(monitor_data_co.dump_ts)"""
            ):
        monitor_data.append({'point': (i[0], i[1]), 'value': i[2]})

    print monitor_data

    import time
    for layer in config['layers']:
        start_time = time.time()
        for x in range(layer['min_x'], layer['max_x']):
            for y in range(layer['min_y'], layer['max_y']):
                render_tile(x, y, layer['scale'], monitor_data)
        logging.info('End render %s with %s s' % (layer['scale'], str(time.time() - start_time)))

if __name__ == '__main__':
    load_renderer('cfg/render.json')


#for x in range(1236, 1241):
#    for y in range(639, 643):
#        render_tile(x, y, 11)

#for x in range(2471, 2480):
#    for y in range(1276, 1284):
#        render_tile(x, y, 12)
