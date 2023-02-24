import logging
import os
import pytz
from datetime import datetime
from flask import abort
import traceback
import sys

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



def abort_msg(e):
    """500 bad request for exception

    Returns:
        500 and msg which caused problems
    """
    error_class = e.__class__.__name__ # 引發錯誤的 class
    detail = e.args[0] # 得到詳細的訊息
    cl, exc, tb = sys.exc_info() # 得到錯誤的完整資訊 Call Stack
    lastCallStack = traceback.extract_tb(tb)[-1] # 取得最後一行的錯誤訊息
    fileName = lastCallStack[0] # 錯誤的檔案位置名稱
    lineNum = lastCallStack[1] # 錯誤行數 
    funcName = lastCallStack[2] # function 名稱
    # generate the error message
    errMsg = "Exception raise in file: {}, line {}, in {}: [{}] {}. Please contact the member who is the person in charge of project!".format(fileName, lineNum, funcName, error_class, detail)
    # return 500 code
    abort(500, errMsg)

logger()