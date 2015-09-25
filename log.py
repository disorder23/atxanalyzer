__version__ = '1.0'

import datetime
import traceback
import warnings

filename = 'log.txt'


def _write(text, level=None, timestamp=True, stdout=True):
	f = open(filename, 'a')

	lines = text.split('\n')
	lines = [i.strip() for i in lines]

	if level:
		lines = [level + ': ' + i for i in lines]
	#endif

	if timestamp:
		t = datetime.datetime.now()
		time_str = str(t)
		if t.microsecond == 0: time_str += '.000000'

		lines = [time_str + ': ' + i for i in lines]
	#endif

	lines = [i + '\n' for i in lines]

	f.writelines(lines)
	f.flush()

	if stdout:
		for i in lines: print i,
	#endif

	f.close()
#enddef


def critical(text, timestamp=True, stdout=True):
	_write(text, 'CRITICAL', timestamp, stdout)
#enddef


def error(text, timestamp=True, stdout=True):
	_write(text, 'ERROR', timestamp, stdout)
#enddef


def warning(text, timestamp=True, stdout=True):
	_write(text, 'WARNING', timestamp, stdout)
#enddef


def info(text, timestamp=True, stdout=True):
	_write(text, 'INFO', timestamp, stdout)
#enddef


def debug(text, timestamp=True, stdout=True):
	_write(text, 'DEBUG', timestamp, stdout)
#enddef


def exception(text, timestamp=True, stdout=True):
	error(text + '\n' + traceback.format_exc(), timestamp, stdout)
#enddef


def log(text, timestamp=True, stdout=True):
	warnings.warn('log.log() is deprecated', DeprecationWarning)
	_write(text, None, timestamp, stdout)
#enddef


# TODO: what is the correct level for this?
def log_exc(timestamp=True, stdout=True):
	_write(traceback.format_exc(), None, timestamp, stdout)
#enddef


def log_exception(t, v, tb):
	_write(''.join(traceback.format_exception(t, v, tb)), 'CRITICAL')
#enddef
