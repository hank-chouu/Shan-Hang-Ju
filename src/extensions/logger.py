import logging
import os
import pytz
from datetime import datetime

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