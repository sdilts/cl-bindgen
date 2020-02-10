import sys

from cl_bindgen.processfile import ProcessOptions
import cl_bindgen.mangler as mangler
import cl_bindgen.util as util

def main():
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
    # typdef manglers are applied to typdefs
    typedef_manglers = [u_mangler]
    constant_manglers = [u_mangler, const_mangler]

    options = ProcessOptions(typedef_manglers=typedef_manglers,
                             enum_manglers=enum_manglers,
                             type_manglers=type_manglers,
                             name_manglers=name_manglers,
                             constant_manglers=constant_manglers)
    util.dispatch_from_arguments(sys.argv[1:], options)

if __name__ == "__main__":
    main()
