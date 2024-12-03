import orjson
from pydantic import BaseModel


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class BaseConfig(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_alias = True
