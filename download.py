import ftplib
import glob
import shutil
import os
import utils


filesExtensions = ['fastq.gz', 'fq.gz']
pairEnd_file = ['_1.f', '_2.f']


def ftpListFiles(ftp, link):
	ftp.cwd(link)
	dirs = ftp.nlst()

	files = []

	for item in dirs:
		files.append(item)

	if len(files) == 0:
		files = None

	return files


def ftpSearchFileTypes(files, libraryType):
	files_to_download = []
	if files is not None:
		if len(files) == 1 and (libraryType is None or libraryType == 'SE'):
			for extensions in filesExtensions:
				if extensions in files[0]:
					files_to_download.append(files[0])
					break
		elif len(files) > 1 and (libraryType is None or libraryType == 'PE'):
			for file_ena in files:
				for extensions in filesExtensions:
					if extensions in file_ena:
						for pairEnd_file_number in pairEnd_file:
							if pairEnd_file_number in file_ena:
								files_to_download.append(file_ena)
								break
						break
	if len(files_to_download) == 0:
		files_to_download = None

	return files_to_download


def getFilesList(runID, libraryType):
	run_successfully = False

	partial_tid = runID[0:6]

	files = None

	try:
		f = ftplib.FTP('ftp.sra.ebi.ac.uk', timeout=3600)
		f.login()
	except Exception as e:
		print 'It was not possible to connect to ENA!'
		print e
	else:
		link = '/vol1/fastq/' + partial_tid + '/' + runID
		try:
			files = ftpListFiles(f, link)
		except:
			print 'The link ' + link + ' did not work. Trying a different one...'
			link = '/vol1/fastq/' + partial_tid + "/00" + runID[-1] + '/' + runID
			print '... ' + link
			try:
				files = ftpListFiles(f, link)
			except Exception as e:
				print e
				print link
			else:
				run_successfully = True
		else:
			run_successfully = True

		try:
			f.quit()
		except Exception as e:
			print e

	files = ftpSearchFileTypes(files, libraryType)

	return run_successfully, files


def download(dirs2, target_dir2, ref2, success2, f2, link2, libraryType):
	insucess = 0

	print 'Get files list from ENA...'
	files = ftpListFiles(f2, link2)
	files = ftpSearchFileTypes(files, libraryType)

	if files is not None:
		for item in files:

			try:
				f2.cwd(link2)
				final_target_dir = target_dir2 + "/" + item
				file = open(final_target_dir, 'wb')
				print "Downloading: %s" % item

				f2.retrbinary('RETR %s' % item, file.write)
				file.close()
				print "Downloaded %s" % item
				success2 += 1
			except Exception as e:
				print e
				insucess += 1

	return success2, insucess


def download_ERR(ERR_id, target_dir, libraryType):
	ref = ERR_id
	failed = 0
	success = 0
	insucess = 0

	try:
		f = ftplib.FTP('ftp.sra.ebi.ac.uk', timeout=3600)
		f.login()

		try:

			firstid = ref[0:6]
			# get the read files name from the reference id
			link = '/vol1/fastq/' + firstid + "/" + ref
			f.cwd(link)
			dirs = f.nlst()

		except:
			try:
				firstid = ref[0:6]
				# get the read files name from the reference id
				link = '/vol1/fastq/' + firstid + "/00" + ref[-1] + "/" + ref
				f.cwd(link)
				dirs = f.nlst()
			except Exception as e:
				failed += 1
				print "Bad ID: " + ref
			else:
				success, insucess = download(dirs, target_dir, ref, success, f, link, libraryType)
		else:
			success, insucess = download(dirs, target_dir, ref, success, f, link, libraryType)
		try:
			f.quit()
		except Exception as e:
			print e
			print 'Insucess: ' + str(insucess)
	except Exception as e:
		print e

	print "Downloaded %s files successfully, %s fail and %s ID references were wrong" % (success, insucess, failed)
	return success, insucess


