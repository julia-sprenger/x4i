#! /usr/bin/env python

# Copyright (c) 2011, Lawrence Livermore National Security, LLC. Produced at
# the Lawrence Livermore National Laboratory. Written by David A. Brown
# <brown170@llnl.gov>.
#
# LLNL-CODE-484151 All rights reserved.
#
# This file is part of EXFOR Interface (x4i)
#
# Please also read the LICENSE.txt file included in this distribution, under
# "Our Notice and GNU General Public License".
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License (as published by the
# Free Software Foundation) version 2, dated June 1991.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# terms and conditions of the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
################################################################################
#
# Changes since LLNL release (x4i-1.0):
#
#   1.     Add shebang (David Brown <dbrown@bnl.gov>, 2021-06-16T08:16:09)
#   2.     python -> $PYTHON (David Brown <dbrown@bnl.gov>, 2021-06-16T08:15:48)
#
################################################################################

#
#
#  USE THIS CODE TO DOWNLOAD AND INSTALL CORRECT
#  IAEA DATABASE FOR EDITABLE OR DEVELOPER INSTALLS
#
#
import os
import subprocess
import argparse
import tempfile
import shutil
import urllib.request
import json
import zipfile
import datetime
from x4i.exfor_paths import DATAPATH


DOWNLOAD = False  # for debugging with terrible internet, skip downloading

EXFORSOURCES = {
    "NDS-git": {
        "url": "https://github.com/IAEA-NDS/exfor_master.git",
	    "mode": "git",
        "relative_data_path": "exfor_master/exforall/"},
    "NRDC-git": {
        "url": "https://github.com/IAEA-NRDCNetwork/EXFOR-Archive.git",
	    "mode": "git",
	    "relative_data_path": "EXFOR-Archive/EXFOR/"},
    "EXFOR-Master": {	
        "url": "https://www-nds.iaea.org/nrdc/exfor-master/entry/entry.zip",
	    "mode": "zip",
	    "relative_data_path": "entry/"}}
DEFAULTEXFORSOURCE = 'NRDC-git'

#	- commit_hash = ...get the hash...
#	- sha = ...get the hash...
#	- downloaded = ...get the datetime...

__doc__ = """
Install EXFOR data files from one of the varients of the EXFOR Master file or in development NRDC EXFOR git projects.
"""


# ------------------------------------------------------------------------------
#                            .... ARGPARSE ....
# ------------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', dest='verbose', default=False, action='store_true', help="Enable verbose output.")
    parser.add_argument('--source', choices=EXFORSOURCES.keys(), default=DEFAULTEXFORSOURCE,
                        help="Output format (Default: %s)" % DEFAULTEXFORSOURCE)
    parser.add_argument("--db", default=DATAPATH+os.sep+"db", help="Location of local EXFOR data files")
    return parser.parse_args()


# ------------------------------------------------------------------------------
#                            .... UTILITIES ....
# ------------------------------------------------------------------------------
def archive_metadata(_datapath, _metadata):
    return
    raise NotImplementedError()
    with open("x4i/data/database_info.json") as jsonfile:
        jsondata = json.load(jsonfile)
        EXFORZIP = jsondata["zipfile"]
        EXFORURL = jsondata["url"] + EXFORZIP

def remove_old_db(_db):
    print(_db)
    return
    shutil.rmtree()
    raise NotImplementedError() 

def rebuild_index(_datapath, _db):
    return
    raise NotImplementedError() 
    subprocess.run(["bin/setup-exfor-db.py"])


# ------------------------------------------------------------------------------
#                            .... MAIN ....
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    args = parse_args()
    metadata = {}
    metadata.update(EXFORSOURCES[args.source])
    remove_old_db(args.db)

    if DOWNLOAD:
        if EXFORSOURCES[args.source]['mode'] == 'git':
            # pull head from github repo
            subprocess.run(["git", 'clone', '--depth', '1', EXFORSOURCES[args.source]['url']], cwd=DATAPATH)

        elif EXFORSOURCES[args.source]['mode'] == 'zip':
            with tempfile.NamedTemporaryFile(delete=False, dir=DATAPATH) as tmp_file:
                # download file from NRDC page
                with urllib.request.urlopen(
                        urllib.request.Request(
                            EXFORSOURCES[args.source]['url'], 
                            {}, 
                            {'User-Agent': "x4i"})) as response:
                    shutil.copyfileobj(response, tmp_file)
                    # unpack zipfile
                    with zipfile.ZipFile(tmp_file) as zf:
                        zf.extractall(path=DATAPATH)
                # clean up
                if os.path.exists(tmp_file.name):
                    os.remove(tmp_file.name)
        else:
            raise ValueError("EXFOR source %s unknown" % args.source)

    # link right place to "db"
    #os.symlink(DATAPATH + os.sep + EXFORSOURCES[args.source]['relative_data_path'], args.db)
    metadata['downloaded'] = str(datetime.datetime.now())
    archive_metadata(DATAPATH, metadata)
    rebuild_index(DATAPATH, args.db)


