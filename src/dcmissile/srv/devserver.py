import logging
import os
import sys

from twisted.internet import protocol, reactor, task
from twisted.internet.error import ProcessDone, ProcessTerminated


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    level=logging.DEBUG)
log = logging.getLogger('devserver')

current_dir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.abspath(os.path.join(current_dir, "..", ".."))

class FileChecker(object):
    def __init__(self):
        self.has_changes = False
        self._mtimes = {}
        self._win = (sys.platform == "win32")

    def __call__(self, arg, curr_dir, files):
        if self.has_changes:
            return
        for filename in files:
            if len(filename) < 3 or filename[-3:] != '.py':
                continue
            fullpath = os.path.join(curr_dir, filename)
            stat = os.stat(fullpath)
            mtime = stat.st_mtime
            if self._win:
                mtime -= stat.st_ctime
            if fullpath not in self._mtimes:
                self._mtimes[fullpath] = mtime
                continue
            if mtime != self._mtimes[fullpath]:
                self._mtimes = {}
                self.has_changes = True
                log.debug("has changes!")

class FSMonitor(object):
    def __init__(self):
        self._counter = 0
        self.file_check = FileChecker()
        self._killing_server = False

    @property
    def is_changed(self):
        os.path.walk(basedir, self.file_check, None)
        return self.file_check.has_changes

    @property
    def launcher(self):
        return self._launcher

    @launcher.setter
    def launcher(self, l):
        self._launcher = l

    @property
    def killing_server(self):
        return self._killing_server

    @killing_server.setter
    def killing_server(self, value):
        """If we finished killing server, let's reset file checker"""
        if self._killing_server and not value:
            self.file_check = FileChecker()
        self._killing_server = value


fsmonitor = FSMonitor()


def check_modules():
    if fsmonitor.killing_server:
        return
    if fsmonitor.is_changed:
        log.debug("modules changed")
        fsmonitor.killing_server = True
        fsmonitor.launcher.transport.signalProcess('KILL')


class WebServerLauncher(protocol.ProcessProtocol):
    def __init__(self):
        pass

    def connectionMade(self):
        log.info("process started")

    def outReceived(self, data):
        sys.stdout.write(data)

    def errReceived(self, data):
        sys.stdout.write(data)

    def processEnded(self, reason):
        log.info("process ended")
        if reason.check(ProcessDone):
            log.info("Process Done")
        elif reason.check(ProcessTerminated):
            log.info("Caught Kill Signal")
        else:
            log.error(str(reason.type))
            log.error(str(reason.value))

        log.debug("Scheduling other instance")
        reactor.callLater(1.0, start_webserver)
        

def start_webserver():
    log.info("starting web server...")
    fsmonitor.launcher = WebServerLauncher()
    reactor.spawnProcess(fsmonitor.launcher, sys.executable,
            [sys.executable, 'server.py'],
            env=os.environ,
            path=current_dir
    )
    log.info("web server started!")
    fsmonitor.killing_server = False

def start():
    start_webserver()
    t = task.LoopingCall(check_modules)
    t.start(1.0) # every second
    log.info("FSNotifier launched!")


def main():
    reactor.callLater(1.0, start)
    reactor.run()

if __name__ == '__main__':
    main()
