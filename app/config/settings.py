import pathlib
from pydantic import BaseSettings


class Base(BaseSettings):

    # Rethink section
    rethinkdb_db: str = 'RTDB_desync'
    rethinkdb_table: str = 'dev_desync'
    rethinkdb_host: str = 'rethink_db'
    rethinkdb_port: int = 28015
    border_time: int = 1000

    # API section
    project_name: str

    #  DB Postgres section

    # pg_database_url: str = ''
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    algorithm: str = "HS256"
    secret_key: str = "2abb483d487c3b4f1ba39a4ae56ac318050417e89e7c1ceb903f8d2c362f5d51"

    access_token_expire_minutes: int = 30

    admin_email: str

    mail_address: str
    mail_password: str
    mail_smtp_server: str
    mail_port: int
    mail_message_subject: str
    mail_message_text: str

    log_level: str

    redis_host: str
    redis_port: int
    redis_db: int
    redis_cache_expire: int

    class Config:

        env_file = f"{pathlib.Path(__file__).resolve().parent.parent.parent}/.env"
        env_file_encoding = 'utf-8'


settings = Base()
