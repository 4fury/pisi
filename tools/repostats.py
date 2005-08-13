#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#

import sys
import os

sys.path.append('.')
import pisi.specfile
import pisi.purl

class Histogram:
    def __init__(self):
        self.list = {}
    
    def add(self, name):
        if self.list.has_key(name):
            self.list[name] = self.list[name] + 1
        else:
            self.list[name] = 1
    
    def _sortfunc(self, x, y):
        if x[1] > y[1]:
            return -1
        elif x[1] == y[1]:
            return 0
        else:
            return 1
    
    def get_list(self):
        items = self.list.items()
        items.sort(self._sortfunc)
        return items


def echo(string):
    print string.encode("utf8")

def scan_pspec(folder):
    paks = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            paks.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return paks

hosts = Histogram()
people = Histogram()
licenses = Histogram()
components = Histogram()
mostp_name = None
mostp_count = 0
nr_binpaks = 0
nr_patches = 0

errors = []

paks = scan_pspec(sys.argv[1])
for pak in paks:
    spec = pisi.specfile.SpecFile()
    try:
        spec.read(os.path.join(pak, "pspec.xml"))
    except Exception, inst:
        errors.append([pak, str(inst)])
        continue
    if spec.verify() is False:
        errors.append([pak, "specfile verification failed"])
        continue
    nr_binpaks += len(spec.packages)
    nr_patches += len(spec.source.patches)
    if len(spec.source.patches) > mostp_count:
        mostp_count = len(spec.source.patches)
        mostp_name = spec.source.name
    name = spec.source.packager.name
    lices = spec.source.license
    partof = spec.source.partof
    if partof:
        components.add(partof)
    people.add(name)
    for lice in lices:
        licenses.add(lice)
    host = pisi.purl.PUrl(spec.source.archiveUri).location()
    hosts.add(host)

print "<html><head><title>%s İstatistikleri</title>" % (sys.argv[1])
print '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
print "</head><body>"

print "<p>Toplam %d kod paketi, ve bunlardan oluşturulacak %d ikili paket var.</p>" % (len(paks), nr_binpaks)
echo(u"<p>Toplam peç sayısı %d</p>" % nr_patches)
if mostp_count > 0:
    echo(u"<p>En çok peçlenen yazılım %d peçle %s!</p>" % (mostp_count, mostp_name))

if errors != []:
    print "<h1>Hatalar</h1><table>"
    for e in errors:
        print "<tr><td>%s</td><td>%s</td></tr>" % (e[0], e[1])
    print "</table>"
else:
    print "<p>Hata yok, tebrikler!</p>"

print "<h1>Komponentler</h1><table>"
for name,cnt in components.get_list():
    print "<tr><td>%s</td><td>%s</td>" % (name, cnt)
print "</table>"

print "<h1>Paketleyiciler</h1><table>"
for name,cnt in people.get_list():
    echo("<tr><td>%s</td><td>%s</td>" % (name, cnt))
print "</table>"

print "<h1>Lisanslar</h1><table>"
for name,cnt in licenses.get_list():
    print "<tr><td>%s</td><td>%s</td>" % (name, cnt)
print "</table>"

echo(u"<h1>Kod kaynakları</h1><table>")
for name,cnt in hosts.get_list():
    print "<tr><td>%s</td><td>%s</td>" % (name, cnt)
print "</table>"

print "</body>"
