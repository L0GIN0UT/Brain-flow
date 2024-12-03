import pathlib
from pydantic_settings import BaseSettings


class Base(BaseSettings):
    # Rethink section
    rethinkdb_db: str
    rethinkdb_table: str
    rethinkdb_host: str
    rethinkdb_port: int
    border_time: int

    # API section
    project_name: str

    #  DB Postgres section

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    five_minute_sample: int

    use_impedance: bool
    data_file_name: str

    max_samples: int

    log_level: str

    mne_parameter: bool

    admin_email: str
    admin_password: str

    class Config:
        env_file = f"{pathlib.Path(__file__).resolve().parent.parent}/.env"
        env_file_encoding = 'utf-8'


settings = Base()
