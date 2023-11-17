from typing import Any
from peewee import Model, ModelSelect

from database.common.models import db, BaseModel


def store_data(dbase: db, model: Any, *data: list[dict]) -> None:
    with dbase.atomic():
        model.insert_many(*data).execute()


def retrieve_all_data(dbase: db, model: Model, *columns: BaseModel) -> ModelSelect:
    with dbase.atomic():
        respond = model.select(*columns)
    return respond


class CRUDInterface:
    @staticmethod
    def store():
        return store_data

    @staticmethod
    def retrieve():
        return retrieve_all_data
