from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

## users

class User(UserMixin):
    pass

## database

db = SQLAlchemy()

class Rooms(db.Model):
    __tablename__ = 'rooms'
    date = db.Column(db.DateTime, primary_key = True)
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

class Booking(db.Model):
    
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key = True)

    name = db.Column(db.String(20), nullable = False)
    gender = db.Column(db.String(10), nullable = False)
    phone = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(50), nullable = False)

    room_num = db.Column(db.String(10), nullable = False)
    check_in = db.Column(db.DateTime, nullable = False)
    check_out = db.Column(db.DateTime, nullable = False)
    add_bed = db.Column(db.Integer, nullable = False)
    arrival = db.Column(db.String(10), nullable = False)
    parking = db.Column(db.Integer, nullable = False)
    breakfast = db.Column(db.Integer, nullable = False)
    special_needs = db.Column(db.String(200), nullable = True)
    created_on = db.Column(db.DateTime, nullable = False)

    total = db.Column(db.Integer, nullable = False)
    deposit = db.Column(db.Integer, nullable = False)
    final = db.Column(db.Integer, nullable = False)

    deposit_paid = db.Column(db.Integer, nullable = False)
    final_paid = db.Column(db.Integer, nullable = False)

    deleted = db.Column(db.Integer, nullable = False)

    def __init__(self, id, client_info, booking_info, amounts):

        self.id = id
        # client info
        self.name = client_info[0]
        self.gender = client_info[1]
        self.phone = client_info[2]
        self.email = client_info[3]
        # booking info
        self.room_num = booking_info[0]
        self.check_in = booking_info[1]
        self.check_out = booking_info[2]
        self.add_bed = booking_info[3]
        self.arrival = booking_info[4]
        self.parking = booking_info[5]
        self.breakfast = booking_info[6]
        self.special_needs = booking_info[7]
        self.created_on = booking_info[8]
        # payment info
        self.total = amounts[0]
        self.deposit = amounts[1]
        self.final = amounts[2]
        self.deposit_paid, self.final_paid, self.deleted = 0, 0, 0

class Admin(db.Model):

    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key = True)
    invite_code = db.Column(db.String(20), nullable = False)
    username = db.Column(db.String(20), nullable = False)
    pw = db.Column(db.String(70), nullable = False)




