from database.common.models import db, ModelBase
from database.utils.CRUD import CRUDInterface

db.connect()


def create_models():
    db.create_tables(ModelBase.__subclasses__(), safe=True)


crud = CRUDInterface()


create_models()
