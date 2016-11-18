#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
getSeqENA.py - Get fastq files from ENA using ENA IDs
<https://github.com/B-UMMI/getSeqENA/>

Copyright (C) 2016 Miguel Machado <mpmachado@medicina.ulisboa.pt>

Last modified: November 17, 2016

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

version = '1.0'


def requiredPrograms(args):
	programs_version_dictionary = {}
	if args.asperaKey is not None:
		programs_version_dictionary['ascp'] = ['--version', '>=', '3.6.1']
	if args.downloadCramBam:
		programs_version_dictionary['samtools'] = ['--version', '==', '1.3.1']
	missingPrograms = utils.checkPrograms(programs_version_dictionary)
	if len(missingPrograms) > 0:
		sys.exit('\n' + 'Errors:' + '\n' + '\n'.join(missingPrograms))


def runGetSeqENA(args):
	start_time = time.time()

	listENA_IDs = utils.getListIDs(os.path.abspath(args.listENAids.name))
	outdir = os.path.abspath(args.outdir)
	utils.check_create_directory(outdir)
	asperaKey = args.asperaKey
	if asperaKey is not None:
		asperaKey = os.path.abspath(asperaKey.name)

	# Start logger
	logfile = utils.start_logger(outdir)

	# Get general information
	utils.general_information(logfile, version)

	# Check programms
	requiredPrograms(args)

	runs_successfully = 0
	with open(os.path.join(outdir, 'getSeqENA.report.txt'), 'wt') as writer:
		writer.write('\t'.join(['#ENA_ID', 'run_accession', 'run_successfully', 'downloadedFiles', 'instrument_platform', 'instrument_model', 'library_layout', 'library_source']) + '\n')
		for ena_id in listENA_IDs:
			if args.maximumSamples is None:
				maximumSamples = runs_successfully + 1
			else:
				maximumSamples = args.maximumSamples

			if runs_successfully < maximumSamples:
				print '\n' + 'Download ENA_ID ' + ena_id

				ena_id_folder = os.path.join(outdir, ena_id)
				utils.check_create_directory(ena_id_folder)

				run_successfully, downloadedFiles, sequencingInformation = download.runDownload(ena_id, args.downloadLibrariesType, asperaKey, ena_id_folder, args.downloadCramBam, args.threads, args.downloadInstrumentPlatform)

				if run_successfully:
					runs_successfully += 1
				else:
					utils.removeDirectory(ena_id_folder)
					print ena_id + ' was not downloaded'

				writer.write('\t'.join([ena_id, str(sequencingInformation['run_accession']), str(run_successfully), str(';'.join(downloadedFiles) if downloadedFiles is not None else downloadedFiles), str(sequencingInformation['instrument_platform']), str(sequencingInformation['instrument_model']), str(sequencingInformation['library_layout']), str(sequencingInformation['library_source'])]) + '\n')
			else:
					break

	time_taken = utils.runTime(start_time)
	del time_taken

	if runs_successfully == 0:
		sys.exit('No ENA_IDs were successfully downloaded!')


def main():

	parser = argparse.ArgumentParser(prog='getSeqENA.py', description="Get fastq files from ENA using ENA IDs", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--version', help='Version information', action='version', version=str('%(prog)s v' + version))

	parser_required = parser.add_argument_group('Required options')
	parser_required.add_argument('-l', '--listENAids', type=argparse.FileType('r'), metavar='/path/to/list/ENA_IDs.txt', help='Path to list containing the ENA_IDs to be downloaded', required=True)

	parser_optional = parser.add_argument_group('Facultative options')
	parser_optional.add_argument('-o', '--outdir', type=str, metavar='/output/directory/', help='Path for output directory', required=False, default='.')
	parser_optional.add_argument('-j', '--threads', type=int, metavar='N', help='Number of threads', required=False, default=1)
	parser_optional.add_argument('-a', '--asperaKey', type=argparse.FileType('r'), metavar='/path/to/asperaweb_id_dsa.openssh', help='Tells getSeqENA.py to download fastq files from ENA using Aspera Connect. With this option, the path to Private-key file asperaweb_id_dsa.openssh is provided (normaly found in ~/.aspera/connect/etc/asperaweb_id_dsa.openssh).', required=False)
	parser_optional.add_argument('--downloadLibrariesType', type=str, metavar='PAIRED', help='Tells getSeqENA.py to download files with specific library layout', choices=['PAIRED', 'SINGLE', 'BOTH'], required=False, default='PAIRED')
	parser_optional.add_argument('--downloadCramBam', action='store_true', help='Tells getSeqENA.py to also download cram/bam files and convert them to fastq files')
	parser_optional.add_argument('--downloadInstrumentPlatform', type=str, metavar='ILLUMINA', help='Tells getSeqENA.py to download files with specific library layout', choices=['ILLUMINA', 'ALL'], required=False, default='ILLUMINA')
	parser_optional.add_argument('--maximumSamples', type=int, metavar='N', help='Tells getSeqENA.py to only download files for N samples', required=False)

	parser.set_defaults(func=runGetSeqENA)

	args = parser.parse_args()

	args.func(args)


if __name__ == "__main__":
	main()
