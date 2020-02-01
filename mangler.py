import re

class PrefixMangler:

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

    def __init(self):
        pass

    def can_mangle(self, string):
        # if there is already a colon in the name, then
        # common lisp won't accept it, so don't do anything:
        return not ':' in string

    def mangle(self, string):
        return ':' + string

class UnderscoreMangler:

    def __init(self):
        pass

    def can_mangle(self, string):
        return '_' in string

    def mangle(self, string):
        return string.replace('_', '-')

class RegexSubMangler:

    def __init__(self, regex, replace):
        self.regex = regex
        self.replace = replace

    def can_mangle(self, string):
        # does the string have a prefix?
        return re.search(self.regex, string)

    def mangle(self, string):
        return re.sub(self.regex, self.replace, string)
