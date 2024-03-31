import logging
import os
import sys
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import random

from django.conf import settings
from django.utils.translation import gettext_lazy as _


class PackagePathFilter(logging.Filter):
    def filter(self, record):
        pathname = record.pathname
        record.relativepath = None
        abs_sys_paths = map(os.path.abspath, sys.path)
        for path in sorted(abs_sys_paths, key=len, reverse=True):  # longer paths first
            if not path.endswith(os.sep):
                path += os.sep
            if pathname.startswith(path):
                record.relativepath = os.path.relpath(pathname, path)
                break
        return True


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    This class is a customization of TimedRotatingFileHandler.
    The best way I found to rotate the logs based on midnight.
    This class works with a little bug on the very first log
    emitted because when the server starts the init method is
    fired 3 times and the log file created remains open in the
    python cache (o RAM idk). The fix consist in closing these
    files when the server starts but the bug is on the first
    log emitted.
    """
    templateName = ''
    suffixMapping = {
        'S': '%Y-%m-%d_%H-%M-%S',
        'M': '%Y-%m-%d_%H-%M',
        'H': '%Y-%m-%d_%H',
        'D': '%Y-%m-%d',
        'midnight': '%Y-%m-%d',
        'W': '%Y-%m-%d'
    }

    def __init__(self, filename="", when="midnight", interval=1, backupCount=14, templateName=''):
        self.templateName = templateName
        filename = filename.format(datetime.now().strftime(self.suffixMapping.get(when, "W")))
        super(CustomTimedRotatingFileHandler, self).__init__(
            filename=filename,
            when=when,
            interval=int(interval),
            backupCount=int(backupCount)
        )
        # self.stream.flush()
        # self.stream.close()
        # self._open()

    def getFilesToDelete(self):
        """
        Customization of the parent getFilesToDelete.
        If there are more than backupCount file in the log folder
        add in the remove list all older files
        """
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        for fileName in fileNames:
            result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result

    def doRollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        newFileName = self.templateName.format(datetime.now().strftime(self.suffix))
        dirName, baseName = os.path.split(self.baseFilename)
        self.baseFilename = f"{dirName}/{newFileName}"
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


def environment_callback(request):
    if settings.DEBUG:
        return [_("Development"), "info"]

    return [_("Production"), "warning"]


def badge_callback(request):
    return f"+{random.randint(1, 99)}"


def permission_callback(request):
    return True
