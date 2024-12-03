import sys
import hashlib
import string
import random
from http import HTTPStatus
from http.client import HTTPException
from uuid import uuid4
from datetime import datetime
import pytz

from deprecated import deprecated
import numpy as np
from pylsl import StreamInlet
from rethinkdb import r, errors as re
import backoff

from sqlalchemy.orm import sessionmaker, make_transient
from sqlalchemy import create_engine, exc, inspect
from sqlalchemy.future import select
from sqlalchemy_utils import database_exists, create_database

from config.settings import settings
from config.logs_config import logger_load_data
from database_etl.models import Base, Device, Clinic, User, ClinicAddress
from datetime import datetime


class RethinkDB:
    """
    Класс для работы с базой данных реального времени RethinkDB
    """
    HOST = settings.rethinkdb_host
    PORT = settings.rethinkdb_port
    DB = settings.rethinkdb_db
    TABLE = settings.rethinkdb_table

    @staticmethod
    def giveup():
        sys.exit(-1)

    @staticmethod
    @backoff.on_exception(backoff.expo, re.ReqlDriverError, max_time=60, on_giveup=giveup,
                          logger=logger_load_data)
    def rethink_connect_to_db(host=HOST, port=PORT):
        """
        Создать подключение к RethinkDB
        :param host:
        :param port:
        :return: conn
        """
        logger_load_data.info('Try connect to rethinkdb...')
        conn = r.connect(host, port)
        logger_load_data.info('Success connect to rethinkdb')
        return conn

    @staticmethod
    def rethink_create_db(conn, db=DB):
        """
        Создать базу данных в RethinkDB
        :param conn:
        :param db: str
        """
        try:
            r.db_create(db).run(conn)
        except re.ReqlError as e:
            logger_load_data.error("DataBase create error: " + e.message)

    @staticmethod
    def rethink_create_table(db=DB, table=TABLE):
        """
        Создать таблицу в RethinkDB
        :param db: str
        :param table: str
        """
        with RethinkDB.rethink_connect_to_db() as conn:
            if db not in r.db_list().run(conn):
                RethinkDB.rethink_create_db(conn)

            if table not in r.db(db).table_list().run(conn):
                try:
                    r.db(db).table_create(table).run(conn)
                except re.ReqlError as e:
                    logger_load_data.error(f"Create table - {table} error: " + e.message)

    @staticmethod
    def rethink_delete_table(db=DB, table=TABLE):
        """
        Удалить таблицу в RethinkDB
        :param db: str
        :param table: str
        """
        with RethinkDB.rethink_connect_to_db() as conn:
            r.db(db).table(table).delete().run(conn)

    @staticmethod
    def rethink_from_postgresql(devices: list, db=DB, table=TABLE):
        """
        Перенести устройства из PostgreSQL в RethinkDB
        :param devices: list
        :param db: str
        :param table: str
        """
        RethinkDB.rethink_delete_table()
        with RethinkDB.rethink_connect_to_db() as conn:
            # if not devices:
            #     return
            for device in devices:
                r.db(db).table(table).insert({"device": device.name, "device_uuid": str(device.uuid),
                                              "research_status": {}, "calibration": False, "time_calibration": 10.0,
                                              "baseline": {}, "channel_desync": {}, "impedance": {},
                                              "desync_data_uuid": {}, "status": False, "patient_code": {},
                                              "date_start": {}, "duration": {}}).run(conn)

    @staticmethod
    @deprecated("Insert data. Old method, now use 'rethink_from_postgresql'")
    def rethink_insert_data(inlet_data: StreamInlet, table=TABLE, db=DB):
        try:
            with RethinkDB.rethink_connect_to_db() as conn:
                lst = list(r.db(db).table(table).filter(r.row["device"] == inlet_data.info().name()).run(conn))
                if len(lst) == 0:
                    r.db(db).table(table).insert({"device": inlet_data.info().name(), "patient": None, "status": 1,
                                                  "channel_desync": {}}).run(conn)
        except re.ReqlError as e:
            logger_load_data.error("Inserting initialization data error: " + e.message)

    @staticmethod
    def rethink_update_baseline(inlet_data: StreamInlet, baseline: dict, table=TABLE, db=DB):
        """
        Обновление baseline в RethinkDB
        :param inlet_data: StreamInlet
        :param baseline: dict
        :param table: str
        :param db: str
        """
        try:
            with RethinkDB.rethink_connect_to_db() as conn:
                r.db(db).table(table).filter(r.row["device"] ==
                                             inlet_data.info().name()).update({"baseline": baseline}).run(conn)
        except re.ReqlError as e:
            logger_load_data.error("Updating data error: " + e.message)

    @staticmethod
    def rethink_calibration_false(device: str, table=TABLE, db=DB):
        """
        Изменение calibration в RethinkDB
        :param device: str
        :param table: str
        :param db: str
        """
        try:
            with RethinkDB.rethink_connect_to_db() as conn:
                r.db(db).table(table).filter({"device": str(device)}).update({"calibration": bool(False)}).run(conn)
        except re.ReqlError as e:
            logger_load_data.error("Updating data error: " + e.message)

    @staticmethod
    def rethink_status_false(device: str, table=TABLE, db=DB):
        """
        Изменение status в RethinkDB
        :param device: str
        :param table: str
        :param db: str
        """
        try:
            with RethinkDB.rethink_connect_to_db() as conn:
                r.db(db).table(table).filter({"device": str(device)}).update({"status": bool(False)}).run(conn)
        except re.ReqlError as e:
            logger_load_data.error("Updating data error: " + e.message)

    @staticmethod
    def rethink_update_data(inlet_data: StreamInlet, corr: dict, impedance: dict, table=TABLE, db=DB):
        """
        Обновление данных в RethinkDB
        :param inlet_data: StreamInlet
        :param corr: dict
        :param impedance: dict
        :param table: str
        :param db: str
        """
        # Замена NaN значений на 0
        for key, cor in corr.items():
            if np.isnan(cor):
                corr[key] = 0
        try:
            with RethinkDB.rethink_connect_to_db() as conn:
                r.db(db).table(table).filter(r.row["device"] ==
                                             inlet_data.info().name()).update({"channel_desync": corr}).run(conn)
                r.db(db).table(table).filter(r.row["device"] ==
                                             inlet_data.info().name()).update({"impedance": impedance}).run(conn)
        except re.ReqlError as e:
            logger_load_data.error("Updating data error: " + e.message)

    @staticmethod
    def rethink_update_impedance(desync_data_uuid: str, impedance: dict, table=TABLE, db=DB):
        """
        Обновление импеданса в RethinkDB
        :param desync_data_uuid: str
        :param impedance: dict
        :param table: str
        :param db: str
        """
        try:
            with RethinkDB.rethink_connect_to_db() as conn:
                r.db(db).table(table).filter(r.row["desync_data_uuid"] ==
                                             str(desync_data_uuid)).update({"impedance": impedance}).run(conn)
        except re.ReqlError as e:
            logger_load_data.error("Updating data error: " + e.message)

    @staticmethod
    def rethink_status_state(device: str, research_status: str, table=TABLE, db=DB):
        """
        Изменение status в RethinkDB
        :param device: str
        :param table: str = dev_desync
        :param db: str
        :param research_status: str
        """
        try:
            with RethinkDB.rethink_connect_to_db() as conn:
                r.db(db).table(table).filter({"device": str(device)}).update({"research_status": research_status}).run(conn)
        except re.ReqlError as e:
            logger_load_data.error("Updating research_status error: " + e.message)


