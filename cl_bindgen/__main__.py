import sys

import cl_bindgen.util as util

def main():
    options = util.build_default_options()
    util.dispatch_from_arguments(sys.argv[1:], options)

if __name__ == "__main__":
    main()
