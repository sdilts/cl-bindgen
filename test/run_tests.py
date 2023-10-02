import framework
from framework import TestOptions
import os
import shutil

import cl_bindgen.mangler as mangler
from cl_bindgen.processfile import ProcessOptions, process_file
import cl_bindgen.util as util
from cl_bindgen.macro_util import macro_matches_file_path

def make_default_options():
    u_mangler =  mangler.UnderscoreMangler()
    k_mangler =   mangler.KeywordMangler()
    const_mangler = mangler.ConstantMangler()

    # manglers are applied in the order that they are given in these lists:
    # enum manglers transform enum fields, e.g. FOO, BAR in enum { FOO, BAR }
    enum_manglers = [k_mangler, u_mangler]
    # type mangers are applied to struct names, function names, and type names
    type_manglers = [u_mangler]
    # name manglers are applied to parameters and variables
    name_manglers = [u_mangler]
    # typedef manglers are applied to typedefs
    typedef_manglers = [u_mangler]
    constant_manglers = [u_mangler, const_mangler]

    options = ProcessOptions(typedef_manglers=typedef_manglers,
                             enum_manglers=enum_manglers,
                             type_manglers=type_manglers,
                             name_manglers=name_manglers,
                             constant_manglers=constant_manglers,
                             macro_detector=macro_matches_file_path)
    return options

def make_gen_fn():
    options = make_default_options()
    def gen_fn(inputfile, outputfile):
        options.output = outputfile
        process_file(inputfile, options)
    return gen_fn

tests = [
    ('inputs/simple_struct.h', 'outputs/simple-struct.lisp', {}),
    ('inputs/nested_struct.h', 'outputs/nested-struct.lisp', {}),
    ('inputs/function_pointer.h', 'outputs/function-pointer.lisp', {}),
    ('inputs/macro_constant.h', 'outputs/macro_constant.lisp', {}),
    ('inputs/header_guard.h', 'outputs/header_guard.lisp', {}),
    ('inputs/header_guard_path.h', 'outputs/header_guard_path.lisp', {})
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
