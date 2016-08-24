#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
getSeqENA.py - Get fastq files from ENA using Run IDs
<https://github.com/B-UMMI/getSeqENA/>

Copyright (C) 2016 Miguel Machado <mpmachado@medicina.ulisboa.pt>

Last modified: August 22, 2016

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import os
import download
import sys
import utils
import time

version = '0.4'


def requiredPrograms(args):
	programs_version_dictionary = {}
	if args.asperaKey is not None:
		programs_version_dictionary['ascp'] = ['--version', '>=', '3.6.1']
	missingPrograms = utils.checkPrograms(programs_version_dictionary)
	if len(missingPrograms) > 0:
		sys.exit('\n' + 'Errors:' + '\n' + '\n'.join(missingPrograms))


def runGetSeqENA(args):
	start_time = time.time()

	listRunIDs = utils.getListIDs(os.path.abspath(args.listRunIDs.name))
	outdir = os.path.abspath(args.outdir)
	utils.check_create_directory(outdir)
	asperaKey = args.asperaKey
	if asperaKey is not None:
		asperaKey = os.path.abspath(asperaKey.name)
	downloadLibrariesType = args.downloadLibrariesType

	# Start logger
	logfile = utils.start_logger(outdir)

	# Get general information
	utils.general_information(logfile, version)

	# Check programms
	requiredPrograms(args)

	runs_successfully = 0
	with open(os.path.join(outdir, 'getSeqENA.samples_with_problems.txt'), 'wt') as samples_with_problems:
		for run_id in listRunIDs:
			if args.maximumSamples is None:
				maximumSamples = runs_successfully + 1
			else:
				maximumSamples = args.maximumSamples

			if runs_successfully < maximumSamples:
				print '\n' + 'Download RunID ' + run_id
				pairedOrSingle, downloadedFiles = download.runDownload(run_id, outdir, asperaKey, downloadLibrariesType)
				if pairedOrSingle == args.downloadLibrariesType or (args.downloadLibrariesType is None and pairedOrSingle is not None):
					runs_successfully += 1
				else:
					utils.removeDirectory(os.path.join(outdir, run_id))
					print run_id + ' was not downloaded'
					samples_with_problems.write(run_id + '\n')
			else:
					break

	time_taken = utils.runTime(start_time)
	del time_taken

	if runs_successfully == 0:
		sys.exit('No RunIDs were successfully downloaded!')


def main():

	parser = argparse.ArgumentParser(prog='getSeqENA.py', description="Get fastq files from ENA using Run IDs", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--version', help='Version information', action='version', version=str('%(prog)s v' + version))

	parser_required = parser.add_argument_group('Required options')
	parser_required.add_argument('-l', '--listRunIDs', type=argparse.FileType('r'), metavar='/path/to/list/RunIDs.txt', help='Path to list containing the RunIDs to be downloaded', required=True)

	parser_optional = parser.add_argument_group('Facultative options')
	parser_optional.add_argument('-o', '--outdir', type=str, metavar='/output/directory/', help='Path for output directory', required=False, default='.')
	parser_optional.add_argument('-a', '--asperaKey', type=argparse.FileType('r'), metavar='/path/to/asperaweb_id_dsa.openssh', help='Tells analyseSero38.py to download fastq files from ENA using Aspera Connect. With this option, the path to Private-key file asperaweb_id_dsa.openssh is provided (normaly found in ~/.aspera/connect/etc/asperaweb_id_dsa.openssh).', required=False)
	parser_optional.add_argument('--downloadLibrariesType', type=str, metavar='PE', help='Tells getSeqENA.py to only download files from PE or SE libraries', choices=['PE', 'SE'], required=False)
	parser_optional.add_argument('--maximumSamples', type=int, metavar='N', help='Tells getSeqENA.py to only download files for N samples', required=False)

	parser.set_defaults(func=runGetSeqENA)

	args = parser.parse_args()

	args.func(args)


if __name__ == "__main__":
	main()