class PostgresqlDB:
    """
    Класс для работы с базой данных PostgreSQL
    """
    HOST = settings.postgres_host
    PORT = settings.postgres_port
    DB = settings.postgres_db
    USER = settings.postgres_user
    Password = settings.postgres_password
    URL = f'postgresql://{USER}:{Password}@{HOST}:{PORT}/{DB}'
    tz = pytz.timezone('Europe/Samara')

    engine = create_engine(URL, echo=True, future=True)

    @staticmethod
    def giveup():
        sys.exit(-1)

    @staticmethod
    def init_models(engine=engine):
        """
        Инициализация бд в PostgreSQL
        :param engine: str
        """
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(engine)

    @staticmethod
    def get_session(engine=engine):
        """
        Получение сессии в PostgreSQL
        :param engine: str
        """
        session = sessionmaker(bind=engine)()
        return session

    @staticmethod
    def create_desync_data():
        pass

    @staticmethod
    def update_desync_data(uuid: str, desync_average: dict, model, session=get_session()):
        """
        Обновление десинхронизации в PostgreSQL
        :param uuid: str
        :param desync_average: dic
        :param model: DesyncDatas
        :param session: str
        """
        try:
            result = session.get(model, uuid)
            if result:
                result_dict = result.data
                new_write = {str(datetime.now()): desync_average}
                result_dict = {**result_dict, **new_write}
                result.data = result_dict
                PostgresqlDB.add_note(result, session)
        except exc.SQLAlchemyError as e:
            logger_load_data.error(f'Updating data error: {e.message}')
        finally:
            session.close()

    @staticmethod
    @deprecated
    def insert_data(uuid: str, desync_average: dict, model, session=get_session()):
        """
        Запись десинхронизации в PostgreSQL
        :param uuid: str
        :param desync_average: dic
        :param model: DesyncDatas
        :param session: str
        """
        try:
            result = session.get(model, uuid)
            if result:
                # session.expunge(result) # expunge the object from session
                make_transient(result)  # sqlalchemy.orm.session.make_transient

                result.data = desync_average
                result.date = datetime.now(tz=PostgresqlDB.tz)
                result.uuid = uuid4()

                session.add(result)
                session.commit()
                session.refresh(result)
        except exc.SQLAlchemyError as e:
            logger_load_data.error(f'Updating data error: {e.message}')
        finally:
            session.close()

    @staticmethod
    def add_note(note, session):
        """
        Добавление данных и обновление в PostgreSQL
        :param note: model
        :param session: str
        """
        session.add(note)
        session.commit()
        session.refresh(note)
        session.close()

    @staticmethod
    def get_list_device(device=Device, session=get_session()):
        """
        Получение списка устройств из PostgreSQL
        :param device: Device
        :param session: str
        :return: list
        """
        try:
            result = session.execute(select(device))
            model_list = result.scalars().all()
            return model_list
        except exc.SQLAlchemyError as e:
            logger_load_data.error(f'Updating data error: {e.message}')
            return None
        finally:
            session.close()

    @staticmethod
    def get_random_string(length=12):
        """ Генерирует случайную строку, использующуюся как соль """
        return "".join(random.choice(string.ascii_letters) for _ in range(length))

    @staticmethod
    def hash_password(password: str, salt: str = None):
        """ Хеширует пароль с солью """
        if salt is None:
            salt = PostgresqlDB.get_random_string()
        enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
        return enc.hex()

    @staticmethod
    def check_and_add_clinic_and_user():
        logger_load_data.info('Checking and adding clinic and user if necessary.')

        try:
            session = PostgresqlDB.get_session()

            # Begin transaction
            with session.begin():
                clinic = session.query(Clinic).first()
                if not clinic:
                    new_clinic = Clinic(name="")
                    session.add(new_clinic)
                    session.flush()
                    clinic_uuid = new_clinic.uuid
                    logger_load_data.info('Clinic record added.')
                else:
                    clinic_uuid = clinic.uuid

                clinic_address = session.query(ClinicAddress).first()
                if not clinic_address:
                    new_clinic_address = ClinicAddress(region="", city="", street="", clinic_uuid=clinic_uuid)
                    session.add(new_clinic_address)
                    session.flush()
                    logger_load_data.info('Clinic record added.')

                existing_user = session.query(User).filter_by(email=settings.admin_email).first()
                if existing_user:
                    logger_load_data.info('User already exists. No action taken.')
                else:
                    salt = PostgresqlDB.get_random_string()
                    hashed_password = PostgresqlDB.hash_password(settings.admin_password, salt)
                    new_user = User(password=f"{salt}${hashed_password}", email=settings.admin_email,
                                    clinic_uuid=clinic_uuid)
                    session.add(new_user)
                    logger_load_data.info('User record added.')

            session.commit()

        except Exception as e:
            logger_load_data.error(f'Error in check_and_add_clinic_and_user: {str(e)}')
            session.rollback()
        finally:
            session.close()
