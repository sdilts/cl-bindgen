# CL-bindgen

A command line tool and library for creating common lisp language bindings
from C header files

## Processing individual files
To process individual files, use the `f` command and specify one or
more files to process. By default, output will be printed to
stdout, but the output file can be specified with the `-o` option.

``` bash
# Process test.h and print the results to stdout:
cl-bindgen f test.h
# Process the files test1.h, test2.h, and place the output in
output.lisp:
cl-bindgen f -o output.lisp test1.h test2.h
```

## Batch file processing
CL-bindgen can use a yaml file to process many header
files with a single invocation. You are also able to specify
options that aren't available on the command line. Use the `b` command
to specify one or more batch files to process:

``` bash
cl-bindgen b my_library.yaml
```

### Batch file format
Each yaml document corresponds to one output file.
Examples can be found in the test directory.

Required Fields:
+ output: where to place the generated code
+ files: a list of files to process
Optional Fields:
+ package: The name of the Common Lisp package of the generated file

## Customizing generated symbols
CL-bindgen attempts to reasonably translate C style names into lisp
ones, but there are a few cases that the default configuration makes
no attempt to handle. In those cases, it is possible to use cl-bindgen
as a python library to manually specify how C names are translated
into lisp symbols.

### Transforming C Names

CL-bindgen uses a set of classes called manglers to translate C
names so that they follow lisp naming conventions. Each mangler class
provides one or more tranformations to a symbol. For example, the
`UnderscoreMangler` converts underscores (`_`) into dashes
(`-`). A series of manglers are applied to each C name to translate it
into an lisp symbol.

To maximize customization, a set of manglers is associated with each
type of name that can be converted. Enums, variable names, typedefs,
constants, and record types all use a different set of manglers.

Mangler classes follow a simple interface:
+ `can_mangle(string)`: returns true if the mangler can perform its
  operations on the given string
+ `mangle(string)`: returns a string with the desired tranformations
  applied to its argument.

See [cl_bindgen/manglers.py](docs/manglers] for a full list of provided
manglers and their documentation.

### Using the library

The simplest way to use the library is to copy the file at
./examples/template.py and customize the lists of
manglers for each type. The file is setup to process command line
arguments in the same way as the 'cl-bindgen` executable, so no other editing is
needed in most cases.

To see the full documentation for the library, see ./doc/index.
