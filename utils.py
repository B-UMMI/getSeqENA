import os
import sys
import shlex
import subprocess
import os.path
import time
import shutil
from threading import Timer
import functools
import traceback
import pickle


def start_logger(workdir):
    sys.stdout = Logger(workdir, time.strftime("%Y%m%d-%H%M%S"))
    logfile = sys.stdout.getLogFile()
    return logfile


class Logger(object):
    def __init__(self, out_directory, time_str):
        self.logfile = os.path.join(out_directory, str('run.' + time_str + '.log'))
        self.terminal = sys.stdout
        self.log = open(self.logfile, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message.encode('utf-8'))
        self.log.flush()

    def flush(self):
        pass

    def getLogFile(self):
        return self.logfile


def general_information(logfile, version):
    # Check if output directory exists

    print '\n' + '==========> getSeqENA <=========='
    print '\n' + 'Program start: ' + time.ctime()

    # Tells where the logfile will be stored
    print '\n' + 'LOGFILE:'
    print logfile

    # Print command
    print '\n' + 'COMMAND:'
    script_path = os.path.abspath(sys.argv[0])
    print sys.executable + ' ' + script_path + ' ' + ' '.join(sys.argv[1:])

    # Print directory where programme was lunch
    print '\n' + 'PRESENT DIRECTORY :'
    present_directory = os.path.abspath(os.getcwd())
    print present_directory

    # Print program version
    print '\n' + 'VERSION:'
    scriptVersionGit(version, present_directory, script_path)

    # Print PATH variable
    print '\n' + 'PATH variable:'
    print os.environ['PATH']


def scriptVersionGit(version, directory, script_path):
    print 'Version ' + version

    try:
        os.chdir(os.path.dirname(script_path))
        command = ['git', 'log', '-1', '--date=local', '--pretty=format:"%h (%H) - Commit by %cn, %cd) : %s"']
        run_successfully, stdout, stderr = runCommandPopenCommunicate(command, False, 15, False)
        print stdout
        command = ['git', 'remote', 'show', 'origin']
        run_successfully, stdout, stderr = runCommandPopenCommunicate(command, False, 15, False)
        print stdout
        os.chdir(directory)
    except:
        print 'HARMLESS WARNING: git command possibly not found. The GitHub repository information will not be obtained.'


def runTime(start_time):
    end_time = time.time()
    time_taken = end_time - start_time
    hours, rest = divmod(time_taken, 3600)
    minutes, seconds = divmod(rest, 60)
    print 'Runtime :' + str(hours) + 'h:' + str(minutes) + 'm:' + str(round(seconds, 2)) + 's'
    return time_taken


# USADO
def check_create_directory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)


def kill_subprocess_Popen(subprocess_Popen, command):
    print 'Command run out of time: ' + str(command)
    subprocess_Popen.kill()


def runCommandPopenCommunicate(command, shell_True, timeout_sec_None, print_comand_True):
    run_successfully = False
    if not isinstance(command, basestring):
        command = ' '.join(command)
    command = shlex.split(command)

    if print_comand_True:
        print 'Running: ' + ' '.join(command)

    if shell_True:
        command = ' '.join(command)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    else:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    not_killed_by_timer = True
    if timeout_sec_None is None:
        stdout, stderr = proc.communicate()
    else:
        timer = Timer(timeout_sec_None, kill_subprocess_Popen, args=(proc, command,))
        timer.start()
        stdout, stderr = proc.communicate()
        timer.cancel()
        not_killed_by_timer = timer.isAlive()

    if proc.returncode == 0:
        run_successfully = True
    else:
        if not print_comand_True and not_killed_by_timer:
            print 'Running: ' + str(command)
        if len(stdout) > 0:
            print 'STDOUT'
            print stdout.decode("utf-8")
        if len(stderr) > 0:
            print 'STDERR'
            print stderr.decode("utf-8")
    return run_successfully, stdout, stderr


# Remove directory
def removeDirectory(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)


# USADO
def getListIDs(fileListIDs):
    list_ids = []

    with open(fileListIDs, 'rtU') as lines:
        for line in lines:
            line = line.splitlines()[0]
            if len(line) > 0:
                list_ids.append(line)

    if len(list_ids) == 0:
        sys.exit('No runIDs were found in ' + fileListIDs)

    return list_ids


# Check programs versions
def checkPrograms(programs_version_dictionary):
    print '\n' + 'Checking dependencies...'
    programs = programs_version_dictionary
    which_program = ['which', '']
    listMissings = []
    for program in programs:
        which_program[1] = program
        run_successfully, stdout, stderr = runCommandPopenCommunicate(which_program, False, None, False)
        if not run_successfully:
            listMissings.append(program + ' not found in PATH.')
        else:
            if programs[program][0] is None:
                print program + ' (impossible to determine programme version) found at: ' + stdout.splitlines()[0]
            else:
                check_version = [stdout.splitlines()[0], programs[program][0]]
                run_successfully, stdout, stderr = runCommandPopenCommunicate(check_version, False, None, False)
                if stdout == '':
                    stdout = stderr
                if program == 'bunzip2':
                    version_line = stdout.splitlines()[0].rsplit(',', 1)[0].split(' ')[-1]
                elif program in ['wget', 'awk']:
                    version_line = stdout.splitlines()[0].split(' ', 3)[2]
                elif program in ['prefetch', 'fastq-dump']:
                    version_line = stdout.splitlines()[1].split(' ')[-1]
                else:
                    version_line = stdout.splitlines()[0].split(' ')[-1]
                replace_characters = ['"', 'v', 'V', '+', ',']
                for i in replace_characters:
                    version_line = version_line.replace(i, '')
                print program + ' (' + version_line + ') found'
                if programs[program][1] == '>=':
                    program_found_version = version_line.split('.')
                    program_version_required = programs[program][2].split('.')
                    if float('.'.join(program_found_version[0:2])) < float('.'.join(program_version_required[0:2])):
                        listMissings.append('It is required ' + program + ' with version ' + programs[program][1] + ' ' + programs[program][2])
                    elif float('.'.join(program_found_version[0:2])) == float('.'.join(program_version_required[0:2])):
                        if len(program_version_required) == 3:
                            if len(program_found_version) == 2:
                                program_found_version.append(0)
                            if program_found_version[2].split('_')[0] < program_version_required[2]:
                                listMissings.append('It is required ' + program + ' with version ' + programs[program][1] + ' ' + programs[program][2])
                else:
                    if version_line != programs[program][2]:
                        listMissings.append('It is required ' + program + ' with version ' + programs[program][1] + ' ' + programs[program][2])
    return listMissings


def trace_unhandled_exceptions(func):
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            print 'Exception in ' + func.__name__
            traceback.print_exc()
    return wrapped_func


def saveVariableToPickle(variableToStore, outdir, prefix):
    pickleFile = os.path.join(outdir, str(prefix + '.pkl'))
    with open(pickleFile, 'wb') as writer:
        pickle.dump(variableToStore, writer)


def extractVariableFromPickle(pickleFile):
    with open(pickleFile, 'rb') as reader:
        variable = pickle.load(reader)
    return variable


def rchop(string, ending):
    if string.endswith(ending):
        string = string[:-len(ending)]
    return string


def timer(function, name):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        print('\n' + 'RUNNING {0}\n'.format(name))
        start_time = time.time()

        results = list(function(*args, **kwargs))  # guarantees return is a list to allow .insert()

        time_taken = runTime(start_time)
        print('END {0}'.format(name))

        results.insert(0, time_taken)
        return results
    return wrapper
