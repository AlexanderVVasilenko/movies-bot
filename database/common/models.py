from datetime import datetime

import peewee as pw

db = pw.SqliteDatabase("movies.db")


class ModelBase(pw.Model):
    created_at = pw.DateField(default=datetime.now())

    class Meta:
        database = db


class User(ModelBase):
    user_id = pw.IntegerField(primary_key=True)
    username = pw.CharField()
    first_name = pw.CharField()
    last_name = pw.CharField(null=True)


class History(ModelBase):
    movie = pw.TextField()
    user = pw.ForeignKeyField(User, backref="history")
    date = pw.DateField()






