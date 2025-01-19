import re

def process_pointer_expansion_rules(options: dict):
    include_rules = options.get('include')
    if include_rules is not None:
        match_obj = include_rules.get('match')
        inc_regex = match_obj if type(match_obj) is list else [ match_obj ]
        inc_list = include_rules.get('types', [])
    else:
        inc_regex = None
        inc_list = []

    exclude_rules = options.get('exclude')
    if exclude_rules is not None:
        match_obj = exclude_rules.get('match')
        ex_regex = match_obj if type(match_obj) is list else [ match_obj ]
        ex_list = exclude_rules.get('types', [])
    else:
        ex_list = []
        ex_regex = None
    return make_batch_determiner(whitelist=inc_list, blacklist=ex_list,
                                 include_matcher=inc_regex, exclude_matcher=ex_regex)

def _match_regex_list(regex_list, name):
    for r in regex_list:
        if r.search(name):
            return True;
    return False;

def _compile_regexes(regexes):
    return [re.compile(m) for m in regexes]

def make_batch_determiner(whitelist=None, blacklist=None, include_matcher=None, exclude_matcher=None):
    has_whitelist = whitelist is not None or include_matcher is not None
    has_blacklist = blacklist is not None or exclude_matcher is not None

    white_set = set(whitelist)
    black_set = set(blacklist)

    if has_blacklist and not has_whitelist:
        # import everything but the blacklist
        if exclude_matcher:
            excluder = _compile_regexes(exclude_matcher)
            return lambda typename: typename not in black_set and not match_regex_list(excluder, typename)
        else:
            return lambda typename: typename not in black_set
    elif has_whitelist and not blacklist:
        # only import the whitelist
        if include_matcher:
            includer = _compile_regexes(include_matcher)
            return lambda typename: typename in white_set or match_regex_list(includer, typename)
        else:
            return lambda x: x in white_set
    elif has_whitelist and has_blacklist:
        # import everything on whitelist, excluding blacklist
        if exclude_matcher and include_matcher:
            excluder = _compile_regexes(exclude_matcher)
            includer = _compile_regexes(include_matcher)
            def fn(typename):
                in_white = (typename in white_set or match_regex_list(includer, typename))
                not_black = (typename not in black_set and not match_regex_list(excluder, typename))
                return in_white and not_black
        elif exclude_matcher is not None:
            excluder = _compile_regexes(exclude_matcher)
            return lambda x: x in white_set and not match_regex_list(excluder, x) and x not in black_set
        elif include_matcher:
            includer = _compile_regexes(include_matcher)
            return lambda x: (x in  white_set or match_regex_list(includer, x)) and x not in black_set
        else:
            return lambda x: typename in white_set and typename not in black_set
    else:
        # import everything
        return lambda x: True
