import argparse
import sys
import io
import copy
from dataclasses import dataclass, field
import typing

import processfile

@dataclass
class ProcessOptions:
    typedef_manglers: list = field(default_factory=lambda: [])
    enum_manglers: list = field(default_factory=lambda: [])
    type_manglers: list = field(default_factory=lambda: [])
    name_manglers: list = field(default_factory=lambda: [])
    constant_manglers: list = field(default_factory=lambda: [])

    output: typing.IO = field(default_factory=lambda: sys.stdout)
    package : str = None
    arguments: list = field(default_factory=lambda: [])

    def __copy__(self, memo=None):
        return ProcessOptions(list(self.typedef_manglers),
                              list(self.enum_manglers),
                              list(self.type_manglers),
                              list(self.name_manglers),
                              list(self.constant_manglers),
                              output=self.output,
                              package=copy.copy(self.package),
                              arguments=copy.copy(self.arguments))

def processor_from_options(optiondata):
    return processfile.FileProcessor(optiondata.output,
                         enum_manglers=optiondata.enum_manglers,
                         type_manglers=optiondata.type_manglers,
                         name_manglers=optiondata.name_manglers,
                         typedef_manglers=optiondata.typedef_manglers,
                         constant_manglers=optiondata.constant_manglers)

def _add_args_to_option(option, args):
    if args.output:
        if args.output == ":stdout":
            option.output = sys.stdout
        elif args.output == ":stderr":
            option.output = sys.stderr
        else: # not isinstance(args.output, io.IOBase):
            # TODO: do something intellegent here:
            print(args.output)
            raise Exception("Not implemented")
    if args.includes:
        for item in args.includes:
            option.arguments.append('-I')
            option.arguments.append(item)
    if args.package:
        option.package = args.package

def process_batch_file(batchfile, options):
    """ Perform the actions specified in the batch file with the given base options

    If options are specified in the batch file that override the options given, those
    options will be used instead.
    """

    return 0

def _arg_batch_files(arguments, options):
    """ Perform the actions described in batch_files using the given manglers """

    for batch_file in arguments.inputs:
        processfile.process_batch_file(batch_file, options)

def _arg_process_files(arguments, options):
    """ Process the files using the given parsed arguments and options """

    processor = processor_from_options(options)

    if options.package:
        output_package_include(options.output, options.package)

    for f in arguments.inputs:
        processor.process_file(f, options.arguments)

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

    # We modify options, so copy it so the argument isn't affected:
    options = copy.copy(options)

    parser = _build_parser()

    args = parser.parse_args(arguments)
    _add_args_to_option(options, args)

    return args.func(args, options)


if __name__ == "__main__":
    options = ProcessOptions()
    dispatch_from_arguments(sys.argv[1:], options)
