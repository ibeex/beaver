# -*- coding: utf-8 -*-
import redis
import time
import urlparse

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class RedisTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(RedisTransport, self).__init__(beaver_config, logger=logger)

        redis_url = beaver_config.get('redis_url')
        redis_password = beaver_config.get('redis_password')
        _url = urlparse.urlparse(redis_url, scheme='redis')
        _, _, _db = _url.path.rpartition('/')

        self._redis = redis.StrictRedis(host=_url.hostname, port=_url.port, password=redis_password, db=int(_db), socket_timeout=10)
        self._redis_namespace = beaver_config.get('redis_namespace')

        wait = 0
        while 1:
            if wait == 20:
                break

            time.sleep(1)
            wait += 1
            try:
                self._redis.ping()
                break
            except UserWarning:
                self._is_valid = False
                raise TransportException('Connection appears to have been lost')
            except Exception, e:
                self._is_valid = False
                try:
                    raise TransportException(e.strerror)
                except AttributeError:
                    raise TransportException('Unspecified exception encountered')

        self._pipeline = self._redis.pipeline(transaction=False)

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        for line in lines:
            self._pipeline.rpush(
                self._redis_namespace,
                self.format(filename, line, timestamp, **kwargs)
            )

        self._pipeline.execute()
