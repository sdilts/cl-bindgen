import framework
from framework import TestOptions
import os
import shutil

import cl_bindgen.mangler as mangler
from cl_bindgen.processfile import ProcessOptions, process_file
import cl_bindgen.util as util
from cl_bindgen.macro_util import macro_matches_file_path

def make_gen_fn():
    options = util.build_default_options()
    if clang_dir := util.find_clang_resource_dir():
        options.arguments.append('-I' + clang_dir)
    else:
        print('WARNING: Could not find clang include directory. It must be manually added as a clang argument', file=sys.stderr)

    def gen_fn(inputfile, outputfile):
        options.output = outputfile
        process_file(inputfile, options)
    return gen_fn

tests = [
    ('inputs/simple_struct.h', 'outputs/simple-struct.lisp', {}),
    ('inputs/nested_struct.h', 'outputs/nested-struct.lisp', {}),
    ('inputs/function_pointer.h', 'outputs/function-pointer.lisp', {}),
    ('inputs/macro_constant.h', 'outputs/macro-constant.lisp', {}),
    ('inputs/header_guard.h', 'outputs/header-guard.lisp', {}),
    ('inputs/header_guard_path.h', 'outputs/header-guard-path.lisp', {}),
    ('inputs/macro_constant_invalid.h', 'outputs/macro-constant-invalid.lisp', {}),
    ('inputs/nested_anonymous_records.h', 'outputs/nested-anonymous-records.lisp', {}),
    ('inputs/builtin_pointers.h', 'outputs/builtin-pointers.lisp', {}),
    ('inputs/typedef.h', 'outputs/typedef.lisp', {}),
    ('inputs/constant_array_in_struct.h', 'outputs/constant-array-in-struct.lisp', {}),
    ('inputs/standard_types.h', 'outputs/standard_types.lisp', {}),
    ('inputs/forward_declaration.h', 'outputs/forward_declaration.lisp', {}),
    ('inputs/capitalization.h', 'outputs/capitalization.lisp', {})
]

def test_file_generation():
    cur_dir = os.getcwd()
    file_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(file_dir)

    output_dir = ".output"
    success = framework.run_tests(tests, make_gen_fn(), output_dir, os.sys.stdout)
    if success:
        shutil.rmtree(".output")

    os.chdir(cur_dir)
    return success

if __name__ == "__main__":
    success = test_file_generation()
    if success:
        exit(0)
    else:
        exit(1)
