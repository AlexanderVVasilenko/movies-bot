from database.common.models import db, BaseModel
from database.utils.CRUD import CRUDInterface

db.connect()

crud = CRUDInterface()

db.create_tables(BaseModel.__subclasses__(), safe=True)
