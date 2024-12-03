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
        'FileHandler_app_clinic_user': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_clinic_user.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_desyncdata': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_desyncdata.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_device': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_device.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_patient': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_patient.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_sse': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_sse.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_type_research': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_type_research.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_user': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_user.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_admin_panel': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_admin_panel.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_clinic': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_clinic.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_clinic_address': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_clinic_address.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_desyncdata_admin': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_desyncdata_admin.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_device_admin': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_device_admin.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_device_type': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_device_type.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_patient_admin': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_patient_admin.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_type_research_admin': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_type_research_admin.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_user_admin': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_user_admin.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_settings': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_settings.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
        'FileHandler_app_login': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': 'logs/app_login.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'app_clinic_user': {
            'handlers': ['FileHandler_app_clinic_user'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_desyncdata': {
            'handlers': ['FileHandler_app_desyncdata'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_device': {
            'handlers': ['FileHandler_app_device'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_patient': {
            'handlers': ['FileHandler_app_patient'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_sse': {
            'handlers': ['FileHandler_app_sse'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_type_research': {
            'handlers': ['FileHandler_app_type_research'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_user': {
            'handlers': ['FileHandler_app_user'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_admin_panel': {
            'handlers': ['FileHandler_app_admin_panel'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_clinic': {
            'handlers': ['FileHandler_app_clinic'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_clinic_address': {
            'handlers': ['FileHandler_app_clinic_address'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_desyncdata_admin': {
            'handlers': ['FileHandler_app_desyncdata_admin'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_device_admin': {
            'handlers': ['FileHandler_app_device_admin'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_device_type': {
            'handlers': ['FileHandler_app_device_type'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_patient_admin': {
            'handlers': ['FileHandler_app_patient_admin'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_type_research_admin': {
            'handlers': ['FileHandler_app_type_research_admin'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_user_admin': {
            'handlers': ['FileHandler_app_user_admin'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_settings': {
            'handlers': ['FileHandler_app_settings'],
            'level': settings.log_level,
            'propagate': True
        },
        'app_login': {
            'handlers': ['FileHandler_app_login'],
            'level': settings.log_level,
            'propagate': True
        },
    }
}
logging.config.dictConfig(LOGGING_CONFIG)

logger_app_clinic_user = logging.getLogger('app_clinic_user')
logger_app_desyncdata = logging.getLogger('app_desyncdata')
logger_app_device = logging.getLogger('app_device')
logger_app_patient = logging.getLogger('app_patient')
logger_app_sse = logging.getLogger('app_sse')
logger_app_type_research = logging.getLogger('app_type_research')
logger_app_user = logging.getLogger('app_user')
logger_app_settings = logging.getLogger('app_settings')

logger_app_login = logging.getLogger('app_login')

logger_app_admin_panel = logging.getLogger('app_admin_panel')
logger_app_clinic = logging.getLogger('app_clinic')
logger_app_clinic_address = logging.getLogger('app_clinic_address')
logger_app_desyncdata_admin = logging.getLogger('app_desyncdata_admin')
logger_app_device_admin = logging.getLogger('app_device_admin')
logger_app_device_type = logging.getLogger('app_device_type')
logger_app_patient_admin = logging.getLogger('app_patient_admin')
logger_app_type_research_admin = logging.getLogger('app_type_research_admin')
logger_app_user_admin = logging.getLogger('app_user_admin')
