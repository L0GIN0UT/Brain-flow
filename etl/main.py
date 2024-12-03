from multiprocessing import Event

from load_data.load_data import RethinkDB, PostgresqlDB
from control_proc.processes_control import ControlProcesses

if __name__ == '__main__':
    process_list = []

    PostgresqlDB.init_models()
    RethinkDB.rethink_create_table()

    # Добавление клиники и пользователя в базу данных, если это необходимо
    PostgresqlDB.check_and_add_clinic_and_user()

    # из PG добавлять в rethink
    devices = PostgresqlDB.get_list_device()
    if devices:
        RethinkDB.rethink_from_postgresql(devices)
    control_proc = ControlProcesses()
    control_proc.start_stop_process()
