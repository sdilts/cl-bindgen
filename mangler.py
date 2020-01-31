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

class UnderscoreMangler:

    def __init(self):
        pass

    def can_mangle(self, string):
        return True

    def mangle(self, string):
        return string
