#!/usr/bin/python

#
#   Copyright (C) 2017  Olivier Martin <olivier@labapart.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

# Example of usage:
#	../../tools/apt-build-tree.py ubuntu trusty amd64 $PWD 'libgtk2.0-dev libpango1.0-dev'

import argparse
import os
import shutil
import sqlite3
import subprocess
import urllib

parser = argparse.ArgumentParser(description='Build package list for Linux Distribution.')
parser.add_argument('distribution', choices=['debian', 'ubuntu'], help='Linux distribution')
parser.add_argument('distribution_version', type=str, help='Linux distribution')
parser.add_argument('architecture', choices=['amd64', 'arm64'], help='CPU Architecture')
parser.add_argument('build_root', type=str, help='Location to store the Linux Distribution package.')
parser.add_argument('packages', type=str, help='List of packages (and their versions)')
args = parser.parse_args()

# Build URL command line
if args.distribution == "debian":
	distribution_packages_url = "http://ftp.uk.debian.org/debian/"
elif args.distribution == "ubuntu":
	distribution_packages_url = "http://gb.archive.ubuntu.com/ubuntu/"

#
# Create Database
#
sqlite_database_filepath = args.build_root + "/%s-%s-%s-Packages.db" % (args.distribution, args.distribution_version, args.architecture)
sql_conn = sqlite3.connect(sqlite_database_filepath)
sql_cur = sql_conn.cursor()

packages = args.packages.split(' ')

distribution_root = "%s/%s/%s/" % (args.distribution, args.distribution_version, args.architecture)
try:
	os.makedirs(distribution_root)
except:
	pass

for package in packages:
	sql_cur.execute("SELECT Filename FROM Packages WHERE Name='%s'" % package)
	package_info = sql_cur.fetchone()
	
	if package_info:
		package_file = distribution_root + package + '.deb'
		package_url = distribution_packages_url + package_info[0]
		print "Download package %s" % package_file
		urllib.urlretrieve(package_url, package_file)
		subprocess.call([ "dpkg", "-x", package_file, distribution_root ])
	else:
		print "Cannot find %s" % package

# Fix Symbolic Links
for root, dirs, files in os.walk(distribution_root):
	for file in files:
		if os.path.islink(root + '/' + file) and not os.path.isfile(os.path.realpath(root + '/' + file)):
			original_file = distribution_root + os.path.realpath(root + '/' + file)
			if not os.path.isfile(original_file):
				print "File '%s' does not exist." % os.path.realpath(root + '/' + file)
			else:
				print "%s -> %s" % (root + '/' + file, original_file)
				os.remove(root + '/' + file)
				shutil.copy2(original_file, root + '/' + file)
