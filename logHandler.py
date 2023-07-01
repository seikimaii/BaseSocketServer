import logging
from logging.handlers import TimedRotatingFileHandler
import time
from datetime import datetime
import os

def MyLogNamer(defaultName):
    '''If interval set, must set namer to trigger'''
    base_filename, ext, date = defaultName.split(".")
    return f"{base_filename}_{date}.{ext}"

class MyTimedRotatingFileHandler(TimedRotatingFileHandler):

    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        super().__init__(filename, when=when, interval=interval, backupCount=backupCount, encoding=encoding, delay=delay, utc=utc)
    
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        currentTime = self.rolloverAt - self.interval
        # dstNow = time.localtime(currentTime)[-1]
        if self.utc:
            timeTuple = datetime.utcfromtimestamp(currentTime)
            # timeTuple = time.gmtime(currentTime)
        else:
            timeTuple = datetime.fromtimestamp(currentTime)
            # timeTuple = time.localtime(currentTime)
            # dstNow = timeTuple[-1]
        pastName = f'{self.baseFilename.split(".")[0]}_{datetime.strftime(timeTuple, self.suffix)}.{self.baseFilename.split(".")[1]}'
        dfn = self.rotation_filename(pastName)
        # dfn = self.rotation_filename(self.baseFilename + "." + time.strftime(self.suffix, timeTuple))
        if os.path.exists(dfn):
            with open(dfn, 'a') as dest:
                with open(self.baseFilename, 'r') as src:
                    dest.write(src.read())
            os.remove(self.baseFilename)
        else:
            os.rename(self.baseFilename, dfn)

class TextBrowserHandler(logging.Handler):
    def __init__(self, text_browser):
        super().__init__()
        self.text_browser = text_browser

    def emit(self, record):
        tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        
        msg = record.msg
        if record.levelname == 'INFO':
            text =f'''<p>{tm} <span>{record.levelname}</span> : {msg}</p>''' 
        elif record.levelname == 'DEBUG':
            pass
        elif record.levelname == 'WARNING':
            text =f'''<p>{tm} <span style="color:#eb2d2d">{record.levelname}</span> : {msg}</p>'''
        elif record.levelname == 'CRITICAL':
            text =f'''<p>{tm} <span style="color:#FF0000">{record.levelname}</span> : {msg}</p>'''
        elif record.levelname == 'ERROR':
            text =f'''<p>{tm} <span style="color:#CC0000">{record.levelname}</span> : {msg}</p>'''

        self.text_browser.append(text)

class LogDBHandler(logging.Handler):
    '''
    Customized logging handler that puts logs to the database.
    pymssql required
    '''
    def __init__(self, sql_conn, sql_cursor, db_log_table):
        logging.Handler.__init__(self)
        self.sql_cursor = sql_cursor
        self.sql_conn = sql_conn
        self.log_table = db_log_table

    def emit(self, record):
        # Set current time
        
        tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        # Clear the log message so it can be put to db via sql (escape quotes)
        self.log_msg = record.msg
        # Make the SQL insert
        sql = f'''INSERT INTO {self.log_table}(log_level, log_levelname, log, created_at, created_by) Values(%s,%s,%s,%s,%s)'''
        values = (str(record.levelno),str(record.levelname),str(self.log_msg),tm,str(record.name))
        try:
            self.sql_cursor.execute(sql,values)
            self.sql_conn.commit()
        except Exception as e:
            print(e)
            print(sql)
            print('CRITICAL DB ERROR! Logging to database not possible!')


if __name__ == '__main__':

    db_server = 'servername'
    db_user = 'db_user'
    db_password = 'db_pass'
    db_dbname = 'db_name'
    db_tbl_log = 'log'

    log_file_path = './test.log'
    log_error_level = 'DEBUG'       # LOG error level (file)
    log_to_db = True                    # LOG to database?

    # Main settings for the database logging use
    if (log_to_db):
        # Make the connection to database for the logger
        log_conn = psycopg2.connect("user=postgres password=28556839 dbname=postgres")
        log_cursor = log_conn.cursor()
        log_cursor.execute('''CREATE TABLE if not exists log(id Serial Primary key,
                                                log_level integer,
                                                log_levelname text,
                                                log text,
                                                created_at text,
                                                created_by text
                                            )''')
        logdb = LogDBHandler(log_conn, log_cursor, db_tbl_log)
# Set logger
    logging.basicConfig(filename=log_file_path)
# Set db handler for root logger
    if (log_to_db):
        logging.getLogger('').addHandler(logdb)
    today_date = datetime.today()
    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(f'./ErrorLog/{today_date.date()}.log')        
    handler.setFormatter(formatter)
    # Register MY_LOGGER
    log = logging.getLogger('MY_LOGGER')
    log.addHandler(handler)
    log.setLevel(log_error_level)

    # Example variable
    test_var = 'This is test message'

    # Log the variable contents as an error
    log.error(f'new: {test_var}')
    log.info("we")
    log.debug('wowowowowowowowow')