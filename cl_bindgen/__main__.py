import sys

from cl_bindgen.processfile import ProcessOptions
from cl_bindgen.macro_util import macro_matches_file_path
import cl_bindgen.mangler as mangler
import cl_bindgen.util as util

def main():
    options = util.build_default_options()
    util.dispatch_from_arguments(sys.argv[1:], options)

if __name__ == "__main__":
    main()
