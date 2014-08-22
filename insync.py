#!/usr/bin/env python
"""
Autosync local files with remote host

Usage:
    insync [-c <config>] [-l <log_file>]

Options:
    -c <config>     path to config file. [default: ./insync.yaml]
    -l <log_file>   path to log file. [default: ./insync.log]
"""
from __future__ import print_function
import logging
import logging.handlers
import sys
import psh
import os
import os.path
import asyncore
import re

import yaml
import pyinotify
from docopt import docopt
import time
from ndict import NDict


__version__ = "0.1"


class DirWatcher(pyinotify.ProcessEvent):
    """Tail reader class"""

    def my_init(self, conf_path, log_fname):
        """Chained constructor: see docs/sources for pyinotify.__init__()"""

        self.path = []
        self.conf = NDict(self.read_conf(conf_path))
        self.log = self.setup_logging(sys.argv[0], log_fname,
                                      log_level=logging.INFO)

    def read_conf(self, fname, _fail=True):
        try:
            f = open(fname)
        except Exception as e:
            if _fail == True:
                print("%s file not found: %s" % (fname, str(e), ))
            else:
                return {}
        else:
            conf = yaml.load(f)
            f.close()
            if conf is None:
                return {}
            return conf

    def setup_logging(self, name, fname, log_level=logging.DEBUG):
        """Setup simple logging to file"""

        log = logging.getLogger(name)
        handler = logging.FileHandler(fname)
        fmt = "%(asctime)s %(levelname)s: %(filename)s[%(process)s]: %(message)s"
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        log.addHandler(handler)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.setLevel(log_level)
        log.propagate = True

        return log

    def start_loop(self):
        """Start loop"""

        eventmask = pyinotify.IN_DELETE | pyinotify.IN_CREATE |\
                    pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO |\
                    pyinotify.IN_MOVE_SELF
        wm = pyinotify.WatchManager()  # Watch Manager
        notifier = pyinotify.AsyncNotifier(wm, self)

        for _dir in self.conf.keys():
            if os.path.isdir(_dir) == True:
                self.path.append(_dir)
                wdd = wm.add_watch(_dir, eventmask, auto_add=True, rec=True)
                self.log.info("Watch for {0}".format(_dir))
            else:
                self.log.warning("dir %s defined in conf but not exists", _dir)

        try:
            asyncore.loop()
        except asyncore.ExitNow:
            pass

    def check_exclude(self, path, fname):
        """Check fname for exclude pattern"""

        for pattern in self.conf[path].exclude:
            p = re.compile(pattern)
            if p.match(fname) is not None:
                return True

        return False

    def process_IN_CREATE(self, event):
        self.log.debug("Creating: %s", event.pathname)

    def process_IN_DELETE(self, event):
        self.log.debug("Deleting: %s", event.pathname)

    def process_IN_MOVE_SELF(self, event):
        self.log.debug("Moving self: %s", event.pathname)

    def process_IN_MOVED_TO(self, event):
        self.log.debug("Moved to: %s", event.pathname)
        if event.pathname.startswith(self.path[0]):
            if self.sync(event.pathname) is not None:
                self.log.info("MT: file {0} was synced".format(event.pathname))
        else:
            self.log.debug("Ignoring")

    def process_IN_MODIFY(self, event):
        self.log.debug("Modifing: %s", event.pathname)

        if event.pathname.startswith(self.path[0]):
            if self.sync(event.pathname) is not None:
                self.log.info("M: file {0} was synced".format(event.pathname))
        else:
            self.log.debug("Ignoring")

    def sync(self, fname):
        """Sync file with remote"""

        for path in self.conf.keys():
            if fname.startswith(path) and not self.check_exclude(path, fname):
                time.sleep(0.5)
                rel_path = fname.split(path)[1]
                cmd = "scp -P {0} \"{1}\" {2}@{3}:\"{4}\" 2>&1 > /dev/null".format(self.conf[path].port,
                                                                           fname, self.conf[path].user,
                                              self.conf[path].host, self.conf[path].path + rel_path)

                self.log.debug("cmd: {0} (exit: {1})".format(cmd, os.system(cmd)))

                return True


def main():
    """Main function"""

    args = docopt(__doc__, version=__version__)

    dw = DirWatcher(**{ "conf_path": args["-c"], "log_fname": args["-l"] })
    dw.start_loop()
    #dw.sync("/home/dk/devel/c2/common/c2/core.py")
    #print(dw.check_exclude("/home/dk/devel/c2/common", "/home/dk/devel/c2/common/c2/core.py"))





if __name__ == "__main__":
    main()

