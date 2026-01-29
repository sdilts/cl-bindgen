import re

def _extract_match_option(rules: dict, list_arg: str):
    match_obj = rules.get(list_arg)
    if match_obj:
        if type(match_obj) is list:
            return match_obj
        else:
            return [ match_obj ]
    return None

def process_pointer_expansion_rules(options: dict, list_arg='names'):
    include_rules = options.get('include')
    if include_rules is not None:
        inc_regex = _extract_match_option(include_rules, 'match')
        inc_list = include_rules.get(list_arg, [])
    else:
        inc_regex = None
        inc_list = []

    exclude_rules = options.get('exclude')
    if exclude_rules is not None:
        ex_regex = _extract_match_option(exclude_rules, 'match')
        ex_list = exclude_rules.get(list_arg, [])
    else:
        ex_list = []
        ex_regex = None
    return make_batch_determiner(whitelist=inc_list, blacklist=ex_list,
                                 include_matcher=inc_regex, exclude_matcher=ex_regex)

def _match_regex_list(regex_list, name):
    for r in regex_list:
        if r.search(name):
            return True
    return False

def _compile_regexes(regexes):
    return [re.compile(m) for m in regexes]

def make_batch_determiner(whitelist=None, blacklist=None, include_matcher=None, exclude_matcher=None):
    has_whitelist = whitelist or include_matcher is not None
    has_blacklist = blacklist or exclude_matcher is not None

    white_set = set(whitelist)
    black_set = set(blacklist)

    if has_blacklist and not has_whitelist:
        # import everything but the blacklist
        if exclude_matcher:
            excluder = _compile_regexes(exclude_matcher)
            return lambda typename: typename not in black_set and not _match_regex_list(excluder, typename)
        else:
            return lambda typename: typename not in black_set
    elif has_whitelist and not blacklist:
        # only import the whitelist
        if include_matcher:
            includer = _compile_regexes(include_matcher)
            return lambda typename: typename in white_set or _match_regex_list(includer, typename)
        else:
            return lambda x: x in white_set
    elif has_whitelist and has_blacklist:
        # import everything on whitelist, excluding blacklist
        allowed_set = white_set.difference(black_set)
        if exclude_matcher and include_matcher:
            excluder = _compile_regexes(exclude_matcher)
            includer = _compile_regexes(include_matcher)
            def fn(typename):
                in_white = (typename in allowed_set or _match_regex_list(includer, typename))
                not_black = (not _match_regex_list(excluder, typename))
                return in_white and not_black
            return fn
        elif exclude_matcher is not None:
            excluder = _compile_regexes(exclude_matcher)
            return lambda x: x in allowed_set and not _match_regex_list(excluder, x)
        elif include_matcher:
            includer = _compile_regexes(include_matcher)
            return lambda x: x in allowed_set or _match_regex_list(includer, x)
        else:
            return lambda x: x in allowed_set
    else:
        # import everything
        return lambda x: True
