import re
import sys
from pathlib import Path

def macro_matches_file_path(location: str, name: str):
    location_path = Path(location)
    parent_name = '_'.join([g.name for g in location_path.parents]) + name.replace('.', '_')
    return parent_name.upper().endswith(name.upper())

def is_header_guard(cursor, detector_fn):
    if not detector_fn:
        return False

    location = cursor.location
    macro_name = cursor.spelling
    return detector_fn(location.file.name, macro_name)


class LiteralConversionError(Exception):
    pass

def convert_literal_token(token):
    if token.spelling.startswith('0x'):
        try:
            val = int(token.spelling, 0)
            return f'#x{val:x}'
        except Exception as e:
            print('could not parse int', token.spelling, e, file = sys.stderr)
            raise LiteralConversionError()
    if re.fullmatch('"(.*)"|([0-9]*\.{0,1}[0-9]*)', token.spelling):
        return token.spelling
    else:
        raise LiteralConversionError()
