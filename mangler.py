import re

class PrefixMangler:

    def __init__(self, prefix):
        self.prefix = prefix
        pass

    def can_mangle(self, string):
        # does the string have a prefix?
        return True

    def mangle(self, string):
        return string

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
