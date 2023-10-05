import logging, logging.config
from pathlib import Path

import yaml


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class _CustomFormatter(logging.Formatter):
        
    format_str = '[%(asctime)s] %(name)s:%(className)s.%(funcName)s [%(levelname)-8s] %(message)s (%(module)s:%(lineno)d)'

    FORMATS = {
        logging.DEBUG: format_str,
        logging.INFO: bcolors.OKGREEN + format_str + bcolors.ENDC,
        logging.WARNING: bcolors.WARNING + format_str + bcolors.ENDC,
        logging.ERROR: bcolors.FAIL + format_str + bcolors.ENDC,
        logging.CRITICAL: bcolors.FAIL + format_str + bcolors.ENDC
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        
        # I'd like the loglevel and msg to be separated from the name+className+funcName directive.
        original_str = f'{record.name}:{record.className}.{record.funcName}'
        whitespaces_count = len('{:<80}'.format(original_str)) - len(original_str)
        record.funcName = record.funcName + ' ' + '.' * (whitespaces_count - 1)
        
        # tab = len(f'[{record.asctime}] {record.name}:{record.className}.{record.funcName} [{"{:<8}".format(record.levelname)}] ') * ' '
        
        return formatter.format(record)


class CustomLoggerAdapter(logging.LoggerAdapter):
    
    @classmethod
    def getLogger(cls, name: str, *, className: str = '') -> logging.LoggerAdapter:
        """
        Args:
            className (str): Leave empty if the logger is outside of a class
            appName (str): Like 'gui', 'pdf_table_reader' etc...
        """
        return cls(logging.getLogger(name), {'className': className})
    
    
def set_up_logging(*, global_level: str | None = None) -> None:
    path_to_config = Path(__file__).parent.parent.parent / 'logging_config.yaml'
    
    with open(path_to_config) as config:
        config_dict: dict = yaml.safe_load(config.read())
        
        if global_level is not None:
            # Change preset log level to the given one in each handler, logger and the root logger
            
            # handlers
            handlers: dict | None = config_dict.get('handlers', None)
            if handlers is not None:
                for handler_name in handlers.keys():
                    config_dict['handlers'][handler_name]['level'] = global_level
            # loggers
            loggers: dict | None = config_dict.get('loggers', None)
            if loggers is not None:
                for logger_name in loggers.keys():
                    config_dict['loggers'][logger_name]['level'] = global_level
            # root
            root: dict | None = config_dict.get('root', None)
            if root is not None:
                config_dict['root']['level'] = global_level
                
        logging.config.dictConfig(config_dict)
        
    CustomLoggerAdapter.getLogger('app').info('Logging config loaded.')