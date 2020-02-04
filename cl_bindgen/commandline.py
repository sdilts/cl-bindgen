import argparse
import sys
import io
import copy
import yaml

import processfile
from processfile import ProcessOptions


def _add_args_to_option(option, args):
    """ Return a new option object with the options specified by `args` and based on 'option' """
    option = copy.copy(option)
    if args.output:
        option.output = args.output
    if args.includes:
        for item in args.includes:
            option.arguments.append('-I')
            option.arguments.append(item)
    if args.package:
        option.package = args.package
    return option

def process_batch_file(batchfile, options):
    """ Perform the actions specified in the batch file with the given base options

    If options are specified in the batch file that override the options given, those
    options will be used instead.
    """

    return 0

def _arg_batch_files(arguments, options):
    """ Perform the actions described in batch_files using `options` as the defaults """

    for batch_file in arguments.inputs:
        processfile.process_batch_file(batch_file, options)

def _arg_process_files(arguments, options):
    """ Process the files using the given parsed arguments and options """

    options = _add_args_to_option(options, arguments)
    try:
        processfile.process_files(arguments.inputs, options)
    except FileNotFoundError as err:
        print(f"Error: File {err.strerror} not found. Exiting with completed work.",
              file=sys.stderr)
        exit(err.errno)
    except IsADirectoryError as err:
        print(f"Error: {err.strerror} is a directory. Exiting with completed work.",
              file=sys.stderr)
        exit(err.errno)

def _build_parser():
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
    batch_parser.set_defaults(func=_arg_batch_files)


    process_parser = subparsers.add_parser('files',aliases=['f'],
                                           help="Specify options and files on the command line")
    process_parser.add_argument('inputs',nargs='+',
                                metavar="input files",
                                help="The input files to cl-bindgen")
    process_parser.add_argument('-o',
                                metavar='output',
                                dest='output',
                                help="Specify where to place the generated output.")
    process_parser.add_argument('-I',
                                metavar='include directories',
                                dest='includes',
                                default=[],
                                help="Specify include directories to be passed to libclang",
                                action='append')
    process_parser.add_argument('-p',
                                metavar='package',
                                dest='package',
                                help="Output an in-package form with the given package at the top of the output")
    process_parser.set_defaults(func=_arg_process_files)
    return parser

def dispatch_from_arguments(arguments, options):
    """ Use the given arguments and manglers to perform the main task of cl-bindgen """

    parser = _build_parser()

    if not len(arguments) > 1:
        parser.print_help()
        exit(1)

    args = parser.parse_args(arguments)

    return args.func(args, options)


if __name__ == "__main__":
    options = ProcessOptions()
    dispatch_from_arguments(sys.argv[1:], options)
