import logging


class ErrorLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'ERROR'


class DebugWarningLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname in ('DEBUG', 'INFO')


class CriticalLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'CRITICAL'