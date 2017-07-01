#!/bin/bash

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

# Get all the broken symbolic links
SYMLINKS=`find $TARGETDIR -type l ! -exec test -e {} \; -print`

for S in $SYMLINKS; do
	echo "Fixing symlink $S"
	ORIGINAL_FILE=`ls -l $S | awk '{print $11}'`

	# Replace symlink by original file
	#rm $S
	#cp $TARGETDIR/$ORIGINAL_FILE $S
	echo "$PWD/$TARGETDIR/$ORIGINAL_FILE -> $S"
done
