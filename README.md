# CL-bindgen

A command line tool and library for creating Common Lisp language bindings
from C header files

Features:
+ Generates CFFI bindgings for function declarations, enums, variables, unions,
  and structures.
+ Handles nested and anonymous structures, unions, and enums.
+ Warns when it cannot produce a correct binding
+ Documentation comments from the C source files are lispified and
  included with the generated bindings when available.
+ Provides a powerful way to customize how names are translated into
  lisp symbols.

## Installation
CL-bindgen requires `libclang`, which usually isn't installed beside the other Python
dependencies when installing with pip. It is recommended to install it
first before installing cl-bindgen. Use your favorite package mangager to install it.

From pip:
``` bash
pip install --user cl-bindgen
```
From source:
``` bash
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
CL-bindgen can use a yaml file to process many header
files with a single invocation. Use the `b` command
to specify one or more batch files to process:

``` bash
cl-bindgen b my_library.yaml
```

### Batch file format
Batch files use the YAML format. Mutliple documents can be contained in each input file.

Required Fields:
+ `output` : where to place the generated code
+ `files` : a list of files to process

Optional Fields:
+ `package` : The name of the Common Lisp package of the generated file
+ `arguments` : Arguments to pass to clang

To see example batch files, look in the 
[examples](https://github.com/sdilts/cl-bindgen/tree/master/examples)
directory.

## Customizing the behavior of cl-bindgen
cl-bindgen attempts to provide a reasonable interface that is usable
in most cases. However, if you need to customize how C names are
converted into lisp names or embed cl-bindgen into another
application, cl-bindgen is available as a library.

The cl-bindgen is broken up into three modules: the `processfile`,
`mangler` and `util` modules. The `processfile` module provides the
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

### The `mangler` Module

CL-bindgen uses a set of classes called manglers to translate C
names so that they follow lisp naming conventions. Each mangler class
provides one or more tranformations to a symbol. For example, the
`UnderscoreMangler` converts underscores (`_`) into dashes
(`-`). A series of manglers are applied to each C name to make it
follow lisp naming conventions.

To maximize customization, a list of manglers is associated with each
type of name that can be converted. Enums, variable names, typedefs,
constants, and record types all use a different set of manglers.

Built-in manglers:
+ `UnderscoreMangler` : Converts underscores to dashes.
+ `ConstantMangler` : Converts a string to follow Common Lisp's constant style
  recomendation.
+ `KeywordMangler` : Adds a `:` to the begining of a string to make it a symbol.
   Doesn't perfom any action if the string has a package prefix.
+ `RegexSubMangler` : Substitutes the substring matched by a regex with the given string.

#### Mangler Interface

Mangler classes follow a simple interface:
+ `can_mangle(string)`: returns true if the mangler can perform its
  operations on the given string
+ `mangle(string)`: returns a string with the desired tranformations
  applied.

### The `util` Module

The `util` module provides two functions: `process_batch_file` and
`dispatch_from_arguments`.

+ `process_batch_file(batch_file, options)` : Processes the given
  batch file using `options` as the default options.
+ `dispatch_from_arguments(arguments, options)` : Uses the provided
  command line arguments to perform the actions of cl-bindgen using
  `options` as the default options.

### Examples

The best example of how to use cl-bindgen as a library is to look at its main
function found in [cl\_bindgen/\_\_main\_\_.py](https://github.com/sdilts/cl-bindgen/blob/master/cl_bindgen/__main__.py). In it, cl-bindgen's
default options are set, then passed to `dispatch_from_arguments` to
run the utility.
