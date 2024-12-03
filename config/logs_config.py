import logging.config
from datetime import datetime
from .settings import settings
import pytz

tz = pytz.timezone('Europe/Samara')

class DefaultFormatter(logging.Formatter):
    converter = lambda *args: datetime.now(tz).timetuple()

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default_formatter': {
            '()': DefaultFormatter,
            'format': '%(asctime)s :: %(lineno)s :: %(levelname)s :: %(message)s'
        },
    },
    'handlers': {
        'FileHandler_interface': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/interface.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_main': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/main.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_filtration_manager': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/filtration_manager.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_manager_settings': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/manager_settings.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_processing_manager': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/processing_manager.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_load_data': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/load_data.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_processes_control': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/processes_control.log',
            'mode': 'w',
            'encoding': 'utf-8',
        }
    },
    'loggers': {
        'interface': {
            'handlers': ['FileHandler_interface'],
            'level': settings.log_level,
            'propagate': True
        },
        'main': {
            'handlers': ['FileHandler_main'],
            'level': settings.log_level,
            'propagate': True
        },
        'filtration_manager': {
            'handlers': ['FileHandler_filtration_manager'],
            'level': settings.log_level,
            'propagate': True
        },
        'manager_settings': {
            'handlers': ['FileHandler_manager_settings'],
            'level': settings.log_level,
            'propagate': True
        },
        'processing_manager': {
            'handlers': ['FileHandler_processing_manager'],
            'level': settings.log_level,
            'propagate': True
        },
        'load_data': {
            'handlers': ['FileHandler_load_data'],
            'level': settings.log_level,
            'propagate': True
        },
        'processes_control': {
            'handlers': ['FileHandler_processes_control'],
            'level': settings.log_level,
            'propagate': True
        },
    }
}
logging.config.dictConfig(LOGGING_CONFIG)
logger_interface = logging.getLogger('interface')
logger_main = logging.getLogger('main')
logger_filtration_manager = logging.getLogger('filtration_manager')
logger_manager_settings = logging.getLogger('manager_settings')
logger_processing_manager = logging.getLogger('processing_manager')
logger_load_data = logging.getLogger('load_data')
logger_processes_control = logging.getLogger('processes_control')
