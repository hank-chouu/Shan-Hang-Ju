from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

## users

class User(UserMixin):
    pass

## database

db = SQLAlchemy()

class Rooms(db.Model):
    __tablename__ = 'rooms'
    date = db.Column(db.String(15), primary_key = True)
    room_301 = db.Column(db.Integer, nullable = False)
    room_302 = db.Column(db.Integer, nullable = False)
    room_303 = db.Column(db.Integer, nullable = False)
    room_501 = db.Column(db.Integer, nullable = False)
    room_502 = db.Column(db.Integer, nullable = False)

    def __init__(self, date, room_301, room_302, room_303, room_501, room_502):
        self.date = date
        self.room_301 = room_301
        self.room_302 = room_302
        self.room_303 = room_303
        self.room_501 = room_501
        self.room_502 = room_502