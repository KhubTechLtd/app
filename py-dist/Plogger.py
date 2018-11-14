import logging.config
import structlog
import os
import sys
import datetime
import logging


class Log:

    def __init__(self):
        self.info_path = ""
        self.error_path = ""
        self.log_directory = ""


    def process_structlog(self):
        # setup the directory and the log files
        self.log_files_setup()

        # setup the loggers
        self.configure_logging()

        try:

            """ structlog setup """ 
            structlog_processors = list([
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                ])

            structlog_processors.append(structlog.processors.JSONRenderer())
            structlog_processors.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)

            structlog.configure(
                processors=structlog_processors,
                logger_factory=structlog.stdlib.LoggerFactory(),
                cache_logger_on_first_use=True,
                )
        except Exception as e:
            print (e)


    def log_files_setup(self):
        # set the current date
        date_today = datetime.datetime.now()
        this_date = date_today.strftime('%d-%m-%Y')

        # recreate the log files
        if sys.platform == 'win32':
            self.log_directory = "C:\\Users\\Public\\PosServer\\packager"
            self.info_path = self.log_directory + '\\' + this_date + '_info.log'
            self.error_path = self.log_directory + '\\' + this_date + '_error.log'
        else:
            self.log_directory = os.path.expanduser('~/PosServer/packager')
            self.info_path = self.log_directory + '/' + this_date + '_info.log'
            self.error_path = self.log_directory + '/' + this_date + '_error.log'

        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

    def configure_logging(self):
        print('configuring logging .... ')
        LOGFILE_SIZE = 5 * 1024 * 1024
        LOGFILE_COUNT = 10
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                "verbose": {
                    "format": "[%(asctime)s] %(levelname)s module=%(module)s, "
                              "process_id=%(process)d, path=%(pathname)s, "
                              "line=%(lineno)d, %(message)s"
                },
                'standard': {
                    'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'simple': {
                    'format': '[%(asctime)s] %(levelname)s %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
            },
            'handlers': {
                'null': {
                    'class': 'logging.NullHandler',
                },
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple'
                },
                'error': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': self.error_path,
                    'maxBytes': LOGFILE_SIZE,
                    'backupCount': LOGFILE_COUNT,
                    'formatter': 'verbose'
                },
                'info': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': self.info_path,
                    'maxBytes': LOGFILE_SIZE,
                    'backupCount': LOGFILE_COUNT,
                    'formatter': 'verbose'
                },
            },
            'loggers': {
                '': {
                    'handlers': ['info', 'error'],
                    'level': 'INFO',
                    'propagate': True
                },
                'error_logger': {
                    'handlers': ['error'],
                    'level': 'ERROR',
                    'propagate': True
                },
                'info_logger': {
                    'handlers': ['info'],
                    'level': 'INFO',
                    'propagate': True
                }
            }
        })