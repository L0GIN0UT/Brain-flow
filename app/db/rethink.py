from rethinkdb import r

from config.settings import settings


host = settings.rethinkdb_host
port = settings.rethinkdb_port
db_name = settings.rethinkdb_db
table = settings.rethinkdb_table

# r.set_loop_type('twуisted')


def get_rethink_session() -> r:
    conn = r.connect(host, port)
    return conn
