#! -*- coding: utf-8 -*-
import atexit
import logging
import socket
import sys

import abc
import os

from skee_t.conf import CONF

__author__ = 'pluto'

DOT_CHAR = '.'

LOG = logging.getLogger(__name__)


class Launcher(object):

    def __init__(self, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super(Launcher, self).__init__()
        self.__started = False
        self.__running = True
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.del_sock)
        pid = str(os.getpid())
        file(CONF.pid_file, 'w+').write('%s\n' % pid)

    def start(self):
        self.daemonize()
        LOG.info('skee_t starting...')
        try:
            self._run()
            LOG.info('skee_t has been started.')
        except Exception:
            LOG.exception("start error.")
        self._wait()

    @abc.abstractmethod
    def _run(self):
        pass

    @abc.abstractmethod
    def _pre_close(self):
        pass

    def set_running(self, value=True):
        self.__running = value

    def del_sock(self):
        os.remove(CONF.sock_file)
        os.remove(CONF.pid_file)

    def _wait(self):
        shutdown_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        shutdown_sock.bind(CONF.sock_file)
        shutdown_sock.listen(1)
        while self.__running:
            conn, address = shutdown_sock.accept()
            LOG.debug('The agent launcher has been listened [%s]' % address)
            recv_data = conn.recv(1024)
            print recv_data
            if recv_data == 'SHUTDOWN':
                self.set_running(False)
                self._pre_close()
                conn.close()
        shutdown_sock.close()
        #self.del_sock()
        LOG.info('The unix connection of protoss agent has been closed.')

    @staticmethod
    def stop():
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(CONF.sock_file)
        sock.sendall('SHUTDOWN')
        sock.close()

