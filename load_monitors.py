__author__ = 'vlkulpinov'

import json
import logging
import sqlite3
from table_parser import parse_table

from collections import namedtuple

from datetime import datetime

logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)
eco_monitoring = json.load(open('monitoring_coordinates.json', 'r'))


def load_mosecom(url, factors, db, monitoring_id):
    """
    Load url with daily monitoring from mosecom.ru site
    Return None for factors not founded
    :param url: url for daily table
    :param factors: list with factors to load
    :return: None
    """
    table = parse_table(url)
    if table is None:
        logging.error('Cannot load table from %s' % url)
        return None
    elif len(table) == 0:
        logging.error('Table is empty %s' % url)
        return None

    for f in factors:
        index_factor = None
        if f == 'co':
            for i in range(len(table[0])):
                if 'co' in table[0][i].lower():
                    index_factor = i
                    break

            if index_factor is None:
                logging.error('Factor %s not found in %s' % (f, url))

            records = []
            last_date = None
            for i in range(2, len(table)):
                date_time_str = table[i][0]
                try:
                    score_str = float(table[i][index_factor])
                except:
                    score_str = None

                if len(date_time_str.split(' ')) == 2:
                    last_date = date_time_str.split(' ')[0]
                    cur_time = date_time_str.split(' ')[1]
                else:
                    cur_time = date_time_str

                records.append((datetime.strptime(last_date + ' ' + cur_time,
                                                 '%d.%m.%Y %H:%M'),
                                monitoring_id,
                                score_str))

            c = db.cursor()
            c.executemany('''insert or replace into monitor_data_co
            (dump_ts, monitor_id, dump_value) values (?, ?, ?)''', records)
            db.commit()
        else:
            logging.error('Unrecognized factor %s' % f)


def load_monitors():
    db = sqlite3.connect('eco.db')

    c = db.cursor()

    for obj in c.execute('''select id, url, url_type, is_co from monitor'''):
        use_factors = []
        if obj[3] == 1:
            use_factors.append('co')

        if obj[2] == 'mosecom':
            load_mosecom(obj[1], use_factors, db, obj[0])
        else:
            logging.error('Unrecognized url_type %s' % obj[2])

    db.close()

load_monitors()