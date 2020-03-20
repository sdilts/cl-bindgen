import framework

import cl_bindgen.mangler as mangler
from cl_bindgen.processfile import ProcessOptions, process_file
import cl_bindgen.util as util

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
                             constant_manglers=constant_manglers)
    return options

def make_gen_fn():
    options = make_default_options()
    def gen_fn(inputfile, outputfile):
        options.output = outputfile
        process_file(inputfile, options)
    return gen_fn

tests = [
    ('simple_struct.h', 'outputs/simple-struct.lisp', {}),
    ('nested_struct.h', 'outputs/nested-struct.lisp', {})
]
