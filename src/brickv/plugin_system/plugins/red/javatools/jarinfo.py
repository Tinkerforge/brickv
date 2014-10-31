# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, see
# <http://www.gnu.org/licenses/>.


"""
Module and utility for fetching information out of a JAR file, and
printing it out.

:author: Christopher O'Brien  <obriencj@gmail.com>
:license: LGPL
"""


from json import dump
from sys import stdout

from brickv.plugin_system.plugins.red.javatools import unpack_class
from brickv.plugin_system.plugins.red.javatools.dirutils import fnmatches
from brickv.plugin_system.plugins.red.javatools.ziputils import open_zip_entry, zip_file, zip_entry_rollup


__all__ = (
    "JAR_PATTERNS", "JarInfo",
    "main", "cli", "jarinfo_optgroup",
    "cli_jar_classes", "cli_jar_manifest_info",
    "cli_jar_provides", "cli_jar_requires",
    "cli_jar_zip_info", "cli_jarinfo",
    "cli_jarinfo_json", )


# for reference by other modules
JAR_PATTERNS = ( "*.ear",
                 "*.jar",
                 "*.rar",
                 "*.sar",
                 "*.war", )


REQ_BY_CLASS = "class.requires"
PROV_BY_CLASS = "class.provides"


class JarInfo(object):

    def __init__(self, filename=None, zipfile=None):
        if not (filename or zipfile):
            raise TypeError("one of pathname or zipinfo must be specified")

        self.filename = filename
        self.zipfile = zipfile

        self._requires = None
        self._provides = None


    def __del__(self):
        self.close()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return (exc_type is None)


    def open(self, entry, mode='r'):
        return open_zip_entry(self.get_zipfile(), entry, mode)


    def _collect_requires_provides(self):
        req = {}
        prov = {}

        # we need to collect private provides in order to satisfy deps
        # for things like anonymous inner classes, which have access
        # to private members of their parents. This is only used to
        # filter out false-positive requirements.
        p = set()

        for entry in self.get_classes():
            ci = self.get_classinfo(entry)
            for sym in ci.get_requires():
                req.setdefault(sym, list()).append((REQ_BY_CLASS,entry))
            for sym in ci.get_provides(private=False):
                prov.setdefault(sym, list()).append((PROV_BY_CLASS,entry))
            for sym in ci.get_provides(private=True):
                p.add(sym)

        req = dict((k,v) for k,v in req.iteritems() if k not in p)

        self._requires = req
        self._provides = prov


    def get_requires(self, ignored=tuple()):
        if self._requires is None:
            self._collect_requires_provides()

        d = self._requires
        if ignored:
            d = dict((k,v) for k,v in d.iteritems()
                     if not fnmatches(k, *ignored))
        return d


    def get_provides(self, ignored=tuple()):
        if self._provides is None:
            self._collect_requires_provides()

        d = self._provides
        if ignored:
            d = dict((k,v) for k,v in d.iteritems()
                     if not fnmatches(k, *ignored))
        return d


    def get_classes(self):
        """
        sequence of .class files in the underlying zip
        """

        for n in self.get_zipfile().namelist():
            if fnmatches(n, "*.class"):
                yield n


    def get_classinfo(self, entry):
        """
        fetch a class entry as a JavaClassInfo instance
        """

        with self.open(entry) as cfd:
            return unpack_class(cfd)


    def get_zipfile(self):
        if self.zipfile is None:
            self.zipfile = zip_file(self.filename)
        return self.zipfile


    def close(self):
        if self.zipfile:
            self.zipfile.close()
            self.zipfile = None