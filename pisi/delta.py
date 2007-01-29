# -*- coding: utf-8 -*-
#
# Copyright (C) 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
from sets import Set as set

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
from pisi.package import Package
import pisi.util as util
import pisi.archive as archive

def create_delta_package(old_package, new_package):

    oldpkg = Package(old_package, "r")
    newpkg = Package(new_package, "r")

    newmd = newpkg.get_metadata()
    oldmd = oldpkg.get_metadata()

    oldfiles = oldpkg.get_files()
    newfiles = newpkg.get_files()

    files_new = set(map(lambda x:(x.path, x.hash), newfiles.list))
    files_old = set(map(lambda x:(x.path, x.hash), oldfiles.list))
    files_delta = files_new - files_old

    if not files_delta:
        ctx.ui.info(_("Nothing has changed between builds, not creating a delta"))
        return

    ctx.ui.info(_("Creating delta PiSi package between %s %s") % (old_package, new_package))

    # Unpack new package to temp    
    newpkg_name = util.package_name(newmd.package.name, newmd.package.version, newmd.package.release, newmd.package.build, False)
    newpkg_path = util.join_path(ctx.config.tmp_dir(), newpkg_name)
    newpkg.extract_to(newpkg_path, True)

    tar = archive.ArchiveTar(util.join_path(newpkg_path, ctx.const.install_tar_lzma), 'tarlzma', False, False)
    tar.unpack_dir(newpkg_path)

    # Create delta package
    deltaname = "%s-%s-%s%s" % (oldmd.package.name, oldmd.package.release, newmd.package.release, ".delta.pisi")
    
    outdir = ctx.get_option('output_dir')
    if outdir:
        deltaname = util.join_path(outdir, deltaname)

    print deltaname
    deltapkg = Package(deltaname, "w")

    c = os.getcwd()
    os.chdir(newpkg_path)

    # add comar files to package
    for pcomar in newmd.package.providesComar:
        fname = util.join_path(ctx.const.comar_dir, pcomar.script)
        deltapkg.add_to_package(fname)

    # add xmls and files
    deltapkg.add_to_package(ctx.const.metadata_xml)
    deltapkg.add_to_package(ctx.const.files_xml)

    ctx.build_leftover = util.join_path(ctx.config.tmp_dir(), ctx.const.install_tar_lzma)

    tar = archive.ArchiveTar(util.join_path(ctx.config.tmp_dir(), ctx.const.install_tar_lzma), "tarlzma")
    for path, hash in files_delta:
        tar.add_to_archive(path)
    tar.close()

    os.chdir(ctx.config.tmp_dir())
    deltapkg.add_to_package(ctx.const.install_tar_lzma)
    deltapkg.close()

    os.unlink(util.join_path(ctx.config.tmp_dir(), ctx.const.install_tar_lzma))
    ctx.build_leftover = None
    os.chdir(c)

    ctx.ui.info(_("Done."))
