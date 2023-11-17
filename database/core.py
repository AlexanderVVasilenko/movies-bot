from database.common.models import db, BaseModel
from database.utils.CRUD import CRUDInterface

db.connect()


def create_models():
    db.create_tables(BaseModel.__subclasses__(), safe=True)


crud = CRUDInterface()


create_models()
