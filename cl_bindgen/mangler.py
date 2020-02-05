""" Classes to transform C names into lisp symbol names

Each mangler class provides one or more tranformations to a symbol. For example, the
`UnderscoreMangler` converts underscores (`_`) into dashes
(`-`). A series of manglers are applied to each C name to translate it
into an lisp symbol.

Each mangler class follows the following interface:
+ can_mangle(string): returns true if the entity knows how to mangle the string
+ mangle(string): returns a new string with the tranformations applied
"""

import re

class PrefixMangler:
    """ Mangler to replace the prefix of a string wtih a given string."""

    def __init__(self, prefix, replace):
        self.prefix = prefix
        self.replace = replace
        pass

    def can_mangle(self, string):
        # does the string have a prefix?
        return string.startswith(self.prefix)

    def mangle(self, string):
        return string.replace(self.prefix, self.replace, 1)

class KeywordMangler:
    """Mangler to transform the given string into a keyword

    Doesn't transform symbols that have a package prefix.
    """

    def __init(self):
        pass

    def can_mangle(self, string):
        # if there is already a colon in the name, then
        # common lisp won't accept it, so don't do anything:
        return not ':' in string

    def mangle(self, string):
        return ':' + string

class ConstantMangler:
    """Transform a string into a symbol for a constant variable

    Adds the "+" character around the symbol name, and correctly handles package prefixes
    """

    def __init__(self):
        pass

    def can_mangle(self, string):
        return True

    def mangle(self, string):
        if ':' in string:
            # Remove any possible package prefix and save it:
            (pkg_prefix, colon, symb) = string.rpartition(':')
            return pkg_prefix + ':+' + symb + '+'
        else:
            return "+" + string + "+"

class UnderscoreMangler:
    """ Converts underscores to dashes"""

    def __init(self):
        pass

    def can_mangle(self, string):
        return '_' in string

    def mangle(self, string):
        return string.replace('_', '-')

class RegexSubMangler:
    """ Substitutes the substring matched by the regex with another string

    Uses re.sub to perform the subistituion.
    """

    def __init__(self, regex, replace):
        self.regex = regex
        self.replace = replace

    def can_mangle(self, string):
        # does the string have a prefix?
        return re.search(self.regex, string)

    def mangle(self, string):
        return re.sub(self.regex, self.replace, string)
