#!/usr/bin/env python3

import logging
import time


class _Logs:
    def __init__(self):
        self.start_time = None
        self.colors = {
            'default': '\033[0m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
        }

        logging.basicConfig(level=logging.INFO)

    def write(self, *args):
        """ Write to console

        Args:
            *args: Any number of arguments

        Returns:
            None
        """
        logging.info(' '.join(map(str, args)))

    def log_request(self, request):
        """ Log incoming request

        Args:
            request: Flask request object

        Returns:
            None
        """
        self.start_time = time.time()
        self.write(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}]|"
            f"{self.colors['green']}Receipt{self.colors['default']}[{str(request.remote_addr)}]->{request.url}[{request.method}]"
            f"|args:{str(dict(request.args) if dict(request.args) else None)}|data:{str(request.get_json()) if request.is_json else None}"
        )

    def log_response(self, response):
        """ Log outgoing response

        Args:
            response: Flask response object

        Returns:
            None
        """
        response_time = ((time.time() - self.start_time) * 1000).__round__(5)
        self.write(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}]|"
            f"{self.colors['yellow']}Response{self.colors['default']}:{self.format_status_code(response.status_code)}:{response_time}ms"
        )

    def format_status_code(self, status_code):
        """ Format status code with color

        Args:
            status_code: HTTP status code

        Returns:
            Formatted status code
        """
        if status_code == 200:
            return f"{self.colors['green']}{status_code}{self.colors['default']}"
        elif status_code >= 400 and status_code < 500:
            return f"{self.colors['magenta']}{status_code}{self.colors['default']}"
        elif status_code == 500:
            return f"{self.colors['red']}{status_code}{self.colors['default']}"
        else:
            return f"{self.colors['blue']}{status_code}{self.colors['default']}"



_log = _Logs()
