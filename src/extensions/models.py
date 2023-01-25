from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import logging
import os
import pytz
from datetime import datetime

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


## logger

class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""

    def converter(self, timestamp):
        # Create datetime in UTC
        dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        # Change datetime's timezone
        return dt.astimezone(pytz.timezone('Asia/Taipei'))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s


def logger():
    #1.setup log path and create log directory
    logName = 'Program.log'
    logDir = 'log'
    logPath = logDir + '/' + logName

    #create log directory 
    os.makedirs(logDir,exist_ok=True)

    #2.create logger, then setLevel
    global allLogger
    allLogger = logging.getLogger('allLogger')
    allLogger.setLevel(logging.DEBUG)

    #3.create file handler, then setLevel
    #create file handler
    fileHandler = logging.FileHandler(logPath,mode='w')
    fileHandler.setLevel(logging.INFO)

    #4.create stram handler, then setLevel
    #create stream handler
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.INFO)

    #5.create formatter, then handler setFormatter
    AllFormatter = Formatter("%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s", '%Y-%m-%d %H:%M:%S')
    fileHandler.setFormatter(AllFormatter)
    streamHandler.setFormatter(AllFormatter)

    #6.logger addHandler
    allLogger.addHandler(fileHandler)
    allLogger.addHandler(streamHandler)

logger()