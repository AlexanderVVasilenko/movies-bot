from vedis import Vedis

from tg_API.utils import config
from errors import SetStateError

db_file = "database.vdb"


def get_current_state(user_id):
    with Vedis(db_file) as db:
        try:
            return db[user_id].decode()
        except KeyError:
            return config.States.S_START.value


def set_state(user_id, value):
    with Vedis(db_file) as db:
        try:
            db[user_id] = value
            return True
        except Exception as e:
            current_state = get_current_state(user_id)
            raise SetStateError(user_id, value, current_state) from e
