# it would probably be better to use an class instead of a series of functions
# so that the output file can be specified easier, but we don' need that
# yet

import sys

def _emit_message(level_string, messages, location, sep, end):
    sys.stderr.write(level_string)
    iterator = iter(messages)
    val = next(iterator, None)
    if val is not None:
        sys.stderr.write(val)
    for val in iterator:
        sys.stderr.write(sep)
        sys.stderr.write(val)
    if location is not None:
        sys.stderr.write(f' at {location.file}:{location.line}:{location.column}')
    sys.stderr.write(end)
    sys.stderr.flush()

def warn(*messages, location=None, sep='\n ', end='\n'):
    _emit_message('WARNING: ', messages, location, sep, end)

def error(*messages, location=None, sep='\n ', end='\n'):
    _emit_message('ERROR: ', messages, location, sep, end)
