#!/usr/bin/env python3

from flask import jsonify, abort
import logging
import time

from classes.Dictionnary import Dictionnary


ANSI_COLORS = {
    'default': '\033[0m',
    'white': '\033[37m',
    'grey': '\033[38m',
    'green': '\033[32m',
    'bold_green': '\033[32;1m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'bold_magenta': '\033[35;1m',
    'cyan': '\033[36m',
    'yellow': '\033[33m',
    'bold_yellow': '\033[33;1m',
    'red': '\033[31m',
    'bold_red': '\033[31;1m',
}

WRITE = 15
REQUEST = 24
RESPONSE = 26
EXCEPTION = 45

logging.addLevelName(WRITE, "WRITE")
logging.addLevelName(REQUEST, "REQUEST")
logging.addLevelName(RESPONSE, "RESPONSE")
logging.addLevelName(EXCEPTION, "EXCEPTION")
logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)',
    filename='logs/server.log',
    filemode='a',
)


class CustomFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.ansi_colors = ANSI_COLORS
        self.formatStandard = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.formatAnormal = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
        self.formatExceptions = ["%(asctime)s - %(name)s - %(levelname)s", " - %(message)s (%(filename)s:%(lineno)d)"]

        self.FORMATS = {
            logging.NOTSET: self.ansi_colors.get('grey') + self.formatStandard + self.ansi_colors.get('default'),
            WRITE: self.ansi_colors.get('grey') + self.formatStandard + self.ansi_colors.get('default'),
            logging.DEBUG: self.ansi_colors.get('magenta') + self.formatAnormal + self.ansi_colors.get('default'),
            logging.INFO: self.ansi_colors.get('grey') + self.formatStandard + self.ansi_colors.get('default'),
            REQUEST: self.ansi_colors.get('blue') + self.formatStandard + self.ansi_colors.get('default'),
            RESPONSE: self.ansi_colors.get('green') + self.formatStandard + self.ansi_colors.get('default'),
            logging.WARNING: self.ansi_colors.get('yellow') + self.formatAnormal + self.ansi_colors.get('default'),
            logging.ERROR: self.ansi_colors.get('red') + self.formatAnormal + self.ansi_colors.get('default'),
            EXCEPTION: self.ansi_colors.get('bold_red') + self.formatExceptions[0] + self.ansi_colors.get('default') + self.ansi_colors.get('red') + self.formatExceptions[1] + self.ansi_colors.get('default'),
            logging.CRITICAL: self.ansi_colors.get('bold_red') + self.formatAnormal + self.ansi_colors.get('default'),
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)

class Log(Dictionnary):
    def __init__(self):
        self.Dictionnary = Dictionnary()

        self.level = 10
        self.ansi_colors = ANSI_COLORS
        self.start_time = None

        self.logger = logging.getLogger("AI Playground server")
        self.logger.setLevel(self.level)

        ch = logging.StreamHandler()
        ch.setFormatter(CustomFormatter())
        self.logger.addHandler(ch)
        self.logger.custom_write = lambda *args: self.logger.log(WRITE, ' '.join(map(str, args)), stacklevel=3)

################################################################################
# Private methods
################################################################################

    def _format_status_code(self, status_code):
        """ Format status code. """
        if status_code == 200:
            return f"{self.ansi_colors.get('bold_green')}{status_code}{self.ansi_colors.get('default')}{self.ansi_colors.get('green')}"
        elif status_code >= 400 and status_code < 500:
            return f"{self.ansi_colors.get('bold_magenta')}{status_code}{self.ansi_colors.get('default')}{self.ansi_colors.get('green')}"
        elif status_code == 500:
            return f"{self.ansi_colors.get('bold_red')}{status_code}{self.ansi_colors.get('default')}{self.ansi_colors.get('green')}"
        else:
            return f"{self.ansi_colors.get('bold_blue')}{status_code}{self.ansi_colors.get('default')}{self.ansi_colors.get('green')}"

################################################################################
# Public methods
################################################################################

    def write(self, *args):
        """ Log write. """
        self.logger.custom_write(' '.join(map(str, args)))

    def debug(self, *args):
        """ Log debug. """
        self.logger.debug(' '.join(map(str, args)))

    def info(self, *args):
        """ Log info. """
        self.logger.info(' '.join(map(str, args)))

    def warning(self, *args):
        """ Log warning. """
        self.logger.warning(' '.join(map(str, args)))

    def error(self, *args):
        """ Log error. """
        self.logger.error(' '.join(map(str, args)), stacklevel=2)

    def critical(self, *args):
        """ Log critical. """
        self.logger.critical(' '.join(map(str, args)))

    def exception(self, error_id, **kwargs):
        """ Log exception. """
        error = self.Dictionnary.errors_dictionary.get(error_id)
        error_code = error.get('code') if error else 500
        error_message = error.get('message') if error else error_id
        formatted_message = f"{error_message}{' | ' + str(kwargs) if kwargs else ''}"

        self.logger.log(EXCEPTION, {
            'code': error_code,
            'message': error_message,
            **kwargs
        }, exc_info=True, stack_info=False, stacklevel=2)

        abort(error_code, formatted_message)

    def log_request(self, request):
        """ Log incoming request. """
        self.start_time = time.time()
        msg = (
            f"[{str(request.remote_addr)}]->{request.url}[{request.method}]"
            f"|args:{str(dict(request.args) if dict(request.args) else None)}|data:{str(request.get_json()) if request.is_json else None}"
        )
        self.logger.log(REQUEST, msg)

    def log_response(self, response):
        """ Log outgoing response. """
        response_time = ((time.time() - self.start_time) * 1000).__round__(5)
        msg = f"{self._format_status_code(response.status_code)} in {response_time}ms"
        self.logger.log(RESPONSE, msg)


log = Log()
