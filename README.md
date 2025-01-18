# cl-bindgen

A command line tool and library for creating Common Lisp language bindings
from C header files.

Features:
+ Generates CFFI bindings for function declarations, enums, variables, unions,
  and structures.
+ Handles nested and anonymous structures, unions, and enums.
+ Warns when it cannot produce a correct binding.
+ Documentation comments from the C source files are lispified and
  included with the generated bindings when available.
+ Provides a powerful way to customize how names are translated into
  lisp symbols.

## Installation
cl-bindgen requires `libclang`, which is not installed with the other Python
dependencies and not available on PyPi. It is recommended to install it first before installing
cl-bindgen. Use your distribution's package manager to install it.

Once `libclang` is installed, you can then install `cl-bindgen` from
source or from PyPI.

From PyPI:
``` bash
pip install cl-bindgen
```
From source:
``` bash
git clone --depth=1 https://github.com/sdilts/cl-bindgen
cd cl-bindgen
pip install --user .
```
## Processing individual files
To process individual files, use the `f` command and specify one or
more files to process. By default, output will be printed to
stdout, but the output file can be specified with the `-o` option. To see
a full list of options, run `cl-bindgen f -h`.

``` bash
# Process test.h and print the results to stdout:
cl-bindgen f test.h
# Process the files test1.h, test2.h, and place the output in output.lisp:
cl-bindgen f -o output.lisp test1.h test2.h
```

## Batch file processing
cl-bindgen can use a yaml file to process many header
files with a single invocation. Use the `b` command
to specify one or more batch files to process:

``` bash
cl-bindgen b my_library.yaml
```

### Batch file format
Batch files use the YAML format. Multiple documents can be contained in each input file.

Required Fields:
+ `output` : where to place the generated code
+ `files` : a list of files to process

Optional Fields:
+ `package` : The name of the Common Lisp package of the generated file
+ `arguments` : Arguments to pass to clang
+ `force` : Ignore errors while parsing. Valid values are `True` or `False`
+ `pkg-config`: A list of package names needed by the library. Adds
  the flags needed to compile the given header files as told by
  `pkg-config --cflags`
+ `pointer_expansion` (experimental): Used to provide either a regex
	or a list of pointer types to expand or not expand in the output.


To see example batch files, look in the
[examples](https://github.com/sdilts/cl-bindgen/tree/master/examples)
directory.

## Handling Include Directories and Clang Arguments

If you need to specify additional command line arguments to the clang
processor, you can use the `-a` option, and list any clang arguments after.

``` bash
cl-bindgen b batch_file.yaml -a -I include_dir1 -I include_dir2
# Use -- to stop collecting clang arguments:
# Note that instead of directly calling pkg-config when using a batch
# file, you can use the pkg-config option instead.
cl-bindgen f -a `pkg-config --cflags mylibrary` -- header.h
```

If a header file isn't found while processing the input files,
cl-bindgen will halt and produce no output. This is to avoid producing
incorrect bindings: while bindings can still be produced when header
files are missing, they are likely to be incorrect. To ignore missing
header files and other fatal errors, the `-f` flag can be used:

``` bash
cl-bindgen b -f batch_file.yaml
cl-bindgen f -f header.c
```

## Customizing the behavior of cl-bindgen
cl-bindgen attempts to provide a reasonable interface that is usable
in most cases. However, if you need to customize how C names are
converted into lisp names or embed cl-bindgen into another
application, cl-bindgen is available as a library.

The `cl_bindgen` package is broken up into modules: the `processfile`,
`mangler`, `util` and `macro_util` modules. The `processfile` module provides the
functions to generate the lisp bindings, the `mangler` module provides
functions to convert C names into lisp names, and the `util` module
provides functions to use batch files and cl-bingen's command line
interface.

### The `processfile` Module

This module exports two functions: `process_file` and `process_files`,
which work on a single header file or many, respectively. Both
functions take two arguments: the file(s) to be processed and an
`ProcessOptions` object.

The `ProcessOptions`class is the way to specify how the
processing functions generate their output. It has the following
fields:

+ `typedef_mangers`, `enum_manglers`, `type_manglers`, `name_manglers`
  and `constant_manglers` : See the [mangler module section](#the-mangler-module)
  for what these do.
+ `output` : The path of the file where the output is
  placed. `":stdout"` or `":stderr"` can be specified to use standard
  out or standard error.
+ `package` : If not `None`, this specifies the package the the
  generated output should be placed in.
+ `arguments` : The command line arguments that should be given to the
  clang processor.
+ `force` : If true, then ignore errors while parsing the input files.
+ `macro_detector`: The [macro detctor function](#the-macro_util-module)
  used to detect header macros
+ `expand_pointer_p`: A function that takes a typename and returns
  whether or not pointers of this type should be fully expanded or
  left as `:pointer`.

### The `mangler` Module

cl-bindgen uses a set of classes called manglers to translate C
names so that they follow lisp naming conventions. Each mangler class
provides one or more transformations to a symbol. For example, the
`UnderscoreMangler` class converts underscores (`_`) into dashes
(`-`). A series of manglers are applied to each C name to make it
follow lisp naming conventions.

To maximize customization, a list of manglers is associated with each
type of name that can be converted. enums, variable names, typedefs,
constants, and record types all use a different set of manglers.

Built-in manglers:
+ `UnderscoreMangler` : Converts underscores to dashes.
+ `ConstantMangler` : Converts a string to follow Common Lisp's constant style
  recomendation.
+ `KeywordMangler` : Adds a `:` to the beginning of a string to make it a symbol.
   Doesn't perform any action if the string has a package prefix.
+ `RegexSubMangler` : Substitutes the substring matched by a regex with the given string.

#### Mangler Interface

Mangler classes follow a simple interface:
+ `can_mangle(string)`: returns true if the mangler can perform its
  operations on the given string
+ `mangle(string)`: returns a string with the desired transformations
  applied.

### The `util` Module

The `util` module provides two functions: `process_batch_file` and
`dispatch_from_arguments`.

+ `process_batch_file(batch_file, options)` : Processes the given
  batch file using `options` as the default options.
+ `dispatch_from_arguments(arguments, options)` : Uses the provided
  command line arguments to perform the actions of cl-bindgen using
  `options` as the default options.
+ `find_clang_resource_dir()` : This is needed if you build your own
  `ProcessOptions` object and do not use the `dispatch_from_arguments`
  function. The path returned by this function needs to be appended
  to the clang arguments in order for the script to find built-in
  headers. See the `add_clang_dir` function in this module.

### The `macro_util` Module

This module provides the `macro_matches_file_path` function that is used
by default to check if a macro is a header guard, and the
`convert_literal_token` that converts literal tokens into CL literals.

The `macro_matches_file_path` is a macro detector function. Macro
detector functions are used to determine if a C macro is a header
guard. They take two arguments: the location of the file and the name
of the file as a string.

### Examples

The best example of how to use cl-bindgen as a library is to look at its main
function found in
[cl\_bindgen/\_\_main\_\_.py](https://github.com/sdilts/cl-bindgen/blob/master/cl_bindgen/__main__.py).
In it, cl-bindgen's default options are set, then passed to `dispatch_from_arguments`
to run the utility.
