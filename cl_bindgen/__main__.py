import sys

import cl_bindgen.processfile as processfile
import cl_bindgen.mangler as mangler

def main():
    if len(sys.argv) < 2:
        print(f"Not enough arguments: {len(sys.argv)} given", file=sys.stderr)
        exit(1)

    u_managler =  mangler.UnderscoreMangler()
    k_mangler =   mangler.KeywordMangler()
    wlr_mangler = mangler.PrefixMangler("wlr_", "wlr:")
    wl_mangler =  mangler.PrefixMangler("wl_", "wl:")
    const_mangler = mangler.ConstantMangler()

    # manglers are applied in the order that they are given in these lists:
    # enum manglers transform enum fields, e.g. FOO, BAR in enum { FOO, BAR }
    enum_manglers = [k_mangler, u_managler]
    # type mangers are applied to struct names, function names, and type names
    type_managlers = [wl_mangler, wlr_mangler, u_managler]
    # name manglers are applied to parameters and variables
    name_managlers = [u_managler]
    # typdef manglers are applied to typdefs
    typedef_manglers = [k_mangler, u_managler]
    constant_manglers = [wl_mangler, wlr_mangler, u_managler, const_mangler]
    processor = processfile.FileProcessor(sys.stdout,
                                          enum_manglers=enum_manglers,
                                          type_manglers=type_managlers,
                                          name_manglers=name_managlers,
                                          typedef_manglers=typedef_manglers,
                                          constant_manglers=constant_manglers)

    processor.process_file(sys.argv[1], args=sys.argv[2:1])

if __name__ == "__main__":
    main()
