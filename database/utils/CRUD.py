from typing import Any

from peewee import ModelSelect

from database.common.models import db, ModelBase


def _store_data(dbase: db, model: Any, *data: list[dict]) -> None:
    with dbase.atomic():
        model.insert_many(*data).execute()


def _retrieve_all_data(dbase: db, model: "", *columns: ModelBase) -> ModelSelect:
    with dbase.atomic():
        respond = model.select(*columns)

    return respond


class CRUDInterface:
    @classmethod
    def store(cls):
        return _store_data

    @classmethod
    def retrieve(cls):
        return _retrieve_all_data
