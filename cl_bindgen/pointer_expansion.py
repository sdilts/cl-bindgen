import re

def process_pointer_expansion_rules(options: dict):
    include_rules = options.get('include')
    if include_rules is not None:
        inc_regex = include_rules.get('match')
        inc_list = include_rules.get('types', [])
    else:
        inc_regex = None
        inc_list = []

    exclude_rules = options.get('exclude')
    if exclude_rules is not None:
        ex_regex = exclude_rules.get('match')
        ex_list = exclude_rules.get('types', [])
    else:
        ex_list = []
        ex_regex = None
    return make_batch_determiner(whitelist=inc_list, blacklist=ex_list,
                                 include_matcher=inc_regex, exclude_matcher=ex_regex)

def make_batch_determiner(whitelist=None, blacklist=None, include_matcher=None, exclude_matcher=None):
    has_whitelist = whitelist is not None or include_matcher is not None
    has_blacklist = blacklist is not None or exclude_matcher is not None

    white_set = set(whitelist)
    black_set = set(blacklist)

    if has_blacklist and not has_whitelist:
        # import everything but the blacklist
        if exclude_matcher:
            excluder = re.compile(exclude_matcher)
            return lambda typename: typename not in black_set and not excluder.search(typename)
        else:
            return lambda typename: typename not in black_set
    elif has_whitelist and not blacklist:
        # only import the whitelist
        if include_matcher:
            includer = re.compile(include_matcher)
            return lambda typename: typename in white_set or includer.search(typename)
        else:
            return lambda x: x in white_set
    elif has_whitelist and has_blacklist:
        # import everything on whitelist, excluding blacklist
        if exclude_matcher and include_matcher:
            excluder = re.compile(exclude_matcher)
            includer = re.compile(include_matcher)
            def fn(typename):
                in_white = (typename in white_set or includer.search(typename))
                not_black = (typename not in black_set and not excluder.search(typename))
                return in_white and not_black
        elif exclude_matcher is not None:
            excluder = re.compile(exclude_matcher)
            return lambda x: x in white_set and not excluder.search(x) and x not in black_set
        elif include_matcher:
            includer = re.compile(include_matcher)
            return lambda x: (x in  white_set or includer.search(x)) and x not in black_set
        else:
            return lambda x: typename in white_set and typename not in black_set
    else:
        # import everything
        return lambda x: True
