import sys

import backoff
from rethinkdb import r, errors as re

from config.settings import settings


def giveup():
    sys.exit(-1)


@backoff.on_exception(backoff.expo, (re.ReqlDriverError, re.ReqlOpFailedError), max_time=60, on_giveup=giveup)
def change_feed() -> dict:
    conn = r.connect(settings.rethinkdb_host, settings.rethinkdb_port)
    cursor = r.db('RTDB_desync').table('dev_desync').pluck('device', 'status',
                                                           'calibration', 'time_calibration',
                                                           "desync_data_uuid").changes()['new_val'].run(conn)
    for document in cursor:
        return document
