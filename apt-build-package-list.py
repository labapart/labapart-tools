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
#	../tools/apt-build-package-list.py debian jessie amd64 $PWD
#	../tools/apt-build-package-list.py ubuntu trusty amd64 $PWD

import argparse
import gzip
import os
import sqlite3
import urllib

parser = argparse.ArgumentParser(description='Build package list for Linux Distribution.')
parser.add_argument('distribution', choices=['debian', 'ubuntu'], help='Linux distribution')
parser.add_argument('distribution_version', type=str, help='Linux distribution')
parser.add_argument('architecture', choices=['amd64', 'arm64'], help='CPU Architecture')
parser.add_argument('build_root', type=str, help='Location to store the Linux Distribution package.')
args = parser.parse_args()

# Build URL command line
if args.distribution == "debian":
	distribution_packages_url = "http://ftp.uk.debian.org/debian/dists/%s/main/binary-%s/Packages.gz" % (args.distribution_version, args.architecture)
elif args.distribution == "ubuntu":
	distribution_packages_url = "http://gb.archive.ubuntu.com/ubuntu/dists/%s/main/binary-%s/Packages.gz" % (args.distribution_version, args.architecture)

#
# Create Database
#
sqlite_database_filepath = args.build_root + "/%s-%s-%s-Packages.db" % (args.distribution, args.distribution_version, args.architecture)
if os.path.isfile(sqlite_database_filepath):
	os.remove(sqlite_database_filepath)
sql_conn = sqlite3.connect(sqlite_database_filepath)
sql_cur = sql_conn.cursor()
sql_cur.execute("CREATE TABLE Packages(ID integer primary key autoincrement, Name, Version, Filename, Dependencies)")

# Generate the file for the Linux Distribution Packages
distribution_packages_local_file = args.build_root + "/%s-%s-%s-Packages.gz" % (args.distribution, args.distribution_version, args.architecture)

print "Download file %s" % distribution_packages_url
urllib.urlretrieve(distribution_packages_url, distribution_packages_local_file)
print "Decompress file %s" % distribution_packages_local_file
with gzip.open(distribution_packages_local_file, 'rb') as fp:
	line = fp.readline().strip()
	while line:
		if line.startswith('Package:'):
			package_name = line[9:]
			line = fp.readline().strip()
			while line and (len(line) > 0):
				if line.startswith('Version:'):
					package_version = line[9:]
				if line.startswith('Depends:'):
					package_dependency = line[9:]
				else:
					package_dependency = None
				if line.startswith('Filename:'):
					package_filename = line[10:]
				line = fp.readline().strip()

			sql_cur.execute("INSERT INTO Packages (Name, Version, Filename, Dependencies) VALUES (?,?,?,?)", (package_name, package_version, package_filename, package_dependency))

			# End of file
			if line is None:
				break

		line = fp.readline().strip()

sql_conn.commit()
		
sql_cur.close()