def aspera(run_id, asperaKey, outdir, fileToDownload):
	if fileToDownload is None:
		fileToDownload = ''
	else:
		fileToDownload = '/' + fileToDownload

	aspera_command = ['ascp', '-QT', '-l', '300m', '-i', asperaKey, '', outdir]
	aspera_command[6] = str('era-fasp@fasp.sra.ebi.ac.uk:/vol1/fastq/' + run_id[0:6] + '/' + run_id + fileToDownload)
	run_successfully, stdout, stderr = utils.runCommandPopenCommunicate(aspera_command, False, 3600)
	if not run_successfully:
		print 'It was not possible to download! Trying again:'
		aspera_command[6] = str('era-fasp@fasp.sra.ebi.ac.uk:/vol1/fastq/' + run_id[0:6] + '/00' + run_id[-1] + '/' + run_id + fileToDownload)
		run_successfully, stdout, stderr = utils.runCommandPopenCommunicate(aspera_command, False, 3600)

	return run_successfully


# Download using Aspera Connect
def downloadAspera(run_id, outdir, asperaKey, getAllFiles_Boolean, filesToDownload):
	run_successfully = False

	if getAllFiles_Boolean:
		run_successfully = aspera(run_id, asperaKey, outdir, None)
		if run_successfully:
			files = glob.glob1(os.path.join(outdir, run_id), '*')
			for file_downloaded in files:
				shutil.move(os.path.join(outdir, run_id, file_downloaded), outdir)
			shutil.rmtree(os.path.join(outdir, run_id))
	else:
		if filesToDownload is not None:
			runs = []
			for file_ena in filesToDownload:
				run_successfully = aspera(run_id, asperaKey, outdir, file_ena)
				runs.append(run_successfully)

			if False in runs:
				run_successfully = False
		else:
			run_successfully = True

	return run_successfully


# Search Fastq files (that were downloaded or already provided by the user)
def searchDownloadedFiles(directory):
	for extension in filesExtensions:
		downloadedFiles = glob.glob1(directory, str('*.' + extension))
		if len(downloadedFiles) > 0:
			break

	downloadFiles_withPath = []
	if len(downloadedFiles) > 0:
		for file_downloaded in downloadedFiles:
			downloadFiles_withPath.append(os.path.abspath(os.path.join(directory, file_downloaded)))

	return downloadFiles_withPath


def runDownload(run_id, target_dir, asperaKey, libraryType):

	if not os.path.isdir(target_dir):
		os.makedirs(target_dir)
	dir_sample = os.path.join(target_dir, run_id)
	if not os.path.isdir(dir_sample):
		os.makedirs(dir_sample)

	# download ERR
	aspera_run = False
	ftp_down_suc = 0
	ftp_down_insuc = 0

	downloadedFiles = searchDownloadedFiles(dir_sample)
	if len(downloadedFiles) < 1:
		if asperaKey is not None:
			print 'Get files list from ENA...'
			run_successfully, files = getFilesList(run_id, libraryType)
			if run_successfully:
				print 'Trying download using Aspera...'
				aspera_run = downloadAspera(run_id, dir_sample, asperaKey, False, files)
			if not aspera_run:
				print 'Trying download using FTP...'
				ftp_down_suc, ftp_down_insuc = download_ERR(run_id, dir_sample, libraryType)
		else:
			print 'Trying download using FTP...'
			ftp_down_suc, ftp_down_insuc = download_ERR(run_id, dir_sample, libraryType)

	else:
		ftp_down_suc = len(downloadedFiles)
		print 'Files for ' + run_id + ' already exists...'

	downloadedFiles = searchDownloadedFiles(dir_sample)

	pairedOrSingle = None

	if (ftp_down_insuc > 0 or ftp_down_suc == 0) and aspera_run is False:
		shutil.rmtree(dir_sample)
		return pairedOrSingle, downloadedFiles

	if len(downloadedFiles) == 2:
		pairedOrSingle = 'PE'
	elif len(downloadedFiles) == 1:
		pairedOrSingle = 'SE'

	return pairedOrSingle, downloadedFiles
