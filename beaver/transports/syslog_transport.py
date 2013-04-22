import socket

from beaver.transports.base_transport import BaseTransport


class SyslogTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(SyslogTransport, self).__init__(beaver_config, logger=logger)
        FACILITY = {
            'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
            'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
            'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
            'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
            'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23}
        LEVEL = {
            'emerg': 0, 'alert': 1, 'crit': 2, 'err': 3,
            'warning': 4, 'notice': 5, 'info': 6, 'debug': 7}

        self._sock = socket.socket(socket.AF_INET,  # Internet
                                   socket.SOCK_DGRAM)  # UDP
        self._address = (beaver_config.get('syslog_host'), beaver_config.get('syslog_port'))
        self.level = LEVEL[beaver_config.get('syslog_level')]
        self.facility = FACILITY[beaver_config.get('syslog_facility')]

    def callback(self, filename, lines, **kwargs):

        for line in lines:
            self._sock.sendto(self.format(filename, line, **kwargs), self._address)
