import socket
import os

import beaver.transport


class SyslogTransport(beaver.transport.Transport):

    def __init__(self):
        FACILITY = {
            'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
            'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
            'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
            'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
            'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
        }
        LEVEL = {
            'emerg': 0, 'alert': 1, 'crit': 2, 'err': 3,
            'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
        }

        self.syslog = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = os.environ.get("SYSLOG_ADDRESS", "127.0.0.1")
        self.port = int(os.environ.get("SYSLOG_PORT", "514"))
        self.level = LEVEL[os.environ.get("SYSLOG_LEVEL", "info")]
        self.facility = FACILITY[os.environ.get("SYSLOG_FACILITY", "user")]

    def callback(self, filename, lines):
        for line in lines:
            msg = '<%d>%s:%s' % (self.level + self.facility * 8, filename, line)
            self.syslog.sendto(msg, (self.host, self.port))

    def interrupt(self):
        self.syslog.close()

    def unhandled(self):
        return True
