import argparse
import sys
import processfile

import processfile

def process_batch_file(batchfile, manglers):
    return 0

def arg_batch_files(arguments, manglers):
    """ Perform the actions described in batch_files using the given manglers """
    for batch_file in arguments.inputs:
        processfile.process_batch_file(batch_file, manglers)

def arg_process_files(arguments, manglers):
    """ Process the files using the given parsed arguments and manglers """
    output = arguments.output
    if output == ":stdout":
        output = sys.stdout
    elif output == ":stderr":
        output = sys.stderr
    else:
        # TODO: do something intellegent here:
        raise Exception("Not implemented")

    # TODO: figure out how to unpack the manglers:

    processor = processfile.FileProcessor(output)

    # Add '-I' to the includes so clang understands them:
    includes = ['-I ' + item for item in arguments.includes]
    for f in arguments.inputs:
        processor.process_file(f, includes)

def dispatch_from_arguments(arguments, manglers):
    """ Use the given arguments and manglers to perform the main task of cl-bindgen """
    parser = argparse.ArgumentParser()

    parser.add_argument('--version',action='version',
                        version='CL-BINDGEN 0.1.0',
                        help="Print the version information")

    subparsers = parser.add_subparsers()

    batch_parser = subparsers.add_parser('batch', aliases=['b'],
                                         help="Process files using specification files",
                                         description="Instead of specifying options on the command line, .yaml files can be used to specify options and input files")
    batch_parser.add_argument('inputs', nargs='+',
                              metavar='batch files',
                              help="The batch files to process")
    batch_parser.set_defaults(func=arg_batch_files)


    process_parser = subparsers.add_parser('files',aliases=['f'],
                                           help="Specify options and files on the command line")
    process_parser.add_argument('inputs',nargs='+',
                                metavar="input files",
                                help="The input files to cl-bindgen")
    process_parser.add_argument('-o', default=sys.stdout,
                                metavar='output',
                                dest='output',
                                help="Specify where to place the generated output.")
    process_parser.add_argument('-I',
                                metavar='include directories',
                                dest='includes',
                                default=[],
                                help="Specify include directories to be passed to libclang",
                                action='append')
    process_parser.set_defaults(func=arg_process_files)

    args = parser.parse_args()
    return args.func(args, manglers)


if __name__ == "__main__":
    import sys
    manglers = dict()
    dispatch_from_arguments(sys.argv[1:], manglers)
